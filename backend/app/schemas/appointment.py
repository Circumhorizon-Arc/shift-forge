from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    doctor_id: Optional[int] = None
    appointment_time: Optional[datetime] = None
    reason: Optional[str] = "Routine consultation and lab review"

    # Frontend fields
    doctorName: Optional[str] = None
    specialty: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    clinicOrHospital: Optional[str] = None
    type: Optional[str] = "in-person"
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    doctor_notes: Optional[str] = None
    appointment_time: Optional[datetime] = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_time: datetime
    reason: str
    status: AppointmentStatus
    doctor_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Frontend compatibility fields
    doctorName: Optional[str] = None
    specialty: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    clinicOrHospital: Optional[str] = None
    type: Optional[str] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
