from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.health_record import HealthRecord
from app.schemas.health_record import HealthRecordCreate, HealthRecordResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/health-records", tags=["CareBridge AI — Health Tracker"])


@router.post("", response_model=HealthRecordResponse, status_code=status.HTTP_201_CREATED)
def add_health_measurement(
    payload: HealthRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Adds a vital health measurement (blood pressure, glucose, heart rate, weight, etc.)
    for personal health tracking and visualization.
    """
    record = HealthRecord(
        user_id=current_user.id,
        metric_type=payload.metric_type.strip().lower(),
        value=payload.value,
        unit=payload.unit.strip(),
        notes=payload.notes,
        recorded_at=payload.recorded_at or datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=List[HealthRecordResponse])
def get_health_history(
    metric_type: Optional[str] = Query(None, description="Filter by metric (e.g., glucose, heart_rate)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves health measurements history for the authenticated patient.
    Feeds directly into frontend line charts (Recharts).
    """
    query = db.query(HealthRecord).filter(HealthRecord.user_id == current_user.id)
    if metric_type:
        query = query.filter(HealthRecord.metric_type == metric_type.strip().lower())

    return query.order_by(HealthRecord.recorded_at.asc()).all()
