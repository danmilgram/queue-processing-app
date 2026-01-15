import logging
from typing import Any, Dict

from services.processor.schemas.task import TaskPayload

logger = logging.getLogger(__name__)


class TaskProcessor:
    """Service for processing tasks"""

    @staticmethod
    def process(task: Dict[str, Any]) -> None:
        """
        Process a single task.

        This function is intentionally idempotent:
        - No external side effects
        - Safe to retry
        """
        # Validate task payload
        validated_task = TaskPayload(**task)

        logger.info(
            f"Processing {validated_task.priority} priority task",
            extra={
                "task_id": validated_task.task_id,
                "priority": validated_task.priority,
                "title": validated_task.title,
            },
        )
