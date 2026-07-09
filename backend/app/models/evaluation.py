import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    rule_score = Column(Float, nullable=False)  # 0-1, deterministic checks
    llm_score = Column(Float, nullable=True)  # 0-100, LLM-as-judge
    passed = Column(Boolean, nullable=False)
    failure_tags = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
