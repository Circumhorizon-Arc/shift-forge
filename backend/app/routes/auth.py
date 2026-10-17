from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, UserLogin, UserUpdate
from app.schemas.token import Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user (patient or doctor) and returns authenticated profile."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        phone=user_in.phone,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(subject=user.id, role=user.role.value, expires_delta=expires_delta)

    user_dict = {
        "id": str(user.id),
        "fullName": user.full_name,
        "email": user.email,
        "role": user.role.value,
        "phone": user.phone or "",
        "dateOfBirth": user_in.date_of_birth or "",
        "createdAt": user.created_at.isoformat() if hasattr(user, "created_at") else "",
    }

    user_resp = UserResponse.model_validate(user)
    user_resp.token = token
    user_resp.access_token = token
    user_resp.fullName = user.full_name
    user_resp.user = user_dict
    return user_resp


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user with JSON credentials and returns a JWT token with user object."""
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(subject=user.id, role=user.role.value, expires_delta=expires_delta)

    user_dict = {
        "id": str(user.id),
        "fullName": user.full_name,
        "email": user.email,
        "role": user.role.value,
        "phone": user.phone or "",
        "dateOfBirth": "",
        "createdAt": user.created_at.isoformat() if hasattr(user, "created_at") else "",
    }

    return Token(
        access_token=token,
        token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        email=user.email,
        role=user.role.value,
        full_name=user.full_name,
        user=user_dict,
    )


@router.post("/token", response_model=Token, include_in_schema=False)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 compatible token login for Swagger UI authorization button."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(subject=user.id, role=user.role.value, expires_delta=expires_delta)
    user_dict = {
        "id": str(user.id),
        "fullName": user.full_name,
        "email": user.email,
        "role": user.role.value,
        "phone": user.phone or "",
        "dateOfBirth": "",
        "createdAt": user.created_at.isoformat() if hasattr(user, "created_at") else "",
    }
    return Token(
        access_token=token,
        token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        email=user.email,
        role=user.role.value,
        full_name=user.full_name,
        user=user_dict,
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns profile information for the authenticated user."""
    user_resp = UserResponse.model_validate(current_user)
    user_resp.fullName = current_user.full_name
    user_resp.user = {
        "id": str(current_user.id),
        "fullName": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role.value,
        "phone": current_user.phone or "",
        "dateOfBirth": "",
        "createdAt": current_user.created_at.isoformat() if hasattr(current_user, "created_at") else "",
    }
    return user_resp


@router.put("/profile", response_model=UserResponse)
def update_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates the authenticated user's profile."""
    if updates.full_name is not None:
        current_user.full_name = updates.full_name
    if updates.phone is not None:
        current_user.phone = updates.phone
    if updates.is_active is not None:
        current_user.is_active = updates.is_active

    db.commit()
    db.refresh(current_user)

    user_resp = UserResponse.model_validate(current_user)
    user_resp.fullName = current_user.full_name
    user_resp.user = {
        "id": str(current_user.id),
        "fullName": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role.value,
        "phone": current_user.phone or "",
        "dateOfBirth": updates.date_of_birth or "",
        "createdAt": current_user.created_at.isoformat() if hasattr(current_user, "created_at") else "",
    }
    return user_resp
