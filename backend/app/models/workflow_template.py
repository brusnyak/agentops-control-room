import uuid

from sqlalchemy import Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db import Base

CHANNELS = ("email", "voice_simulated", "sms_simulated")


class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    channel = Column(String, nullable=False)  # one of CHANNELS
    goal_prompt = Column(Text, nullable=False)  # instructs the LLM what the outreach should achieve
    eval_rubric = Column(Text, nullable=False)  # instructs the LLM judge how to score a run
    config = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
