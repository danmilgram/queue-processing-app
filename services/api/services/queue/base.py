from abc import ABC, abstractmethod
from typing import Any, Dict


class QueueProvider(ABC):
    """Base class for all queue providers"""

    @abstractmethod
    def send_message(self, message_body: str, task_id: str, **kwargs) -> Dict[str, Any]:
        """
        Send a message to the queue.

        Args:
            message_body: The message payload as JSON string
            task_id: Unique task identifier for deduplication
            **kwargs: Additional provider-specific parameters

        Returns:
            dict: Response from the queue provider
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of this queue provider"""
        pass
