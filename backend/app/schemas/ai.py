from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.ai_log import TriageLevel


class SymptomCheckRequest(BaseModel):
    query: str = Field(..., min_length=5, description="User description of their symptoms or feeling")
    duration: Optional[str] = Field(None, description="How long symptoms have lasted, e.g., '2 days'")
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    existing_conditions: Optional[str] = None


class SymptomCheckResponse(BaseModel):
    id: Optional[int] = None
    triage_level: TriageLevel
    triage_color: str  # green, yellow, orange, red (for frontend UI badge)
    possible_conditions: List[str]
    recommendations: str
    suggested_specialist: Optional[str] = None
    urgency_message: str
    disclaimer: str = (
        "This AI assessment is for guidance only and does NOT substitute professional medical advice. "
        "In case of emergency, contact local emergency services immediately."
    )
    created_at: Optional[datetime] = None


class AIInteractionHistoryResponse(BaseModel):
    id: int
    user_query: str
    symptoms: Optional[str] = None
    triage_level: TriageLevel
    possible_conditions: Optional[str] = None
    recommendations: str
    suggested_specialist: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
