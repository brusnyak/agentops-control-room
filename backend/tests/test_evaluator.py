import json
from datetime import datetime, timezone

from app.models.message import Message
from app.models.run import Run
from app.models.workflow_template import WorkflowTemplate
from app.services.evaluator import llm_judge, rule_check
from app.services.llm_client import MockLLMProvider

VALID_JUDGE_JSON = json.dumps(
    {"llm_score": 85, "passed": True, "failure_tags": [], "notes": "Clear and on-goal."}
)


def _run(state="completed", latency_ms=1000.0) -> Run:
    return Run(
        id="00000000-0000-0000-0000-000000000001", campaign_id="00000000-0000-0000-0000-000000000002",
        contact_id="00000000-0000-0000-0000-000000000003", channel="email", state=state,
        latency_ms=latency_ms, created_at=datetime.now(timezone.utc),
    )


def test_rule_check_all_pass():
    run = _run()
    messages = [Message(direction="outbound", provider="email", content="hi")]

    score, tags = rule_check(run, messages)

    assert score == 1.0
    assert tags == []


def test_rule_check_flags_incomplete_run():
    run = _run(state="failed")
    messages = [Message(direction="outbound", provider="email", content="hi")]

    score, tags = rule_check(run, messages)

    assert score < 1.0
    assert "run_not_completed" in tags


def test_rule_check_flags_no_outbound_message():
    run = _run()
    score, tags = rule_check(run, [])

    assert score < 1.0
    assert "no_outbound_message" in tags


def test_rule_check_flags_excessive_latency():
    run = _run(latency_ms=999_999)
    messages = [Message(direction="outbound", provider="email", content="hi")]

    score, tags = rule_check(run, messages)

    assert score < 1.0
    assert "latency_exceeded_threshold" in tags


def test_llm_judge_valid_response():
    llm = MockLLMProvider(responses=[VALID_JUDGE_JSON])
    template = WorkflowTemplate(name="t", channel="email", goal_prompt="g", eval_rubric="Pass if clear")
    messages = [Message(direction="outbound", provider="email", content="hi")]

    result = llm_judge(llm, template=template, messages=messages)

    assert result.value.llm_score == 85
    assert result.value.passed is True
