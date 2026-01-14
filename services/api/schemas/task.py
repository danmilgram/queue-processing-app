from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class TaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    priority: Literal["low", "medium", "high"]
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    task_id: str
