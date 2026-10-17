from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Verifies API health and database connectivity."""
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_status,
        "ai_engine": "Gemini 1.5 Flash (Active)" if settings.GEMINI_API_KEY else "Heuristic Engine (Mock Mode)",
    }
