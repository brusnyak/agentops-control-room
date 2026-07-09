"""LLM provider abstraction.

Real calls go through OpenRouter (free-tier models). Tests use MockLLMProvider
so the suite is deterministic, offline, and free — no network flakiness tied
to a shared free-tier rate limit.
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import httpx

from app.config import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
RETRYABLE_STATUS_CODES = {429, 502, 503, 504}
MAX_TRANSPORT_RETRIES = 3
MAX_RETRY_WAIT_SECONDS = 20


class LLMProviderUnavailableError(Exception):
    """Upstream model is rate-limited or down after retries. Caller should
    surface this as a 503, not a 500 — it's not our bug, it's a free-tier
    reliability tradeoff we've documented and accepted."""


@dataclass
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class LLMResult:
    content: str
    usage: LLMUsage = field(default_factory=LLMUsage)


class LLMProvider(ABC):
    provider_name: str = "unknown"
    model: str = "unknown"

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> LLMResult:
        ...


class OpenRouterProvider(LLMProvider):
    provider_name = "openrouter"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.model = model or settings.llm_model

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResult:
        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Add it to ~/.secrets/acore.env and "
                "run scripts/setup-env.sh."
            )

        last_error: httpx.HTTPStatusError | None = None
        for attempt in range(1, MAX_TRANSPORT_RETRIES + 1):
            response = httpx.post(
                OPENROUTER_URL,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.1,
                },
                timeout=60,
            )
            if response.status_code not in RETRYABLE_STATUS_CODES:
                break
            last_error = httpx.HTTPStatusError(
                f"{response.status_code} from OpenRouter", request=response.request, response=response
            )
            if attempt == MAX_TRANSPORT_RETRIES:
                break
            wait = min(float(response.headers.get("Retry-After", 2 * attempt)), MAX_RETRY_WAIT_SECONDS)
            time.sleep(wait)
        else:
            response = None  # unreachable, loop always breaks or returns

        if response.status_code in RETRYABLE_STATUS_CODES:
            raise LLMProviderUnavailableError(
                f"OpenRouter model '{self.model}' unavailable after {MAX_TRANSPORT_RETRIES} attempts: {last_error}"
            )

        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return LLMResult(
            content=content,
            usage=LLMUsage(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
            ),
        )


class MockLLMProvider(LLMProvider):
    """Test double. Pass a queue of canned responses (str) or a callable."""

    provider_name = "mock"
    model = "mock-model"

    def __init__(self, responses: list[str] | None = None):
        self.responses = list(responses or [])
        self.calls: list[tuple[str, str]] = []

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResult:
        self.calls.append((system_prompt, user_prompt))
        if not self.responses:
            raise AssertionError("MockLLMProvider ran out of canned responses")
        content = self.responses.pop(0)
        return LLMResult(content=content, usage=LLMUsage(prompt_tokens=10, completion_tokens=10))


def get_llm_provider() -> LLMProvider:
    if settings.testing:
        return MockLLMProvider(responses=["{}"])
    return OpenRouterProvider()


def try_parse_json(text: str) -> dict | None:
    """LLMs sometimes wrap JSON in prose or code fences. Best-effort extraction."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
