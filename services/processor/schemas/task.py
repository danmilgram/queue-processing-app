from typing import Literal, Optional

from pydantic import BaseModel, Field


class TaskPayload(BaseModel):
    task_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    priority: Literal["low", "medium", "high"]
    due_date: Optional[str] = None
