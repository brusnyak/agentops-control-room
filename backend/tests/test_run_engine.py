import json

from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.message import Message
from app.models.run import Run
from app.models.tool_call import ToolCall
from app.models.workflow_template import WorkflowTemplate
from app.services.llm_client import MockLLMProvider
from app.services.run_engine import execute_run

VALID_SCRIPT_JSON = json.dumps({"script": "Hi Jane, checking in on your appointment."})


def _setup(db_session, channel="voice_simulated"):
    template = WorkflowTemplate(name="t", channel=channel, goal_prompt="book appt", eval_rubric="be clear")
    db_session.add(template)
    db_session.flush()
    campaign = Campaign(workflow_template_id=template.id, name="c", status="active")
    contact = Contact(name="Jane Doe", email="jane@example.com", phone="+1555")
    db_session.add_all([campaign, contact])
    db_session.flush()
    run = Run(campaign_id=campaign.id, contact_id=contact.id, channel=channel, state="pending")
    db_session.add(run)
    db_session.commit()
    db_session.refresh(run)
    return template, campaign, contact, run


def test_execute_run_simulated_channel_completes(db_session):
    template, campaign, contact, run = _setup(db_session, channel="voice_simulated")
    llm = MockLLMProvider(responses=[VALID_SCRIPT_JSON])

    result = execute_run(db_session, llm, run, contact, template)

    assert result.state in ("completed", "failed")  # simulated adapter always "succeeds" -> completed
    assert result.state == "completed"
    assert result.outcome is not None
    assert result.latency_ms is not None

    messages = db_session.query(Message).filter(Message.run_id == run.id).all()
    assert any(m.direction == "outbound" for m in messages)
    assert any(m.direction == "inbound" for m in messages)

    tool_calls = db_session.query(ToolCall).filter(ToolCall.run_id == run.id).all()
    assert len(tool_calls) == 1
    assert tool_calls[0].tool_name == "channel.simulated_voice"


def test_execute_run_email_channel_fails_without_api_key(db_session, monkeypatch):
    monkeypatch.setattr("app.services.channel_adapters.email_adapter.settings.resend_api_key", "")
    template, campaign, contact, run = _setup(db_session, channel="email")
    llm = MockLLMProvider(responses=[VALID_SCRIPT_JSON])

    result = execute_run(db_session, llm, run, contact, template)

    assert result.state == "failed"
    assert result.error_reason is not None


def test_execute_run_records_script_generation_failure(db_session):
    template, campaign, contact, run = _setup(db_session, channel="voice_simulated")
    llm = MockLLMProvider(responses=["garbage", "garbage", "garbage"])

    result = execute_run(db_session, llm, run, contact, template)

    assert result.state == "failed"
    assert "script generation failed" in result.error_reason
