from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.cost_tracker import get_observability_stats

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    return get_observability_stats(db)
