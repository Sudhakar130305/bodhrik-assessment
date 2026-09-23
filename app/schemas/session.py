from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionCreate(BaseModel):
    title: str
    teacher_id: int
    child_id: int
    scheduled_at: datetime


class SessionUpdate(BaseModel):
    title: str | None = None
    teacher_id: int | None = None
    child_id: int | None = None
    scheduled_at: datetime | None = None


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    teacher_id: int
    child_id: int
    scheduled_at: datetime
    created_at: datetime
    updated_at: datetime