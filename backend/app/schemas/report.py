from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.report import ReportStatus


class ReportFindingSchema(BaseModel):
    id: Optional[int] = None
    test_name: str
    value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    is_abnormal: bool = False
    clinical_note: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ReportSummarySchema(BaseModel):
    id: Optional[int] = None
    summary: str
    plain_language_explanation: str
    doctor_questions: List[str]
    model_version: str = "gemini-1.5-flash"
    generated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class MedicalReportResponse(BaseModel):
    id: int
    user_id: int
    title: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    report_date: datetime
    processing_status: ReportStatus
    created_at: datetime
    findings: List[ReportFindingSchema] = []
    summary_rel: Optional[ReportSummarySchema] = None
    model_config = ConfigDict(from_attributes=True)


class ReportExplanationResponse(BaseModel):
    report_id: int
    title: str
    status: ReportStatus
    summary: str
    plain_language_explanation: str
    findings: List[ReportFindingSchema]
    doctor_questions: List[str]
    disclaimer: str = (
        "CareBridge AI provides educational and organizational insights only, "
        "and is NOT a substitute for certified medical diagnosis. "
        "Always discuss laboratory findings with your qualified healthcare provider."
    )
