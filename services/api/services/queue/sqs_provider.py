import os
import boto3
from botocore.config import Config
from typing import Any, Dict
from .base import QueueProvider


class SQSQueueProvider(QueueProvider):
    """AWS SQS queue provider"""

    def __init__(self):
        """Initialize SQS client with retry configuration"""
        self.queue_url = os.environ.get("QUEUE_URL")
        if not self.queue_url:
            raise RuntimeError("QUEUE_URL environment variable is not set")

        # Configure boto3 with automatic retries for transient failures
        retry_config = Config(
            retries={
                'max_attempts': 5,  # Total attempts (1 initial + 4 retries)
                'mode': 'standard'  # Exponential backoff with jitter
            }
        )
        self.client = boto3.client("sqs", config=retry_config)

    def send_message(self, message_body: str, task_id: str, **kwargs) -> Dict[str, Any]:
        """
        Send a message to SQS FIFO queue.

        Args:
            message_body: JSON string payload
            task_id: Task ID for deduplication
            **kwargs: Additional SQS parameters

        Returns:
            dict: SQS response
        """
        # TODO: For complete durability, store in DB before sending (protects against API crash before SQS ack)
        response = self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=message_body,
            MessageGroupId="tasks",  # global ordering
            MessageDeduplicationId=task_id,
        )
        return response

    def get_provider_name(self) -> str:
        return "sqs"
