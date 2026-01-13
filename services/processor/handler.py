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
    task_id = task.get("task_id")
    if not task_id:
        raise ValueError("Missing task_id")

    title = task["title"]
    priority = task["priority"]

    logger.info(
        f"Processing {priority} priority task",
        extra={
            "task_id": task_id,
            "priority": priority,
            "title": title,
        },
    )


def handle(event: Dict[str, Any], context: Any) -> None:
    """
    Lambda entrypoint for SQS FIFO processing.
    """
    # TODO: Add idempotency check (DB lookup) to prevent duplicate processing beyond SQS 5min window
    for record in event.get("Records", []):
        try:
            task = json.loads(record["body"])
            process_task(task)
        except Exception:
            logger.exception("Task processing failed, triggering retry")
            raise  # REQUIRED for SQS retry / DLQ
