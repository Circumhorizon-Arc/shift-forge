from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, AliasChoices


class ReminderCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    dueText: Optional[str] = None
    category: Optional[str] = "general"
    priority: Optional[str] = "medium"

    model_config = ConfigDict(populate_by_name=True)


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    is_completed: Optional[bool] = None
    completed: Optional[bool] = None


class ReminderCompleteRequest(BaseModel):
    completed: Optional[bool] = True
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

    # Frontend compatibility fields
    completed: Optional[bool] = None
    dueText: Optional[str] = None
    category: Optional[str] = "general"
    priority: Optional[str] = "medium"

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
