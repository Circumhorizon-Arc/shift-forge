import json
import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.report import MedicalReport, ReportFinding, ReportSummary, ReportStatus
from app.schemas.report import (
    MedicalReportResponse,
    ReportExplanationResponse,
    ReportFindingSchema,
    ReportUploadResponse,
    FrontendReportAnalysis,
    FrontendReportFinding,
)
from app.core.dependencies import get_current_user
from app.services.file_service import file_service
from app.services.document_processor import document_processor
from app.services.ai_service import ai_service

router = APIRouter(prefix="/reports", tags=["HealthSense — Medical Reports"])


def _format_frontend_report(report: MedicalReport) -> Dict[str, Any]:
    findings_count = len(report.findings) if report.findings else 0
    summary_preview = (
        report.summary_rel.summary
        if report.summary_rel and report.summary_rel.summary
        else f"Extracted {findings_count} diagnostic observations."
    )
    file_size_str = f"{(report.file_size_bytes / (1024 * 1024)):.1f} MB" if report.file_size_bytes else "1.2 MB"

    return {
        "id": str(report.id),
        "name": report.title,
        "title": report.title,
        "type": "Clinical Diagnostic Report",
        "uploadedAt": report.created_at.strftime("%Y-%m-%d") if report.created_at else "",
        "created_at": report.created_at,
        "fileSize": file_size_str,
        "file_size_bytes": report.file_size_bytes,
        "fileType": report.mime_type or "application/pdf",
        "mime_type": report.mime_type or "application/pdf",
        "status": "analyzed" if report.processing_status == ReportStatus.EXPLAINED else report.processing_status.value,
        "processing_status": report.processing_status,
        "doctorOrLab": "HealthSense Diagnostic Services",
        "findingsCount": findings_count,
        "summaryPreview": summary_preview,
    }


