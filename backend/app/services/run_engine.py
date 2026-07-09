"""Orchestrates a single run: generate a script, dispatch through the channel adapter for the
workflow template's channel, log every message/tool-call, update run state. This is the "agent
harness" core of the app — the piece the target postings (Viktor, Duvo, Huzzle) describe."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.message import Message
from app.models.run import Run
from app.models.tool_call import ToolCall
from app.models.workflow_template import WorkflowTemplate
from app.services.channel_adapters.base import ChannelAdapter
from app.services.channel_adapters.email_adapter import EmailAdapter
from app.services.channel_adapters.simulated_adapter import SimulatedSmsAdapter, SimulatedVoiceAdapter
from app.services.cost_tracker import record_llm_call
from app.services.llm_client import LLMProvider, LLMProviderUnavailableError
from app.services.parsing import ParsingFailedError
from app.services.script_generator import generate_script

_ADAPTERS: dict[str, type[ChannelAdapter]] = {
    "email": EmailAdapter,
    "voice_simulated": SimulatedVoiceAdapter,
    "sms_simulated": SimulatedSmsAdapter,
}


def get_adapter(channel: str) -> ChannelAdapter:
    adapter_cls = _ADAPTERS.get(channel)
    if adapter_cls is None:
        raise ValueError(f"Unknown channel '{channel}'")
    return adapter_cls()


def execute_run(db: Session, llm: LLMProvider, run: Run, contact: Contact, template: WorkflowTemplate) -> Run:
    run.state = "running"
    run.started_at = datetime.now(timezone.utc)
    db.commit()

    started = time.perf_counter()

    try:
        script_result = generate_script(
            llm, goal_prompt=template.goal_prompt, contact_name=contact.name, channel=template.channel
        )
    except (ParsingFailedError, LLMProviderUnavailableError) as exc:
        usage = getattr(exc, "usage", None)
        if usage is not None:
            record_llm_call(
                db, purpose="script_generation", provider=llm.provider_name, model=llm.model,
                usage=usage, attempts=getattr(exc, "attempts", 1),
                latency_ms=(time.perf_counter() - started) * 1000, success=False, error=str(exc),
            )
        run.state = "failed"
        run.error_reason = f"script generation failed: {exc}"
        run.completed_at = datetime.now(timezone.utc)
        run.latency_ms = (time.perf_counter() - started) * 1000
        db.commit()
        return run

    record_llm_call(
        db, purpose="script_generation", provider=llm.provider_name, model=llm.model,
        usage=script_result.usage, attempts=script_result.attempts,
        latency_ms=(time.perf_counter() - started) * 1000, success=True,
    )

    script = script_result.value.script
    db.add(Message(run_id=run.id, direction="outbound", provider=template.channel, content=script))

    adapter = get_adapter(template.channel)
    result = adapter.send(
        contact_name=contact.name, contact_email=contact.email, contact_phone=contact.phone, script=script
    )

    if result.response_content:
        db.add(Message(run_id=run.id, direction="inbound", provider=result.provider, content=result.response_content))

    db.add(
        ToolCall(
            run_id=run.id,
            tool_name=f"channel.{result.provider}",
            input={"contact_name": contact.name, "script": script},
            output={"outcome": result.outcome, "response": result.response_content, "error": result.error},
            success=result.success,
        )
    )

    run.state = "completed" if result.success else "failed"
    run.outcome = result.outcome
    run.error_reason = result.error
    run.completed_at = datetime.now(timezone.utc)
    run.latency_ms = (time.perf_counter() - started) * 1000
    db.commit()
    db.refresh(run)
    return run
