"""E2E test fixtures for API → SQS → Processor integration."""

import os
import boto3
import pytest
from moto import mock_sqs


@pytest.fixture(scope="session")
def aws_credentials():
    """Mock AWS credentials for moto."""
    os.environ.update(
        {
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_SECURITY_TOKEN": "testing",
            "AWS_SESSION_TOKEN": "testing",
            "AWS_DEFAULT_REGION": "us-east-1",
        }
    )
    yield
    for key in list(os.environ.keys()):
        if key.startswith("AWS_"):
            os.environ.pop(key, None)


@pytest.fixture
def sqs_fifo_queue(aws_credentials):
    """Create a FIFO SQS queue using moto."""
    with mock_sqs():
        sqs = boto3.client("sqs", region_name="us-east-1")

        response = sqs.create_queue(
            QueueName="task-queue.fifo",
            Attributes={
                "FifoQueue": "true",
                "ContentBasedDeduplication": "false",
                "MessageRetentionPeriod": "86400",
                "VisibilityTimeout": "30",
            },
        )

        queue_url = response["QueueUrl"]
        os.environ["QUEUE_URL"] = queue_url

        yield sqs, queue_url

        os.environ.pop("QUEUE_URL", None)


@pytest.fixture
def api_client(sqs_fifo_queue):
    """FastAPI test client with real SQS queue."""
    from services.api.app import app
    from fastapi.testclient import TestClient

    return TestClient(app)


@pytest.fixture
def processor_handler(sqs_fifo_queue):
    """Processor Lambda handler with real SQS queue."""
    from services.processor.handler import handle

    return handle


@pytest.fixture
def sample_task_payload():
    """Sample task payload for testing."""
    return {
        "title": "E2E Test Task",
        "description": "Testing full flow from API to processor",
        "priority": "high",
    }
