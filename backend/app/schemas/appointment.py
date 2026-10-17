from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_time: datetime
    reason: str = Field(..., min_length=3, max_length=300)


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
    model_config = ConfigDict(from_attributes=True)
