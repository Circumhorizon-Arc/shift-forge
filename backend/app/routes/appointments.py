from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/appointments", tags=["HealthSense — Appointments & Teleconsultation"])


def _format_appointment(a: Appointment) -> Dict[str, Any]:
    doctor_name = a.doctor.full_name if a.doctor else "Dr. Sarah Chen, MD"
    is_tele = "tele" in (a.reason or "").lower()
    st_val = "upcoming"
    if a.status == AppointmentStatus.CANCELLED:
        st_val = "cancelled"
    elif a.status == AppointmentStatus.COMPLETED:
        st_val = "completed"

    return {
        "id": str(a.id),
        "doctorName": doctor_name,
        "specialty": "Internal Medicine & Diagnostics",
        "date": a.appointment_time.strftime("%B %d, %Y") if a.appointment_time else "October 24, 2026",
        "time": a.appointment_time.strftime("%I:%M %p") if a.appointment_time else "10:30 AM",
        "clinicOrHospital": "HealthSense Wellness Center",
        "status": st_val,
        "type": "telehealth" if is_tele else "in-person",
        "notes": a.doctor_notes or a.reason or "Routine health assessment",
        "patient_id": a.patient_id,
        "doctor_id": a.doctor_id,
        "appointment_time": a.appointment_time,
        "reason": a.reason,
        "created_at": a.created_at,
        "updated_at": a.updated_at,
    }


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def book_appointment(
    payload: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Books a consultation appointment with a doctor."""
    doctor_id = payload.doctor_id
    if doctor_id:
        doctor = db.query(User).filter(User.id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The specified doctor was not found.",
            )
    else:
        # Default to first doctor or fallback to current user/admin
        doctor = db.query(User).filter(User.role == UserRole.DOCTOR).first()
        if not doctor:
            doctor = db.query(User).filter(User.id != current_user.id).first() or current_user
        doctor_id = doctor.id

    app_time = payload.appointment_time
    if not app_time:
        app_time = datetime.now(timezone.utc) + timedelta(days=3)

    reason = payload.reason or (f"Consultation with {payload.doctorName or 'Physician'} ({payload.specialty or 'General'})")

    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=doctor_id,
        appointment_time=app_time,
        reason=reason,
        status=AppointmentStatus.REQUESTED,
        doctor_notes=payload.notes,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return _format_appointment(appointment)


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def list_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists appointments with role-based filtering."""
    if current_user.role == UserRole.ADMIN:
        appointments = db.query(Appointment).order_by(Appointment.appointment_time.asc()).all()
    elif current_user.role == UserRole.DOCTOR:
        appointments = (
            db.query(Appointment)
            .filter(Appointment.doctor_id == current_user.id)
            .order_by(Appointment.appointment_time.asc())
            .all()
        )
    else:
        appointments = (
            db.query(Appointment)
            .filter(Appointment.patient_id == current_user.id)
            .order_by(Appointment.appointment_time.asc())
            .all()
        )

    return [_format_appointment(a) for a in appointments]


@router.patch("/{appointment_id}/cancel", response_model=Dict[str, Any])
def cancel_appointment_alias(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancels an appointment."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    if appointment.patient_id != current_user.id and current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    db.refresh(appointment)
    return _format_appointment(appointment)


@router.patch("/{appointment_id}", response_model=Dict[str, Any])
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates appointment status or doctor notes."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    is_doctor = current_user.id == appointment.doctor_id or current_user.role == UserRole.DOCTOR
    is_patient = current_user.id == appointment.patient_id
    is_admin = current_user.role == UserRole.ADMIN

    if not (is_doctor or is_patient or is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    if is_patient and not is_doctor and not is_admin:
        if payload.status and payload.status != AppointmentStatus.CANCELLED:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patients can only cancel appointments.")

    if payload.status is not None:
        appointment.status = payload.status
    if payload.doctor_notes is not None and (is_doctor or is_admin):
        appointment.doctor_notes = payload.doctor_notes
    if payload.appointment_time is not None and (is_doctor or is_admin):
        appointment.appointment_time = payload.appointment_time

    db.commit()
    db.refresh(appointment)
    return _format_appointment(appointment)
