import json
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.ai_log import AIInteraction
from app.schemas.ai import (
    SymptomCheckRequest,
    SymptomCheckResponse,
    AIInteractionHistoryResponse,
)
from app.core.dependencies import get_current_user
from app.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["AI Clinical Guidance"])


@router.post("/symptom-check", response_model=SymptomCheckResponse, status_code=status.HTTP_200_OK)
def check_symptoms(
    payload: SymptomCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyzes patient symptoms and provides clinical triage guidance,
    urgency level, suggested specialist, and recommended next steps.
    """
    triage_result = ai_service.symptom_triage(
        query=payload.query,
        duration=payload.duration,
        age=payload.age,
        gender=payload.gender,
        existing_conditions=payload.existing_conditions,
    )

    # Persist the interaction for patient history & doctor review
    ai_log = AIInteraction(
        user_id=current_user.id,
        user_query=payload.query,
        symptoms=payload.duration or "",
        triage_level=triage_result["triage_level"],
        possible_conditions=json.dumps(triage_result["possible_conditions"]),
        recommendations=triage_result["recommendations"],
        suggested_specialist=triage_result["suggested_specialist"],
        raw_ai_response=json.dumps(triage_result),
    )
    db.add(ai_log)
    db.commit()
    db.refresh(ai_log)

    return SymptomCheckResponse(
        id=ai_log.id,
        triage_level=triage_result["triage_level"],
        triage_color=triage_result["triage_color"],
        possible_conditions=triage_result["possible_conditions"],
        recommendations=triage_result["recommendations"],
        suggested_specialist=triage_result["suggested_specialist"],
        urgency_message=triage_result["urgency_message"],
        created_at=ai_log.created_at,
    )


@router.get("/history", response_model=List[AIInteractionHistoryResponse])
def get_ai_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves the current user's past AI symptom assessments."""
    logs = (
        db.query(AIInteraction)
        .filter(AIInteraction.user_id == current_user.id)
        .order_by(AIInteraction.created_at.desc())
        .limit(50)
        .all()
    )
    return logs
