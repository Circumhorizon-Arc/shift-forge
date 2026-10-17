from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.health_record import HealthRecord
from app.schemas.health_record import HealthRecordCreate, HealthRecordResponse, MetricSummaryResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/health-records", tags=["HealthSense — Health Tracker"])
health_alias_router = APIRouter(prefix="/health", tags=["HealthSense — Health Tracker"])


def _format_record(r: HealthRecord) -> Dict[str, Any]:
    return {
        "id": r.id,
        "user_id": r.user_id,
        "metric_type": r.metric_type,
        "metricType": r.metric_type,
        "value": r.value,
        "unit": r.unit,
        "notes": r.notes,
        "recorded_at": r.recorded_at,
        "recordedAt": r.recorded_at.strftime("%Y-%m-%d") if r.recorded_at else "",
        "created_at": r.created_at,
        "source": "manual",
    }


def _calculate_metric_summary(records: List[HealthRecord], metric_type: str) -> Dict[str, Any]:
    if not records:
        units = {
            "blood_pressure": "mmHg",
            "blood_pressure_sys": "mmHg",
            "blood_glucose": "mg/dL",
            "glucose": "mg/dL",
            "heart_rate": "bpm",
            "weight": "kg",
            "body_temp": "°F",
        }
        return {
            "metricType": metric_type,
            "currentValue": 0.0,
            "previousValue": None,
            "unit": units.get(metric_type, "units"),
            "changePercent": 0.0,
            "trend": "stable",
            "status": "optimal",
            "min": 0.0,
            "max": 0.0,
            "average": 0.0,
            "latestDate": "No entries",
        }

    sorted_records = sorted(records, key=lambda r: r.recorded_at)
    curr = sorted_records[-1].value
    prev = sorted_records[-2].value if len(sorted_records) > 1 else None
    vals = [r.value for r in sorted_records]

    change_pct = round(((curr - prev) / prev) * 100, 1) if prev else 0.0
    trend = "stable"
    if change_pct > 2:
        trend = "declining" if metric_type in ("blood_pressure", "glucose", "weight") else "improving"
    elif change_pct < -2:
        trend = "improving" if metric_type in ("blood_pressure", "glucose", "weight") else "declining"

    return {
        "metricType": metric_type,
        "currentValue": round(curr, 1),
        "previousValue": round(prev, 1) if prev else None,
        "unit": sorted_records[-1].unit,
        "changePercent": change_pct,
        "trend": trend,
        "status": "optimal",
        "min": round(min(vals), 1),
        "max": round(max(vals), 1),
        "average": round(sum(vals) / len(vals), 1),
        "latestDate": sorted_records[-1].recorded_at.strftime("%b %d, %Y") if sorted_records[-1].recorded_at else "Recent",
    }


# Standard /health-records endpoints
@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def add_health_measurement(
    payload: HealthRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds a vital health measurement (blood pressure, glucose, heart rate, weight, etc.)."""
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
    return _format_record(record)


@router.get("", response_model=List[Dict[str, Any]])
def get_health_history(
    metric_type: Optional[str] = Query(None, description="Filter by metric (e.g., glucose, heart_rate)"),
    metricType: Optional[str] = Query(None, description="Alias filter"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves health measurements history for the authenticated patient."""
    filter_val = metric_type or metricType
    query = db.query(HealthRecord).filter(HealthRecord.user_id == current_user.id)
    if filter_val:
        query = query.filter(HealthRecord.metric_type == filter_val.strip().lower())

    records = query.order_by(HealthRecord.recorded_at.asc()).all()
    return [_format_record(r) for r in records]


@router.delete("/{record_id}", status_code=status.HTTP_200_OK)
def delete_health_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a single vital measurement entry."""
    record = (
        db.query(HealthRecord)
        .filter(HealthRecord.id == record_id, HealthRecord.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")

    db.delete(record)
    db.commit()
    return {"success": True, "message": "Health record deleted"}


@router.get("/summary/{metric_type}", response_model=Dict[str, Any])
def get_metric_summary(
    metric_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Computes high, low, average, and trend aggregates for a vital metric."""
    records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.metric_type == metric_type.strip().lower(),
        )
        .order_by(HealthRecord.recorded_at.asc())
        .all()
    )
    return _calculate_metric_summary(records, metric_type)


# Direct /health/records and /health/summary alias endpoints for Frontend
@health_alias_router.post("/records", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def alias_add_health_record(
    payload: HealthRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return add_health_measurement(payload, current_user, db)


@health_alias_router.get("/records", response_model=List[Dict[str, Any]])
def alias_get_health_records(
    metric_type: Optional[str] = Query(None),
    metricType: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_health_history(metric_type, metricType, current_user, db)


@health_alias_router.delete("/records/{record_id}", status_code=status.HTTP_200_OK)
def alias_delete_health_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return delete_health_record(record_id, current_user, db)


@health_alias_router.get("/summary/{metric_type}", response_model=Dict[str, Any])
def alias_get_metric_summary(
    metric_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_metric_summary(metric_type, current_user, db)
