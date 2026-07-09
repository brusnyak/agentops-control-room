import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_llm
from app.models.campaign import Campaign
from app.models.evaluation import Evaluation
from app.models.message import Message
from app.models.run import Run
from app.models.workflow_template import WorkflowTemplate
from app.schemas.evaluation import EvaluationRead
from app.services.cost_tracker import record_llm_call
from app.services.evaluator import llm_judge, rule_check
from app.services.llm_client import LLMProvider, LLMProviderUnavailableError
from app.services.parsing import ParsingFailedError

router = APIRouter(prefix="/evals", tags=["evals"])


@router.post("/{run_id}", response_model=EvaluationRead, status_code=201)
def create_evaluation(run_id: uuid.UUID, db: Session = Depends(get_db), llm: LLMProvider = Depends(get_llm)):
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    messages = db.query(Message).filter(Message.run_id == run_id).order_by(Message.created_at).all()

    rule_score, rule_tags = rule_check(run, messages)

    campaign = db.get(Campaign, run.campaign_id)
    template = db.get(WorkflowTemplate, campaign.workflow_template_id)

    started = time.perf_counter()
    llm_score = None
    passed = rule_score == 1.0
    failure_tags = list(rule_tags)
    notes = "Rule checks only (LLM judge unavailable)."

    try:
        judge_result = llm_judge(llm, template=template, messages=messages)
        record_llm_call(
            db, purpose="evaluation", provider=llm.provider_name, model=llm.model,
            usage=judge_result.usage, attempts=judge_result.attempts,
            latency_ms=(time.perf_counter() - started) * 1000, success=True,
        )
        judge = judge_result.value
        llm_score = judge.llm_score
        passed = passed and judge.passed
        failure_tags = list(dict.fromkeys(failure_tags + judge.failure_tags))
        notes = judge.notes
    except (ParsingFailedError, LLMProviderUnavailableError) as exc:
        usage = getattr(exc, "usage", None)
        if usage is not None:
            record_llm_call(
                db, purpose="evaluation", provider=llm.provider_name, model=llm.model,
                usage=usage, attempts=getattr(exc, "attempts", 1),
                latency_ms=(time.perf_counter() - started) * 1000, success=False, error=str(exc),
            )

    evaluation = Evaluation(
        run_id=run_id, rule_score=rule_score, llm_score=llm_score, passed=passed,
        failure_tags=failure_tags, notes=notes,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation


@router.get("/{run_id}", response_model=list[EvaluationRead])
def list_evaluations(run_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(Evaluation).filter(Evaluation.run_id == run_id).order_by(Evaluation.created_at.desc()).all()
