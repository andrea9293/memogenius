# app/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime

class ReminderBase(BaseModel):
    text: str = Field(..., description="Reminder text")
    due_date: datetime = Field(..., description="Reminder date and time")

class ReminderCreate(ReminderBase):
    user_id: int = Field(..., description="Telegram user ID")

class ReminderUpdate(ReminderBase):
    is_active: bool = True

class Reminder(ReminderBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
