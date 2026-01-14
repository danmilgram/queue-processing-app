import json
import logging
from typing import Any, Dict

from .base import QueueProvider

logger = logging.getLogger(__name__)


class TaskQueueService:
    """Service for managing task queue operations"""

    def __init__(self, provider: QueueProvider):
        """
        Initialize the queue service with a specific provider.

        Args:
            provider: Queue provider implementation
        """
        self.provider = provider

    def enqueue_task(self, task_data: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """
        Enqueue a task to the queue.

        Args:
            task_data: Task payload dictionary
            task_id: Unique task identifier

        Returns:
            dict: Response from the queue provider
        """
        message_body = json.dumps(task_data)

        response = self.provider.send_message(message_body=message_body, task_id=task_id)

        logger.info("Task enqueued", extra={"task_id": task_id})
        return response
