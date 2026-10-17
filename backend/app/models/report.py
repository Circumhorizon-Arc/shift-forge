import enum
from datetime import datetime, timezone
from typing import Optional
# pyrefly: ignore[missing-import]
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
# pyrefly: ignore[missing-import]
from sqlalchemy.orm import relationship, Mapped
# pyrefly: ignore[missing-import]
from app.database import Base


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    EXPLAINED = "explained"
    FAILED = "failed"


class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = Column(String(200), nullable=False)
    file_path: Mapped[str] = Column(String(500), nullable=False)
    original_filename: Mapped[str] = Column(String(255), nullable=False)
    mime_type: Mapped[str] = Column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = Column(Integer, nullable=False)
    extracted_text: Mapped[Optional[str]] = Column(Text, nullable=True)
    report_date: Mapped[datetime] = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    processing_status: Mapped[ReportStatus] = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", backref="medical_reports")
    findings = relationship("ReportFinding", back_populates="report", cascade="all, delete-orphan")
    summary_rel = relationship("ReportSummary", back_populates="report", uselist=False, cascade="all, delete-orphan")


class ReportFinding(Base):
    __tablename__ = "report_findings"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    report_id: Mapped[int] = Column(Integer, ForeignKey("medical_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    test_name: Mapped[str] = Column(String(150), nullable=False)
    value: Mapped[str] = Column(String(50), nullable=False)
    unit: Mapped[Optional[str]] = Column(String(30), nullable=True)
    reference_range: Mapped[Optional[str]] = Column(String(50), nullable=True)
    is_abnormal: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    clinical_note: Mapped[Optional[str]] = Column(String(255), nullable=True)

    report = relationship("MedicalReport", back_populates="findings")


class ReportSummary(Base):
    __tablename__ = "report_summaries"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    report_id: Mapped[int] = Column(Integer, ForeignKey("medical_reports.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    summary: Mapped[str] = Column(Text, nullable=False)
    plain_language_explanation: Mapped[str] = Column(Text, nullable=False)
    doctor_questions: Mapped[str] = Column(Text, nullable=False)  # JSON-encoded array of questions
    model_version: Mapped[str] = Column(String(50), default="gemini-1.5-flash", nullable=False)
    generated_at: Mapped[datetime] = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    report = relationship("MedicalReport", back_populates="summary_rel")
