import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
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

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    document_type = Column(Enum(DocumentType), default=DocumentType.OTHER, nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)

    # Processed and AI extracted fields
    extracted_text = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    extracted_entities = Column(Text, nullable=True)  # JSON-encoded findings/medicines
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="documents")
