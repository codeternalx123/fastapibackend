from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, time
from uuid import UUID


class ReminderBase(BaseModel):
    title: str
    description: Optional[str] = None
    reminder_type: str = Field(regex='^(meal|medication|hydration)$')
    frequency: str = Field(regex='^(daily|weekly|monthly)$')
    scheduled_time: time
    days_of_week: List[int] = Field(default_factory=list)
    is_active: bool = True


class ReminderCreate(ReminderBase):
    pass


class Reminder(ReminderBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True