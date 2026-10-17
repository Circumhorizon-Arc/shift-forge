from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.reminder import Reminder
from app.schemas.reminder import (
    ReminderCreate,
    ReminderResponse,
    ReminderUpdate,
    ReminderCompleteRequest,
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/reminders", tags=["HealthSense — Care Reminders"])


def _format_reminder(r: Reminder) -> Dict[str, Any]:
    due_str = r.due_at.strftime("%b %d · %I:%M %p") if r.due_at else "Upcoming"
    t_lower = (r.title or "").lower()
    if any(w in t_lower for w in ["med", "pill", "capsule", "refill", "tablet", "dose"]):
        cat = "medication-refill"
    elif any(w in t_lower for w in ["lab", "test", "blood", "urine", "panel"]):
        cat = "lab-test"
    elif any(w in t_lower for w in ["dr", "doctor", "consult", "visit"]):
        cat = "follow-up"
    else:
        cat = "general"

    return {
        "id": str(r.id),
        "user_id": r.user_id,
        "title": r.title,
        "description": r.description or "",
        "due_at": r.due_at,
        "dueText": due_str,
        "is_completed": r.is_completed,
        "completed": r.is_completed,
        "completed_at": r.completed_at,
        "created_at": r.created_at,
        "category": cat,
        "priority": "high" if not r.is_completed else "medium",
    }


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Creates a care reminder for appointments or medicine schedules."""
    due = payload.due_at or (datetime.now(timezone.utc) + timedelta(days=2))
    reminder = Reminder(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description or "",
        due_at=due,
        is_completed=False,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return _format_reminder(reminder)


@router.get("", response_model=List[Dict[str, Any]])
def list_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists all active and completed reminders for the authenticated user."""
    reminders = (
        db.query(Reminder)
        .filter(Reminder.user_id == current_user.id)
        .order_by(Reminder.due_at.asc())
        .all()
    )
    return [_format_reminder(r) for r in reminders]


@router.patch("/{reminder_id}/complete", response_model=Dict[str, Any])
def complete_reminder_alias(
    reminder_id: int,
    payload: Optional[ReminderCompleteRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marks a reminder as completed or reopened."""
    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id)
        .first()
    )
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    if payload is None:
        is_done = True
    else:
        is_done = payload.completed if payload.completed is not None else payload.is_completed
        if is_done is None:
            is_done = True

    reminder.is_completed = bool(is_done)
    reminder.completed_at = datetime.now(timezone.utc) if is_done else None

    db.commit()
    db.refresh(reminder)
    return _format_reminder(reminder)


@router.patch("/{reminder_id}", response_model=Dict[str, Any])
def update_reminder(
    reminder_id: int,
    payload: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates a reminder (e.g. title, due date, or completed status)."""
    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id)
        .first()
    )
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    if payload.title is not None:
        reminder.title = payload.title
    if payload.description is not None:
        reminder.description = payload.description
    if payload.due_at is not None:
        reminder.due_at = payload.due_at

    new_completed = payload.is_completed if payload.is_completed is not None else payload.completed
    if new_completed is not None:
        reminder.is_completed = new_completed
        reminder.completed_at = datetime.now(timezone.utc) if new_completed else None

    db.commit()
    db.refresh(reminder)
    return _format_reminder(reminder)


@router.delete("/{reminder_id}", status_code=status.HTTP_200_OK)
def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a reminder."""
    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id)
        .first()
    )
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    db.delete(reminder)
    db.commit()
    return {"success": True, "message": "Reminder deleted successfully"}
