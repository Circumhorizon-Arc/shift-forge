import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    EXPLAINED = "explained"
    FAILED = "failed"


class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    extracted_text = Column(Text, nullable=True)
    report_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    processing_status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", backref="medical_reports")
    findings = relationship("ReportFinding", back_populates="report", cascade="all, delete-orphan")
    summary_rel = relationship("ReportSummary", back_populates="report", uselist=False, cascade="all, delete-orphan")


class ReportFinding(Base):
    __tablename__ = "report_findings"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("medical_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    test_name = Column(String(150), nullable=False)
    value = Column(String(50), nullable=False)
    unit = Column(String(30), nullable=True)
    reference_range = Column(String(50), nullable=True)
    is_abnormal = Column(Boolean, default=False, nullable=False)
    clinical_note = Column(String(255), nullable=True)

    report = relationship("MedicalReport", back_populates="findings")


class ReportSummary(Base):
    __tablename__ = "report_summaries"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("medical_reports.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    summary = Column(Text, nullable=False)
    plain_language_explanation = Column(Text, nullable=False)
    doctor_questions = Column(Text, nullable=False)  # JSON-encoded array of questions
    model_version = Column(String(50), default="gemini-1.5-flash", nullable=False)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    report = relationship("MedicalReport", back_populates="summary_rel")
