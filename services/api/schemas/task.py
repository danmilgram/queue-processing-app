from pydantic import BaseModel, Field, validator
from typing import Literal, Optional
from datetime import datetime


class TaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    priority: Literal["low", "medium", "high"]
    due_date: Optional[datetime] = None

    @validator('due_date')
    def due_date_must_be_future(cls, v):
        if v is not None and v < datetime.now():
            raise ValueError('due_date must be in the future')
        return v


class TaskResponse(BaseModel):
    task_id: str
