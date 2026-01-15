import json
import logging
from typing import Any, Dict

from services.processor.services.task_processor import TaskProcessor

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handle(event: Dict[str, Any], context: Any) -> None:
    """
    Lambda entrypoint for SQS FIFO processing.
    """
    # TODO: Add idempotency check (DB lookup)
    # to prevent duplicate processing beyond SQS 5min window
    for record in event.get("Records", []):
        try:
            task = json.loads(record["body"])
            TaskProcessor.process(task)
        except Exception:
            logger.exception("Task processing failed, triggering retry")
            raise  # REQUIRED for SQS retry / DLQ
