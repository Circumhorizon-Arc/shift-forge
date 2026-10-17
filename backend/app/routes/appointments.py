from typing import List
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

router = APIRouter(prefix="/appointments", tags=["Appointments & Teleconsultation"])


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    payload: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Books a consultation appointment with a registered doctor."""
    # Verify doctor exists and has doctor role
    doctor = db.query(User).filter(User.id == payload.doctor_id).first()
    if not doctor or doctor.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specified doctor was not found or is not a registered doctor.",
        )

    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=payload.doctor_id,
        appointment_time=payload.appointment_time,
        reason=payload.reason,
        status=AppointmentStatus.REQUESTED,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/", response_model=List[AppointmentResponse])
def list_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lists appointments. Patients see their requested visits;
    doctors see their incoming patient appointments; admins see all.
    """
    if current_user.role == UserRole.ADMIN:
        return db.query(Appointment).order_by(Appointment.appointment_time.asc()).all()
    elif current_user.role == UserRole.DOCTOR:
        return (
            db.query(Appointment)
            .filter(Appointment.doctor_id == current_user.id)
            .order_by(Appointment.appointment_time.asc())
            .all()
        )
    else:
        return (
            db.query(Appointment)
            .filter(Appointment.patient_id == current_user.id)
            .order_by(Appointment.appointment_time.asc())
            .all()
        )


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates appointment status or notes. Enforces authorization:
    only the assigned doctor, patient (to cancel), or admin can modify.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    # Authorization rules
    is_doctor = current_user.id == appointment.doctor_id or current_user.role == UserRole.DOCTOR
    is_patient = current_user.id == appointment.patient_id
    is_admin = current_user.role == UserRole.ADMIN

    if not (is_doctor or is_patient or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this appointment.",
        )

    # Patients can only cancel their appointments
    if is_patient and not is_doctor and not is_admin:
        if payload.status and payload.status != AppointmentStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patients are only permitted to cancel appointments.",
            )

    if payload.status is not None:
        appointment.status = payload.status
    if payload.doctor_notes is not None and (is_doctor or is_admin):
        appointment.doctor_notes = payload.doctor_notes
    if payload.appointment_time is not None and (is_doctor or is_admin):
        appointment.appointment_time = payload.appointment_time

    db.commit()
    db.refresh(appointment)
    return appointment
