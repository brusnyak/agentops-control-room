import uuid
from datetime import datetime

from pydantic import BaseModel


class CampaignCreate(BaseModel):
    workflow_template_id: uuid.UUID
    name: str


class CampaignRead(BaseModel):
    id: uuid.UUID
    workflow_template_id: uuid.UUID
    name: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
