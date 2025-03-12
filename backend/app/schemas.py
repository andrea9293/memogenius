# app/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime

class ChatMessage(BaseModel):
    message: str
    user_id: int | None = None

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
        
class UserBase(BaseModel):
    access_key: str

class UserCreate(UserBase):
    telegram_id: int | None = None
    web_token: str | None = None

class User(UserBase):
    id: int
    telegram_id: int | None
    web_token: str | None
    created_at: datetime

    class Config:
        from_attributes = True
        
class ListItemBase(BaseModel):
    text: str = Field(..., description="Item text")
    completed: bool = Field(False, description="Whether the item is completed")

class ListItemCreate(ListItemBase):
    list_id: int = Field(..., description="ID of the list this item belongs to")

class ListItemUpdate(BaseModel):
    text: str | None = Field(None, description="New item text")
    completed: bool | None = Field(None, description="New completion status")

class ListItem(ListItemBase):
    id: int
    list_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

class ListBase(BaseModel):
    title: str = Field(..., description="List title")
    type: str = Field(..., description="List type: 'todo' or 'shopping'")

class ListCreate(ListBase):
    user_id: int = Field(..., description="User ID")

class List(ListBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

class ListWithItems(List):
    items: list[ListItem] = []

    class Config:
        from_attributes = True