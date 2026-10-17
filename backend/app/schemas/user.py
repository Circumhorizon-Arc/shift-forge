from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=150)
    role: UserRole = UserRole.PATIENT
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
