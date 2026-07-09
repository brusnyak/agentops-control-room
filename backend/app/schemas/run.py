import uuid
from datetime import datetime

from pydantic import BaseModel


class RunCreate(BaseModel):
    campaign_id: uuid.UUID
    contact_id: uuid.UUID


class MessageRead(BaseModel):
    id: uuid.UUID
    direction: str
    provider: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ToolCallRead(BaseModel):
    id: uuid.UUID
    tool_name: str
    input: dict | None
    output: dict | None
    success: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RunRead(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    contact_id: uuid.UUID
    channel: str
    state: str
    outcome: str | None
    error_reason: str | None
    latency_ms: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RunDetailRead(RunRead):
    messages: list[MessageRead] = []
    tool_calls: list[ToolCallRead] = []
