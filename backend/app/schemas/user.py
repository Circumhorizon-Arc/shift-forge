from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, AliasChoices
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=150, validation_alias=AliasChoices("full_name", "fullName"))
    role: UserRole = UserRole.PATIENT
    phone: Optional[str] = None
    date_of_birth: Optional[str] = Field(None, validation_alias=AliasChoices("date_of_birth", "dateOfBirth"))


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    token: Optional[str] = None
    access_token: Optional[str] = None
    fullName: Optional[str] = None
    user: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, validation_alias=AliasChoices("full_name", "fullName"))
    phone: Optional[str] = None
    date_of_birth: Optional[str] = Field(None, validation_alias=AliasChoices("date_of_birth", "dateOfBirth"))
    is_active: Optional[bool] = None

