import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.workflow_template import WorkflowTemplate
from app.schemas.workflow_template import WorkflowTemplateCreate, WorkflowTemplateRead

router = APIRouter(prefix="/workflow-templates", tags=["workflow-templates"])


@router.post("", response_model=WorkflowTemplateRead, status_code=201)
def create_template(payload: WorkflowTemplateCreate, db: Session = Depends(get_db)):
    template = WorkflowTemplate(**payload.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("", response_model=list[WorkflowTemplateRead])
def list_templates(db: Session = Depends(get_db)):
    return db.query(WorkflowTemplate).order_by(WorkflowTemplate.created_at.desc()).all()


@router.get("/{template_id}", response_model=WorkflowTemplateRead)
def get_template(template_id: uuid.UUID, db: Session = Depends(get_db)):
    template = db.get(WorkflowTemplate, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    return template
