from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class HealthRecordCreate(BaseModel):
    metric_type: str = Field(..., description="e.g., blood_pressure_sys, blood_pressure_dia, glucose, heart_rate, weight")
    value: float = Field(..., description="Numeric value of measurement")
    unit: str = Field(..., description="e.g., mmHg, mg/dL, bpm, kg")
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None


class HealthRecordResponse(BaseModel):
    id: int
    user_id: int
    metric_type: str
    value: float
    unit: str
    notes: Optional[str] = None
    recorded_at: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
