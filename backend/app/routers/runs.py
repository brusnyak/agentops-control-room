import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_llm
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.message import Message
from app.models.run import Run
from app.models.tool_call import ToolCall
from app.models.workflow_template import WorkflowTemplate
from app.schemas.run import RunCreate, RunDetailRead, RunRead
from app.services.llm_client import LLMProvider
from app.services.run_engine import execute_run

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunRead, status_code=201)
def create_run(payload: RunCreate, db: Session = Depends(get_db), llm: LLMProvider = Depends(get_llm)):
    campaign = db.get(Campaign, payload.campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    contact = db.get(Contact, payload.contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    template = db.get(WorkflowTemplate, campaign.workflow_template_id)

    run = Run(campaign_id=campaign.id, contact_id=contact.id, channel=template.channel, state="pending")
    db.add(run)
    db.commit()
    db.refresh(run)

    # Synchronous execution for MVP simplicity — a real production system would queue this
    # (Celery/RQ/background task) so the API responds instantly. Documented tradeoff, not
    # an oversight: see docs/architecture.md.
    run = execute_run(db, llm, run, contact, template)
    return run


@router.get("", response_model=list[RunRead])
def list_runs(campaign_id: uuid.UUID | None = None, db: Session = Depends(get_db)):
    query = db.query(Run)
    if campaign_id is not None:
        query = query.filter(Run.campaign_id == campaign_id)
    return query.order_by(Run.created_at.desc()).all()


@router.get("/{run_id}", response_model=RunDetailRead)
def get_run(run_id: uuid.UUID, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    messages = db.query(Message).filter(Message.run_id == run_id).order_by(Message.created_at).all()
    tool_calls = db.query(ToolCall).filter(ToolCall.run_id == run_id).order_by(ToolCall.created_at).all()
    return RunDetailRead(
        **RunRead.model_validate(run).model_dump(),
        messages=messages,
        tool_calls=tool_calls,
    )
