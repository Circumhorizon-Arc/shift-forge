from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from app.database import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = Column(String(200), nullable=False)
    description: Mapped[Optional[str]] = Column(String(500), nullable=True)
    due_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    is_completed: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    completed_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", backref="reminders")
