import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.webhook_event import WebhookEvent

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/inbound")
async def receive_webhook(request: Request, run_id: uuid.UUID | None = None, db: Session = Depends(get_db)):
    """Generic inbound webhook receiver — logs the raw payload. In production this is where a
    real voice/SMS provider (Retell, Twilio) would post delivery/call-status events."""
    payload = await request.json()
    event = WebhookEvent(
        run_id=run_id,
        provider=request.headers.get("x-provider", "unknown"),
        event_type=payload.get("event_type", "unknown"),
        payload=payload,
    )
    db.add(event)
    db.commit()
    return {"status": "received", "id": str(event.id)}
