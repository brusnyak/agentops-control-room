import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.campaign import Campaign
from app.models.run import Run
from app.models.webhook_event import WebhookEvent
from app.models.workflow_template import WorkflowTemplate
from app.schemas.campaign import CampaignCreate, CampaignRead
from app.schemas.export import ExportRequest, ExportResult

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("", response_model=CampaignRead, status_code=201)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)):
    template = db.get(WorkflowTemplate, payload.workflow_template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    campaign = Campaign(workflow_template_id=payload.workflow_template_id, name=payload.name, status="active")
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("", response_model=list[CampaignRead])
def list_campaigns(db: Session = Depends(get_db)):
    return db.query(Campaign).order_by(Campaign.created_at.desc()).all()


@router.get("/{campaign_id}", response_model=CampaignRead)
def get_campaign(campaign_id: uuid.UUID, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.post("/{campaign_id}/export", response_model=ExportResult)
def export_campaign(campaign_id: uuid.UUID, payload: ExportRequest, db: Session = Depends(get_db)):
    """Push this campaign's run results to an external webhook (CRM, Zapier, etc.) — the
    'CRM updates' half of Huzzle's posting. Import already existed (contacts); this is export."""
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    runs = db.query(Run).filter(Run.campaign_id == campaign_id).all()
    summaries = [
        {
            "run_id": str(r.id),
            "contact_id": str(r.contact_id),
            "channel": r.channel,
            "state": r.state,
            "outcome": r.outcome,
            "latency_ms": r.latency_ms,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in runs
    ]

    webhook_url = str(payload.webhook_url)
    try:
        response = httpx.post(
            webhook_url,
            json={"campaign_id": str(campaign_id), "campaign_name": campaign.name, "runs": summaries},
            timeout=15,
        )
        delivered = response.status_code < 400
        status_code = response.status_code
        error = None if delivered else f"Target returned {response.status_code}"
    except httpx.HTTPError as exc:
        delivered = False
        status_code = None
        error = str(exc)

    db.add(
        WebhookEvent(
            run_id=None,
            provider="export",
            event_type="campaign_export",
            payload={
                "campaign_id": str(campaign_id), "webhook_url": webhook_url,
                "run_count": len(summaries), "delivered": delivered, "error": error,
            },
        )
    )
    db.commit()

    return ExportResult(delivered=delivered, run_count=len(summaries), status_code=status_code, error=error)
