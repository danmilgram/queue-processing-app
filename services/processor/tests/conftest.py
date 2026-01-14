import json

import pytest


@pytest.fixture
def valid_task():
    """Valid task payload"""
    return {
        "task_id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Test Task",
        "description": "Test Description",
        "priority": "high",
        "due_date": None,
    }


@pytest.fixture
def sqs_event(valid_task):
    """SQS event with single record"""
    return {
        "Records": [
            {
                "body": json.dumps(valid_task),
                "messageId": "test-message-id",
            }
        ]
    }


@pytest.fixture
def multiple_records_event():
    """SQS event with multiple records"""
    return {
        "Records": [
            {
                "body": json.dumps(
                    {
                        "task_id": "1",
                        "title": "Task 1",
                        "description": "First",
                        "priority": "low",
                    }
                )
            },
            {
                "body": json.dumps(
                    {
                        "task_id": "2",
                        "title": "Task 2",
                        "description": "Second",
                        "priority": "medium",
                    }
                )
            },
        ]
    }
