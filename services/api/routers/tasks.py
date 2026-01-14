import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from schemas.task import TaskRequest, TaskResponse
from services.queue.queue_service import TaskQueueService
from services.queue.sqs_provider import SQSQueueProvider

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Tasks"])


@router.post("/tasks", status_code=201, response_model=TaskResponse)
def create_task(task: TaskRequest) -> TaskResponse:
    task_id = str(uuid4())

    payload = {
        "task_id": task_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
    }

    try:
        # Initialize queue service with SQS provider
        queue_provider = SQSQueueProvider()
        queue_service = TaskQueueService(provider=queue_provider)

        queue_service.enqueue_task(task_data=payload, task_id=task_id)
    except Exception as exc:
        logger.exception("Failed to send message to SQS")
        raise HTTPException(status_code=500, detail="Failed to enqueue task") from exc

    return TaskResponse(task_id=task_id)
