import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class WorkflowTemplateCreate(BaseModel):
    name: str
    channel: str = Field(pattern="^(email|voice_simulated|sms_simulated)$")
    goal_prompt: str = Field(min_length=1)
    eval_rubric: str = Field(min_length=1)
    config: dict | None = None


class WorkflowTemplateRead(BaseModel):
    id: uuid.UUID
    name: str
    channel: str
    goal_prompt: str
    eval_rubric: str
    config: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
