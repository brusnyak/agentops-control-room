import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.campaign import Campaign
from app.models.run import Run

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{campaign_id}")
def campaign_dashboard(campaign_id: uuid.UUID, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    runs = db.query(Run).filter(Run.campaign_id == campaign_id).all()
    total = len(runs)

    outcome_counts: dict[str, int] = {}
    failure_reasons: dict[str, int] = {}
    latencies = []

    for run in runs:
        if run.outcome:
            outcome_counts[run.outcome] = outcome_counts.get(run.outcome, 0) + 1
        if run.error_reason:
            failure_reasons[run.error_reason] = failure_reasons.get(run.error_reason, 0) + 1
        if run.latency_ms is not None:
            latencies.append(run.latency_ms)

    avg_latency = sum(latencies) / len(latencies) if latencies else None

    return {
        "campaign_id": str(campaign_id),
        "total_runs": total,
        "outcome_counts": outcome_counts,
        "failure_reasons": failure_reasons,
        "avg_latency_ms": round(avg_latency, 1) if avg_latency is not None else None,
        "completed": sum(1 for r in runs if r.state == "completed"),
        "failed": sum(1 for r in runs if r.state == "failed"),
        "pending": sum(1 for r in runs if r.state in ("pending", "running")),
    }
