import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class EvalJudgeParsed(BaseModel):
    """Structured output the LLM judge must produce when scoring a run."""

    llm_score: float = Field(ge=0, le=100, default=0)
    passed: bool = False
    failure_tags: list[str] = Field(default_factory=list)
    notes: str = ""


class EvaluationRead(BaseModel):
    id: uuid.UUID
    run_id: uuid.UUID
    rule_score: float
    llm_score: float | None
    passed: bool
    failure_tags: list[str] | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
