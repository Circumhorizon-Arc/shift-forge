import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PATIENT, nullable=False)
    phone = Column(String(30), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    ai_interactions = relationship("AIInteraction", back_populates="user", cascade="all, delete-orphan")
    patient_appointments = relationship(
        "Appointment",
        back_populates="patient",
        foreign_keys="Appointment.patient_id",
        cascade="all, delete-orphan",
    )
    doctor_appointments = relationship(
        "Appointment",
        back_populates="doctor",
        foreign_keys="Appointment.doctor_id",
    )
