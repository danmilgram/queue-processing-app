"""POST /tasks Endpoint Tests"""

import json
import uuid

# ==============================================================================
# INPUT VALIDATION TESTS
# ==============================================================================


def test_valid_payload_returns_201(client, valid_payload):
    """Valid payload should return 201 Created"""
    response = client.post("/tasks", json=valid_payload)

    assert response.status_code == 201
    assert "task_id" in response.json()


def test_missing_title_returns_422(client, valid_payload):
    """Missing title should return 422"""
    payload = valid_payload.copy()
    del payload["title"]

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422


def test_invalid_priority_returns_422(client, valid_payload):
    """Invalid priority should return 422"""
    payload = valid_payload.copy()
    payload["priority"] = "urgent"

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422


def test_invalid_due_date_format_returns_422(client, valid_payload):
    """Invalid due_date format should return 422"""
    payload = valid_payload.copy()
    payload["due_date"] = "not-a-date"

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422


def test_due_date_in_past_returns_422(client, valid_payload):
    """due_date in the past should return 422"""
    payload = valid_payload.copy()
    payload["due_date"] = "2020-01-01T00:00:00Z"

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422


# ==============================================================================
# TASK ID GENERATION TESTS
# ==============================================================================


def test_task_id_is_valid_uuid(client, valid_payload, mock_sqs):
    """Task ID should be a valid UUID"""
    response = client.post("/tasks", json=valid_payload)

    assert response.status_code == 201
    task_id = response.json()["task_id"]

    # Should not raise ValueError
    uuid.UUID(task_id)


def test_task_id_is_unique(client, valid_payload, mock_sqs):
    """Each request should generate a unique task ID"""
    response1 = client.post("/tasks", json=valid_payload)
    response2 = client.post("/tasks", json=valid_payload)

    task_id_1 = response1.json()["task_id"]
    task_id_2 = response2.json()["task_id"]

    assert task_id_1 != task_id_2


# ==============================================================================
# SQS INTEGRATION TESTS (with mocked AWS)
# ==============================================================================


def test_sqs_enqueue_behavior(mock_sqs, client, valid_payload):
    """
    Test complete SQS enqueue behavior with valid payload.

    Validates:
    - send_message is called exactly once
    - MessageGroupId="tasks" for FIFO ordering
    - MessageDeduplicationId matches task_id for idempotency
    - Message body contains all task data
    - task_id is consistent across response and message
    """
    response = client.post("/tasks", json=valid_payload)

    # Verify HTTP response
    assert response.status_code == 201
    task_id = response.json()["task_id"]

    # Verify SQS send_message was called exactly once
    mock_sqs.send_message.assert_called_once()
    call_args = mock_sqs.send_message.call_args

    # Verify FIFO configuration
    assert call_args.kwargs["MessageGroupId"] == "tasks"

    # Verify deduplication strategy (at-least-once delivery)
    dedup_id = call_args.kwargs["MessageDeduplicationId"]
    assert dedup_id == task_id

    # Verify message payload
    message_body = json.loads(call_args.kwargs["MessageBody"])
    assert message_body["task_id"] == task_id
    assert message_body["title"] == valid_payload["title"]
    assert message_body["description"] == valid_payload["description"]
    assert message_body["priority"] == valid_payload["priority"]


def test_sqs_failure_returns_500(mock_sqs, client, valid_payload):
    """
    Test SQS failure handling.

    When SQS is unavailable, the API should:
    - Return HTTP 500 (not 2xx)
    - Provide meaningful error message
    - Not leak internal exception details
    """
    mock_sqs.send_message.side_effect = Exception("SQS down")

    response = client.post("/tasks", json=valid_payload)

    assert response.status_code == 500
    assert "Failed to enqueue task" in response.json()["detail"]
