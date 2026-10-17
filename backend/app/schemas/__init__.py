from app.schemas.token import Token, TokenPayload
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from app.schemas.document import DocumentResponse, DocumentUpdate, DocumentAnalysisResponse
from app.schemas.ai import SymptomCheckRequest, SymptomCheckResponse, AIInteractionHistoryResponse
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate

__all__ = [
    "Token",
    "TokenPayload",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "DocumentResponse",
    "DocumentUpdate",
    "DocumentAnalysisResponse",
    "SymptomCheckRequest",
    "SymptomCheckResponse",
    "AIInteractionHistoryResponse",
    "AppointmentCreate",
    "AppointmentResponse",
    "AppointmentUpdate",
]
