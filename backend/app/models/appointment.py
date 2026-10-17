import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class AppointmentStatus(str, enum.Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    appointment_time = Column(DateTime, nullable=False)
    reason = Column(String(300), nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.REQUESTED, nullable=False)
    doctor_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_appointments")
