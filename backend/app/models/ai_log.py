import enum
from datetime import datetime
from typing import Optional
# pyrefly: ignore[missing-import]
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
# pyrefly: ignore[missing-import]
from sqlalchemy.orm import relationship, Mapped
# pyrefly: ignore[missing-import]
from app.database import Base


class TriageLevel(str, enum.Enum):
    LOW = "low"            # Self-care / routine
    MODERATE = "moderate"  # Visit clinic / doctor appointment
    HIGH = "high"          # Urgent care needed within 24h
    EMERGENCY = "emergency"# Immediate hospital / emergency service needed


class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user_query: Mapped[str] = Column(Text, nullable=False)
    symptoms: Mapped[Optional[str]] = Column(Text, nullable=True)
    triage_level: Mapped[TriageLevel] = Column(Enum(TriageLevel), default=TriageLevel.LOW, nullable=False)
    possible_conditions: Mapped[Optional[str]] = Column(Text, nullable=True)  # JSON or bullet list
    recommendations: Mapped[str] = Column(Text, nullable=False)
    suggested_specialist: Mapped[Optional[str]] = Column(String(100), nullable=True)  # e.g., Neurologist, General Physician
    raw_ai_response: Mapped[Optional[str]] = Column(Text, nullable=True)

    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="ai_interactions")
