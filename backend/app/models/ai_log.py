import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class TriageLevel(str, enum.Enum):
    LOW = "low"            # Self-care / routine
    MODERATE = "moderate"  # Visit clinic / doctor appointment
    HIGH = "high"          # Urgent care needed within 24h
    EMERGENCY = "emergency"# Immediate hospital / emergency service needed


class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user_query = Column(Text, nullable=False)
    symptoms = Column(Text, nullable=True)
    triage_level = Column(Enum(TriageLevel), default=TriageLevel.LOW, nullable=False)
    possible_conditions = Column(Text, nullable=True)  # JSON or bullet list
    recommendations = Column(Text, nullable=False)
    suggested_specialist = Column(String(100), nullable=True)  # e.g., Neurologist, General Physician
    raw_ai_response = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="ai_interactions")
