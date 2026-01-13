import json
import logging
from typing import Any, Dict

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def process_task(task: Dict[str, Any]) -> None:
    """
    Process a single task.

    This function is intentionally idempotent:
    - No external side effects
    - Safe to retry
    """
    task_id = task["task_id"]
    title = task["title"]
    priority = task["priority"]

    logger.info(
        "Processing task",
        extra={
            "task_id": task_id,
            "priority": priority,
            "title": title,
        },
    )

    # Example real logic (deterministic & repeat-safe)
    if priority == "high":
        logger.info("High priority task handled", extra={"task_id": task_id})

    elif priority == "medium":
        logger.info("Medium priority task handled", extra={"task_id": task_id})

    else:
        logger.info("Low priority task handled", extra={"task_id": task_id})

    # Simulate validation failure → retry + DLQ
    if not title.strip():
        raise ValueError("Task title cannot be empty")

    logger.info("Task processed successfully", extra={"task_id": task_id})


def handle(event: Dict[str, Any], context: Any) -> None:
    """
    Lambda entrypoint for SQS FIFO processing.
    """
    for record in event.get("Records", []):
        try:
            task = json.loads(record["body"])
            process_task(task)
        except Exception:
            logger.exception("Task processing failed, triggering retry")
            raise  # REQUIRED for SQS retry / DLQ
