from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field, validator


class TaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    priority: Literal["low", "medium", "high"]
    due_date: Optional[datetime] = None

    @validator("due_date")
    def due_date_must_be_future(cls, v):
        if v is not None:
            # Make comparison timezone-aware
            now = datetime.now(timezone.utc)
            # If v is naive, make it UTC aware
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            if v < now:
                raise ValueError("due_date must be in the future")
        return v


class TaskResponse(BaseModel):
    task_id: str
