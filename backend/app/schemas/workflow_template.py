import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class WorkflowTemplateCreate(BaseModel):
    name: str
    version: int = Field(default=1, ge=1)
    channel: str = Field(pattern="^(email|voice_simulated|sms_simulated)$")
    goal_prompt: str = Field(min_length=1)
    eval_rubric: str = Field(min_length=1)
    config: dict | None = None


class WorkflowTemplateRead(BaseModel):
    id: uuid.UUID
    name: str
    version: int
    channel: str
    goal_prompt: str
    eval_rubric: str
    config: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RegressionPoint(BaseModel):
    version: int
    template_id: uuid.UUID
    run_count: int
    avg_rule_score: float | None
    avg_llm_score: float | None
    pass_rate: float | None


class RegressionReport(BaseModel):
    name: str
    points: list[RegressionPoint]
