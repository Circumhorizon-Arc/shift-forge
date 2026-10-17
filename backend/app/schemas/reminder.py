from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ReminderCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    due_at: datetime


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    is_completed: Optional[bool] = None


class ReminderResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    due_at: datetime
    is_completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
