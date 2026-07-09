import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_template_id = Column(UUID(as_uuid=True), ForeignKey("workflow_templates.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="draft")  # draft | active | completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
