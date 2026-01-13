import boto3
import os
import logging
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
from uuid import uuid4

from mangum import Mangum

logger = logging.getLogger()
logger.setLevel(logging.INFO)

QUEUE_URL = os.environ.get("QUEUE_URL")
if not QUEUE_URL:
    raise RuntimeError("QUEUE_URL environment variable is not set")

sqs = boto3.client("sqs")

app = FastAPI(title="Task Management API")

class TaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    priority: Literal["low", "medium", "high"]
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    task_id: str


@app.post("/tasks", status_code=201, response_model=TaskResponse)
def create_task(task: TaskRequest) -> TaskResponse:
    task_id = str(uuid4())

    payload = {
        "task_id": task_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
    }

    message_body = json.dumps(payload)

    # TODO: consider storing message in DB before sending to ensure no loss on API crash
    try:
        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=message_body,
            MessageGroupId="tasks",  # global ordering
            MessageDeduplicationId=task_id,
        )
        if "MessageId" not in response:
            raise RuntimeError("SQS enqueue failed")

    except Exception as exc:
        logger.exception("Failed to send message to SQS")
        raise HTTPException(status_code=500, detail="Failed to enqueue task") from exc

    logger.info("Task enqueued", extra={"task_id": task_id})

    return TaskResponse(task_id=task_id)


# Lambda entrypoint
handler = Mangum(app)
