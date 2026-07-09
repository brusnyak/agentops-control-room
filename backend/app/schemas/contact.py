import uuid
from datetime import datetime

from pydantic import BaseModel


class ContactCreate(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None
    meta: dict | None = None


class ContactRead(BaseModel):
    id: uuid.UUID
    name: str
    phone: str | None
    email: str | None
    meta: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
