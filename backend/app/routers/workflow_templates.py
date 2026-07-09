import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.campaign import Campaign
from app.models.evaluation import Evaluation
from app.models.run import Run
from app.models.workflow_template import WorkflowTemplate
from app.schemas.workflow_template import (
    RegressionPoint,
    RegressionReport,
    WorkflowTemplateCreate,
    WorkflowTemplateRead,
)

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


@router.get("/regression", response_model=RegressionReport)
def regression_report(name: str, db: Session = Depends(get_db)):
    """Compare eval scores across versions of the same template family — the
    'reliable release-over-release' signal named in Action1/JUPUS postings."""
    templates = (
        db.query(WorkflowTemplate)
        .filter(WorkflowTemplate.name == name)
        .order_by(WorkflowTemplate.version)
        .all()
    )
    if not templates:
        raise HTTPException(status_code=404, detail=f"No workflow templates named '{name}'")

    points = []
    for template in templates:
        campaign_ids = [c.id for c in db.query(Campaign.id).filter(Campaign.workflow_template_id == template.id)]
        run_ids = [r.id for r in db.query(Run.id).filter(Run.campaign_id.in_(campaign_ids))] if campaign_ids else []
        evaluations = db.query(Evaluation).filter(Evaluation.run_id.in_(run_ids)).all() if run_ids else []

        rule_scores = [e.rule_score for e in evaluations]
        llm_scores = [e.llm_score for e in evaluations if e.llm_score is not None]
        passed = [e.passed for e in evaluations]

        points.append(
            RegressionPoint(
                version=template.version,
                template_id=template.id,
                run_count=len(evaluations),
                avg_rule_score=round(sum(rule_scores) / len(rule_scores), 4) if rule_scores else None,
                avg_llm_score=round(sum(llm_scores) / len(llm_scores), 2) if llm_scores else None,
                pass_rate=round(sum(passed) / len(passed), 4) if passed else None,
            )
        )

    return RegressionReport(name=name, points=points)


@router.get("/{template_id}", response_model=WorkflowTemplateRead)
def get_template(template_id: uuid.UUID, db: Session = Depends(get_db)):
    template = db.get(WorkflowTemplate, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    return template
