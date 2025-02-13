# app/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime

class ReminderBase(BaseModel):
    text: str = Field(..., description="Testo del promemoria")
    due_date: datetime = Field(..., description="Data e ora del promemoria")

class ReminderCreate(ReminderBase):
    user_id: int = Field(..., description="ID dell'utente Telegram") #per il momento lo chiede, poi sarà automatico

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
