import uuid

from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db import Base

CHANNELS = ("email", "voice_simulated", "sms_simulated")


class WorkflowTemplate(Base):
    """`name` is the template "family" identifier; editing a template's prompt/rubric creates a
    new row with the same name and an incremented `version`, rather than mutating history —
    otherwise there's nothing to compare eval scores against across versions. See
    GET /workflow-templates/regression for the release-over-release comparison this enables."""

    __tablename__ = "workflow_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    channel = Column(String, nullable=False)  # one of CHANNELS
    goal_prompt = Column(Text, nullable=False)  # instructs the LLM what the outreach should achieve
    eval_rubric = Column(Text, nullable=False)  # instructs the LLM judge how to score a run
    config = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
