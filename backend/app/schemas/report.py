from typing import Optional, List, Dict, Any
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

    # Frontend camelCase aliases
    testName: Optional[str] = None
    referenceRange: Optional[str] = None
    interpretation: Optional[str] = None
    flag: Optional[str] = None
    category: Optional[str] = None
    confidenceScore: Optional[float] = 0.98

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


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

    # Frontend compatibility fields
    name: Optional[str] = None
    type: Optional[str] = "Clinical Diagnostic Report"
    uploadedAt: Optional[str] = None
    fileSize: Optional[str] = None
    fileType: Optional[str] = None
    status: Optional[str] = None
    doctorOrLab: Optional[str] = "HealthSense Diagnostic Services"
    findingsCount: Optional[int] = None
    summaryPreview: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ReportExplanationResponse(BaseModel):
    report_id: int
    title: str
    status: ReportStatus
    summary: str
    plain_language_explanation: str
    findings: List[ReportFindingSchema]
    doctor_questions: List[str]
    disclaimer: str = (
        "HealthSense provides educational and organizational insights only, "
        "and is NOT a substitute for certified medical diagnosis. "
        "Always discuss laboratory findings with your qualified healthcare provider."
    )


class FrontendReportFinding(BaseModel):
    id: str
    testName: str
    value: str
    unit: str
    referenceRange: Optional[str] = None
    interpretation: str  # 'within-range' | 'outside-range' | 'unknown'
    flag: Optional[str] = "normal"
    category: Optional[str] = "Laboratory Diagnostic"
    confidenceScore: Optional[float] = 0.98


class FrontendReportAnalysis(BaseModel):
    reportId: str
    reportName: str
    reportDate: str
    labName: Optional[str] = "HealthSense Diagnostic Services"
    status: str = "analyzed"
    summary: str
    findings: List[FrontendReportFinding] = []
    explanations: List[str] = []
    doctorQuestions: List[str] = []
    disclaimer: str = (
        "HealthSense provides educational explanations of uploaded health information. "
        "It does not diagnose medical conditions or replace professional medical advice. "
        "Please discuss your results with a qualified healthcare professional."
    )
    analyzedAt: Optional[str] = None
    extractedFactsCount: Optional[int] = 0


class FrontendMedicalReport(BaseModel):
    id: str
    name: str
    type: str = "Clinical Diagnostic Report"
    uploadedAt: str
    fileSize: Optional[str] = None
    fileType: Optional[str] = None
    status: str = "analyzed"
    doctorOrLab: Optional[str] = "HealthSense Diagnostic Services"
    findingsCount: Optional[int] = 0
    summaryPreview: Optional[str] = None


class ReportUploadResponse(BaseModel):
    report: Dict[str, Any]
    analysis: Dict[str, Any]
