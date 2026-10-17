from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, AliasChoices


class HealthRecordCreate(BaseModel):
    metric_type: str = Field(..., description="e.g. blood_pressure, glucose, heart_rate, weight", validation_alias=AliasChoices("metric_type", "metricType"))
    value: float = Field(..., description="Numeric value of measurement")
    unit: str = Field(..., description="e.g. mmHg, mg/dL, bpm, kg")
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = Field(None, validation_alias=AliasChoices("recorded_at", "recordedAt"))
    source: Optional[str] = "manual"

    model_config = ConfigDict(populate_by_name=True)


class HealthRecordResponse(BaseModel):
    id: int
    user_id: int
    metric_type: str
    value: float
    unit: str
    notes: Optional[str] = None
    recorded_at: datetime
    created_at: datetime

    # Frontend camelCase aliases
    metricType: Optional[str] = None
    recordedAt: Optional[str] = None
    source: Optional[str] = "manual"

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MetricSummaryResponse(BaseModel):
    metricType: str
    currentValue: float
    previousValue: Optional[float] = None
    unit: str
    changePercent: Optional[float] = 0.0
    trend: str = "stable"  # 'improving' | 'stable' | 'declining'
    status: str = "optimal"  # 'optimal' | 'borderline' | 'abnormal'
    min: float
    max: float
    average: float
    latestDate: str
