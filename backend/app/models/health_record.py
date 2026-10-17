from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped
from app.database import Base


class HealthRecord(Base):
    __tablename__ = "health_records"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_type: Mapped[str] = Column(String(50), nullable=False, index=True)  # e.g., blood_pressure_sys, blood_pressure_dia, glucose, heart_rate, weight
    value: Mapped[float] = Column(Float, nullable=False)
    unit: Mapped[str] = Column(String(30), nullable=False)  # e.g., mmHg, mg/dL, bpm, kg
    notes: Mapped[Optional[str]] = Column(Text, nullable=True)
    recorded_at: Mapped[datetime] = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", backref="health_records")
