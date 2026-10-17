import json
import os
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.document import Document, DocumentStatus, DocumentType
from app.schemas.document import DocumentResponse, DocumentAnalysisResponse
from app.core.dependencies import get_current_user
from app.services.file_service import file_service
from app.services.document_processor import document_processor
from app.services.ai_service import ai_service

router = APIRouter(prefix="/documents", tags=["Medical Documents & Prescriptions"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: DocumentType = Form(DocumentType.PRESCRIPTION),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Uploads, validates, processes, and extracts insights from medical reports or prescriptions.
    Enforces format checking (PDF, PNG, JPG), size validation, and magic byte verification.
    """
    # 1. Validate and save file securely
    unique_filename, file_path, file_size = file_service.save_file(file)

    # 2. Extract content from document
    extracted_text = document_processor.process_document(
        file_path=file_path,
        mime_type=file.content_type or "application/octet-stream",
    )

    # 3. Analyze content with AI
    ai_summary = None
    extracted_entities = None
    doc_status = DocumentStatus.PROCESSED

    if extracted_text and not extracted_text.startswith("[PDF text extraction failed"):
        analysis = ai_service.analyze_medical_document(
            text_content=extracted_text,
            doc_type=document_type.value,
        )
        ai_summary = analysis.get("summary")
        extracted_entities = json.dumps({
            "key_findings": analysis.get("key_findings", []),
            "suggested_actions": analysis.get("suggested_actions", []),
        })

    # 4. Save to Database
    document = Document(
        user_id=current_user.id,
        title=title,
        document_type=document_type,
        filename=unique_filename,
        original_filename=file.filename or unique_filename,
        file_path=file_path,
        file_size_bytes=file_size,
        mime_type=file.content_type or "application/octet-stream",
        extracted_text=extracted_text,
        ai_summary=ai_summary,
        extracted_entities=extracted_entities,
        status=doc_status,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lists medical documents. Patients see only their own documents;
    doctors and admins can view patient records for consultations.
    """
    if current_user.role in [UserRole.DOCTOR, UserRole.ADMIN]:
        return db.query(Document).order_by(Document.created_at.desc()).all()
    return (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Gets a specific medical document by ID with authorization checks."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Authorization enforcement: Only document owner, doctor, or admin can access
    if doc.user_id != current_user.id and current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this medical record.",
        )
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a medical record and its local file."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if doc.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this document.",
        )

    # Delete local file if it exists
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return None
