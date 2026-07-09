"""Two-layer evaluation, same philosophy as ai-recruitment-copilot's eval harness: cheap
deterministic checks first, LLM-as-judge for the nuance a rule can't capture."""

from __future__ import annotations

from app.models.message import Message
from app.models.run import Run
from app.models.workflow_template import WorkflowTemplate
from app.schemas.evaluation import EvalJudgeParsed
from app.services.llm_client import LLMProvider
from app.services.parsing import ParsedResult, parse_structured

MAX_REASONABLE_LATENCY_MS = 60_000

JUDGE_SYSTEM_PROMPT = (
    "You are grading whether an AI-run outreach attempt achieved its goal. Given the workflow's "
    "rubric and the run's transcript, respond with ONLY a single JSON object with keys: "
    "llm_score (0-100), passed (boolean), failure_tags (list of short strings describing what "
    "went wrong, empty if none), notes (1-2 sentences explaining the score)."
)


def rule_check(run: Run, messages: list[Message]) -> tuple[float, list[str]]:
    checks = []
    tags = []

    completed = run.state == "completed"
    checks.append(completed)
    if not completed:
        tags.append("run_not_completed")

    has_outbound = any(m.direction == "outbound" for m in messages)
    checks.append(has_outbound)
    if not has_outbound:
        tags.append("no_outbound_message")

    latency_ok = run.latency_ms is None or run.latency_ms < MAX_REASONABLE_LATENCY_MS
    checks.append(latency_ok)
    if not latency_ok:
        tags.append("latency_exceeded_threshold")

    score = sum(checks) / len(checks)
    return score, tags


def llm_judge(llm: LLMProvider, *, template: WorkflowTemplate, messages: list[Message]) -> ParsedResult:
    transcript = "\n".join(f"[{m.direction}] {m.content}" for m in messages) or "(no messages)"
    user_prompt = f"Rubric: {template.eval_rubric}\n\nTranscript:\n{transcript}"
    result = parse_structured(llm, JUDGE_SYSTEM_PROMPT, user_prompt, EvalJudgeParsed)
    assert isinstance(result.value, EvalJudgeParsed)
    return result
