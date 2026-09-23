from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    status: str
    result: str | None
    created_at: datetime
    updated_at: datetime