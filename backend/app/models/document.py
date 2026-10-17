import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship, Mapped
from app.database import Base


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class DocumentType(str, enum.Enum):
    PRESCRIPTION = "prescription"
    LAB_REPORT = "lab_report"
    DISCHARGE_SUMMARY = "discharge_summary"
    OTHER = "other"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = Column(String(200), nullable=False)
    document_type: Mapped[DocumentType] = Column(Enum(DocumentType), default=DocumentType.OTHER, nullable=False)
    filename: Mapped[str] = Column(String(255), nullable=False)
    original_filename: Mapped[str] = Column(String(255), nullable=False)
    file_path: Mapped[str] = Column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = Column(Integer, nullable=False)
    mime_type: Mapped[str] = Column(String(100), nullable=False)

    # Processed and AI extracted fields
    extracted_text: Mapped[Optional[str]] = Column(Text, nullable=True)
    ai_summary: Mapped[Optional[str]] = Column(Text, nullable=True)
    extracted_entities: Mapped[Optional[str]] = Column(Text, nullable=True)  # JSON-encoded findings/medicines
    status: Mapped[DocumentStatus] = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)

    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="documents")
