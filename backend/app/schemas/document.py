from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.document import DocumentType, DocumentStatus


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    title: str
    document_type: DocumentType
    filename: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    extracted_text: Optional[str] = None
    ai_summary: Optional[str] = None
    extracted_entities: Optional[str] = None
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    document_type: Optional[DocumentType] = None


class DocumentAnalysisResponse(BaseModel):
    document_id: int
    status: DocumentStatus
    summary: str
    extracted_text_preview: str
    key_findings: list[str]
    suggested_actions: list[str]
