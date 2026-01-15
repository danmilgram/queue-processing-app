import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_env():
    """Mock environment variables"""
    with patch.dict(os.environ, {"QUEUE_URL": "http://test-queue-url"}):
        yield


@pytest.fixture
def mock_sqs():
    """Mock SQS client"""
    with patch("services.api.services.queue.sqs_provider.boto3.client") as mock:
        sqs_mock = MagicMock()
        sqs_mock.send_message.return_value = {"MessageId": "test-message-id"}
        mock.return_value = sqs_mock
        yield sqs_mock


@pytest.fixture
def client(mock_env, mock_sqs):
    """FastAPI test client with mocked SQS and environment"""
    from services.api.app import app

    return TestClient(app)


@pytest.fixture
def valid_payload():
    """Valid task payload"""
    return {
        "title": "Test Task",
        "description": "Test Description",
        "priority": "low",
        "due_date": "2030-01-01T00:00:00Z",
    }
