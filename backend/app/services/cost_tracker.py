"""Lightweight LLM observability — records every call so cost/latency/error
rate are queryable, without depending on a paid tracing SaaS (LangSmith etc.)
All current models are OpenRouter free-tier, so cost is genuinely $0 today;
this is the hook point for a pricing table once/if a paid model is added."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.llm_call_log import LLMCallLog
from app.services.llm_client import LLMUsage


def record_llm_call(
    db: Session,
    *,
    purpose: str,
    provider: str,
    model: str,
    usage: LLMUsage,
    attempts: int,
    latency_ms: float,
    success: bool,
    error: str | None = None,
) -> LLMCallLog:
    log = LLMCallLog(
        purpose=purpose,
        provider=provider,
        model=model,
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        attempts=attempts,
        latency_ms=latency_ms,
        success=success,
        error=error,
    )
    db.add(log)
    return log


def get_observability_stats(db: Session) -> dict:
    total_calls = db.query(func.count(LLMCallLog.id)).scalar() or 0
    if total_calls == 0:
        return {
            "total_calls": 0,
            "success_rate": None,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "avg_latency_ms": None,
            "avg_attempts": None,
            "by_purpose": {},
        }

    success_count = db.query(func.count(LLMCallLog.id)).filter(LLMCallLog.success.is_(True)).scalar() or 0
    total_prompt = db.query(func.coalesce(func.sum(LLMCallLog.prompt_tokens), 0)).scalar()
    total_completion = db.query(func.coalesce(func.sum(LLMCallLog.completion_tokens), 0)).scalar()
    avg_latency = db.query(func.avg(LLMCallLog.latency_ms)).scalar()
    avg_attempts = db.query(func.avg(LLMCallLog.attempts)).scalar()

    by_purpose_rows = (
        db.query(LLMCallLog.purpose, func.count(LLMCallLog.id)).group_by(LLMCallLog.purpose).all()
    )

    return {
        "total_calls": total_calls,
        "success_rate": round(success_count / total_calls, 4),
        "total_prompt_tokens": int(total_prompt),
        "total_completion_tokens": int(total_completion),
        "avg_latency_ms": round(float(avg_latency), 1) if avg_latency is not None else None,
        "avg_attempts": round(float(avg_attempts), 2) if avg_attempts is not None else None,
        "by_purpose": {purpose: count for purpose, count in by_purpose_rows},
    }