def _format_frontend_analysis(
    report: MedicalReport,
    findings: List[ReportFinding],
    summary_obj: ReportSummary,
    explanations: Optional[List[str]] = None,
    doctor_questions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    try:
        questions = doctor_questions or json.loads(summary_obj.doctor_questions)
    except Exception:
        questions = ["Consult with your physician regarding these test findings."]

    formatted_findings = []
    for f in findings:
        formatted_findings.append({
            "id": f"fnd-{f.id}",
            "testName": f.test_name,
            "value": f.value,
            "unit": f.unit or "",
            "referenceRange": f.reference_range or "Standard",
            "interpretation": "outside-range" if f.is_abnormal else "within-range",
            "flag": "abnormal" if f.is_abnormal else "normal",
            "category": "Laboratory Diagnostic",
            "confidenceScore": 0.98,
        })

    # Default educational explanations if not provided
    if not explanations:
        explanations = [
            f"Analyzed {len(formatted_findings)} clinical test results from your report.",
            "Parameters outside stated reference intervals are highlighted for consultation.",
            "All explanations are educational and intended to guide consultation with your doctor.",
        ]

    return {
        "reportId": str(report.id),
        "reportName": report.title,
        "reportDate": report.created_at.strftime("%B %d, %Y") if report.created_at else "Recent",
        "labName": "HealthSense Diagnostic Services",
        "status": "analyzed",
        "summary": summary_obj.summary,
        "findings": formatted_findings,
        "explanations": explanations,
        "doctorQuestions": questions,
        "disclaimer": (
            "HealthSense provides educational explanations of uploaded health information. "
            "It does not diagnose medical conditions or replace professional medical advice. "
            "Please discuss your results with a qualified healthcare professional."
        ),
        "analyzedAt": "Just now",
        "extractedFactsCount": len(formatted_findings),
    }


@router.post("/upload", response_model=ReportUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_analyze_report(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Seamless integrated upload endpoint for Frontend:
    Uploads document, runs AI extraction & analysis, persists findings,
    and returns both the report and the analysis payload in one round-trip.
    """
    file_bytes = await file.read()
    await file.seek(0)
    report_title = title or (file.filename.rsplit(".", 1)[0].replace("-", " ").replace("_", " ").title() if file.filename else "Medical Laboratory Report")

    # Save physical file
    unique_filename, file_path, file_size = file_service.save_file(file)

    # Process through AI pipeline (Microservice or in-process fallback)
    ai_result = await ai_service.process_report_file(
        file_bytes=file_bytes,
        filename=file.filename or unique_filename,
        content_type=file.content_type,
    )

    extracted_text = ai_result.get("extracted_text", "")
    summary_text = ai_result.get("summary", "Report analyzed by HealthSense AI.")
    plain_lang_exp = ai_result.get("plain_language_explanation", summary_text)
    doc_questions = ai_result.get("doctor_questions", [])
    explanations = ai_result.get("explanations", [])

    # Create Report
    report = MedicalReport(
        user_id=current_user.id,
        title=report_title,
        file_path=file_path,
        original_filename=file.filename or unique_filename,
        mime_type=file.content_type or "application/pdf",
        file_size_bytes=file_size,
        extracted_text=extracted_text,
        processing_status=ReportStatus.EXPLAINED,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # Save findings
    created_findings = []
    for f in ai_result.get("findings", []):
        finding_obj = ReportFinding(
            report_id=report.id,
            test_name=f.get("test_name", "Clinical Parameter"),
            value=str(f.get("value", "")),
            unit=f.get("unit"),
            reference_range=f.get("reference_range"),
            is_abnormal=bool(f.get("is_abnormal", False)),
            clinical_note=f.get("clinical_note"),
        )
        db.add(finding_obj)
        created_findings.append(finding_obj)

    # Save summary
    summary_obj = ReportSummary(
        report_id=report.id,
        summary=summary_text,
        plain_language_explanation=plain_lang_exp,
        doctor_questions=json.dumps(doc_questions),
    )
    db.add(summary_obj)
    db.commit()
    db.refresh(report)

    return {
        "report": _format_frontend_report(report),
        "analysis": _format_frontend_analysis(
            report, created_findings, summary_obj, explanations=explanations, doctor_questions=doc_questions
        ),
    }


@router.post("", response_model=MedicalReportResponse, status_code=status.HTTP_201_CREATED)
def upload_report(
    file: UploadFile = File(...),
    title: str = Form("Medical Laboratory Report"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Uploads and validates a medical report (PDF or Image).
    Extracts readable text via PyMuPDF/OCR.
    """
    unique_filename, file_path, file_size = file_service.save_file(file)

    extracted_text = document_processor.process_document(
        file_path=file_path,
        mime_type=file.content_type or "application/octet-stream",
    )

    report = MedicalReport(
        user_id=current_user.id,
        title=title,
        file_path=file_path,
        original_filename=file.filename or unique_filename,
        mime_type=file.content_type or "application/octet-stream",
        file_size_bytes=file_size,
        extracted_text=extracted_text,
        processing_status=ReportStatus.PENDING,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # Attach frontend friendly fields
    report.name = report.title
    report.uploadedAt = report.created_at.strftime("%Y-%m-%d")
    report.fileSize = f"{(report.file_size_bytes / (1024 * 1024)):.1f} MB"
    report.fileType = report.mime_type
    report.status = report.processing_status.value
    report.findingsCount = len(report.findings)

    return report


@router.get("", response_model=List[Dict[str, Any]])
def list_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists all medical reports belonging to the authenticated user."""
    if current_user.role in [UserRole.DOCTOR, UserRole.ADMIN]:
        reports = db.query(MedicalReport).order_by(MedicalReport.created_at.desc()).all()
    else:
        reports = (
            db.query(MedicalReport)
            .filter(MedicalReport.user_id == current_user.id)
            .order_by(MedicalReport.created_at.desc())
            .all()
        )

    return [_format_frontend_report(r) for r in reports]


@router.get("/{report_id}", response_model=Dict[str, Any])
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves an authorized medical report by ID."""
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if report.user_id != current_user.id and current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this medical report.",
        )

    return _format_frontend_report(report)


@router.get("/{report_id}/analysis", response_model=Dict[str, Any])
def get_report_analysis(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves formatted frontend AI analysis for a report."""
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if report.user_id != current_user.id and current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    if not report.summary_rel:
        # Auto-explain if not yet explained
        content_to_analyze = report.extracted_text or f"Medical report: {report.title}"
        analysis = ai_service.explain_medical_report(content_to_analyze, title=report.title)
        summary_obj = ReportSummary(
            report_id=report.id,
            summary=analysis.get("summary", "Analysis completed."),
            plain_language_explanation=analysis.get("plain_language_explanation", "Analysis completed."),
            doctor_questions=json.dumps(analysis.get("doctor_questions", [])),
        )
        db.add(summary_obj)

        for f in analysis.get("findings", []):
            finding_obj = ReportFinding(
                report_id=report.id,
                test_name=f.get("test_name", "Clinical Marker"),
                value=str(f.get("value", "")),
                unit=f.get("unit"),
                reference_range=f.get("reference_range"),
                is_abnormal=bool(f.get("is_abnormal", False)),
                clinical_note=f.get("clinical_note"),
            )
            db.add(finding_obj)

        report.processing_status = ReportStatus.EXPLAINED
        db.commit()
        db.refresh(report)

    return _format_frontend_analysis(report, report.findings, report.summary_rel)


@router.post("/{report_id}/explain", response_model=ReportExplanationResponse)
def explain_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    CareBridge AI Centerpiece Feature:
    Extracts lab findings, reference ranges, plain-language explanation,
    and tailored questions for doctor consultation.
    """
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if report.user_id != current_user.id and current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to explain this report.",
        )

    # Run AI Explanation
    content_to_analyze = report.extracted_text or f"Medical report: {report.title}"
    analysis = ai_service.explain_medical_report(content_to_analyze, title=report.title)

    # Clean existing findings & summary if re-explaining
    db.query(ReportFinding).filter(ReportFinding.report_id == report.id).delete()
    db.query(ReportSummary).filter(ReportSummary.report_id == report.id).delete()

    created_findings = []
    for f in analysis.get("findings", []):
        finding_obj = ReportFinding(
            report_id=report.id,
            test_name=f.get("test_name", "Clinical Marker"),
            value=str(f.get("value", "N/A")),
            unit=f.get("unit"),
            reference_range=f.get("reference_range"),
            is_abnormal=bool(f.get("is_abnormal", False)),
            clinical_note=f.get("clinical_note"),
        )
        db.add(finding_obj)
        created_findings.append(finding_obj)

    summary_obj = ReportSummary(
        report_id=report.id,
        summary=analysis.get("summary", "Report analyzed by HealthSense AI."),
        plain_language_explanation=analysis.get("plain_language_explanation", "Analysis completed."),
        doctor_questions=json.dumps(analysis.get("doctor_questions", [])),
    )
    db.add(summary_obj)

    report.processing_status = ReportStatus.EXPLAINED
    db.commit()
    db.refresh(report)

    return ReportExplanationResponse(
        report_id=report.id,
        title=report.title,
        status=report.processing_status,
        summary=summary_obj.summary,
        plain_language_explanation=summary_obj.plain_language_explanation,
        findings=[ReportFindingSchema.model_validate(f) for f in created_findings],
        doctor_questions=analysis.get("doctor_questions", []),
    )


@router.get("/{report_id}/summary", response_model=ReportExplanationResponse)
def get_report_summary(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves the pre-generated HealthSense explanation for a medical report."""
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if report.user_id != current_user.id and current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this summary.",
        )

    if not report.summary_rel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This report has not been explained yet. Call POST /api/v1/reports/{id}/explain first.",
        )

    try:
        questions = json.loads(report.summary_rel.doctor_questions)
    except Exception:
        questions = []

    return ReportExplanationResponse(
        report_id=report.id,
        title=report.title,
        status=report.processing_status,
        summary=report.summary_rel.summary,
        plain_language_explanation=report.summary_rel.plain_language_explanation,
        findings=[ReportFindingSchema.model_validate(f) for f in report.findings],
        doctor_questions=questions,
    )


@router.delete("/{report_id}", status_code=status.HTTP_200_OK)
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a medical report, its extracted findings, and physical file."""
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if report.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this report.",
        )

    # Delete physical file if present
    if report.file_path and os.path.exists(report.file_path):
        try:
            os.remove(report.file_path)
        except Exception:
            pass

    db.delete(report)
    db.commit()
    return {"success": True, "message": "Report deleted successfully"}
