"""Shared LLM-backed structured parsing with a repair-retry loop.

Free-tier OpenRouter models are less reliable at strict JSON output than
GPT-4/Claude. Rather than hoping for the best, we validate against the
Pydantic schema and, on failure, send the error back to the model asking it
to fix its own output. This is a deliberate, documented tradeoff — see
docs/architecture.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ValidationError

from app.services.llm_client import LLMProvider, LLMUsage, try_parse_json

MAX_ATTEMPTS = 3


class ParsingFailedError(Exception):
    def __init__(self, attempts: int, last_error: str, usage: LLMUsage | None = None):
        self.attempts = attempts
        self.last_error = last_error
        self.usage = usage or LLMUsage()
        super().__init__(f"Failed to get valid structured output after {attempts} attempts: {last_error}")


@dataclass
class ParsedResult:
    value: BaseModel
    usage: LLMUsage
    attempts: int


def parse_structured(
    llm: LLMProvider,
    system_prompt: str,
    user_prompt: str,
    schema: type[BaseModel],
) -> ParsedResult:
    """Call the LLM and coerce its output into `schema`, retrying with the
    validation error fed back to the model if it produces malformed JSON.
    Aggregates token usage across all attempts for cost tracking."""

    current_user_prompt = user_prompt
    last_error = "no attempts made"
    total_usage = LLMUsage()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        result = llm.complete(system_prompt, current_user_prompt)
        total_usage.prompt_tokens += result.usage.prompt_tokens
        total_usage.completion_tokens += result.usage.completion_tokens
        parsed_json = try_parse_json(result.content)

        if parsed_json is None:
            last_error = "response was not valid JSON"
        else:
            try:
                value = schema.model_validate(parsed_json)
                return ParsedResult(value=value, usage=total_usage, attempts=attempt)
            except ValidationError as exc:
                last_error = str(exc)

        current_user_prompt = (
            f"{user_prompt}\n\n"
            f"Your previous response was invalid: {last_error}\n"
            f"Respond with ONLY a single valid JSON object matching the required fields. "
            f"No prose, no markdown code fences."
        )

    raise ParsingFailedError(attempts=MAX_ATTEMPTS, last_error=last_error, usage=total_usage)
