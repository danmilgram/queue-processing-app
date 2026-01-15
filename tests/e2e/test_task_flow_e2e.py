"""
E2E tests for the complete task processing flow: API → SQS → Processor.

Uses moto to mock AWS SQS with real FIFO queue semantics.
"""

import json
from datetime import datetime, timedelta
from uuid import UUID


def test_task_creation_and_processing_success(
    api_client, processor_handler, sqs_fifo_queue, sample_task_payload
):
    """
    E2E test: POST /tasks → SQS → Processor → Success.

    Verifies:
    - API accepts valid task
    - Task is enqueued to SQS
    - Message has correct format
    - Processor can consume and process the message
    - Task ID is a valid UUID
    """
    sqs, queue_url = sqs_fifo_queue

    # POST task to API
    response = api_client.post("/tasks", json=sample_task_payload)

    assert response.status_code == 201
    response_data = response.json()
    assert "task_id" in response_data

    task_id = response_data["task_id"]
    UUID(task_id)  # Verify valid UUID

    # Receive message from SQS
    messages = sqs.receive_message(
        QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=1
    )

    assert "Messages" in messages
    assert len(messages["Messages"]) == 1

    message = messages["Messages"][0]
    message_body = json.loads(message["Body"])

    # Verify message contents
    assert message_body["task_id"] == task_id
    assert message_body["title"] == sample_task_payload["title"]
    assert message_body["description"] == sample_task_payload["description"]
    assert message_body["priority"] == sample_task_payload["priority"]

    # Process message with Lambda handler
    lambda_event = {"Records": [{"body": message["Body"]}]}
    processor_handler(lambda_event, None)  # Should not raise


def test_fifo_ordering_guarantee(api_client, processor_handler, sqs_fifo_queue):
    """
    E2E test: Verify FIFO ordering is maintained end-to-end.

    Verifies:
    - Multiple tasks submitted in order
    - SQS maintains order (FIFO guarantee)
    - Processor receives messages in submission order
    """
    sqs, queue_url = sqs_fifo_queue

    # Submit multiple tasks
    task_titles = ["First Task", "Second Task", "Third Task", "Fourth Task"]
    submitted_task_ids = []

    for title in task_titles:
        response = api_client.post(
            "/tasks",
            json={
                "title": title,
                "description": f"Description for {title}",
                "priority": "medium",
            },
        )
        assert response.status_code == 201
        submitted_task_ids.append(response.json()["task_id"])

    # Receive all messages
    messages = sqs.receive_message(
        QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=1
    )

    assert "Messages" in messages
    assert len(messages["Messages"]) == len(task_titles)

    # Extract titles and IDs in order received
    received_titles = []
    received_task_ids = []

    for message in messages["Messages"]:
        body = json.loads(message["Body"])
        received_titles.append(body["title"])
        received_task_ids.append(body["task_id"])

    # Verify ordering is preserved
    assert received_titles == task_titles
    assert received_task_ids == submitted_task_ids

    # Process all messages
    for message in messages["Messages"]:
        lambda_event = {"Records": [{"body": message["Body"]}]}
        processor_handler(lambda_event, None)


def test_deduplication_prevents_duplicate_tasks(api_client, sqs_fifo_queue):
    """
    E2E test: SQS deduplication prevents duplicate task processing.

    Verifies SQS accepts only one message with the same MessageDeduplicationId.
    """
    sqs, queue_url = sqs_fifo_queue

    # Create task payload with fixed task_id
    fixed_task_id = "550e8400-e29b-41d4-a716-446655440000"
    task_payload = {
        "task_id": fixed_task_id,
        "title": "Duplicate Test",
        "description": "Testing deduplication",
        "priority": "low",
    }

    message_body = json.dumps(task_payload)

    # Send same message twice (simulating retry)
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
        MessageGroupId="tasks",
        MessageDeduplicationId=fixed_task_id,
    )

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
        MessageGroupId="tasks",
        MessageDeduplicationId=fixed_task_id,
    )

    # Receive messages
    messages = sqs.receive_message(
        QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=1
    )

    # Verify only ONE message was enqueued (deduplication worked)
    assert "Messages" in messages
    assert len(messages["Messages"]) == 1

    received_body = json.loads(messages["Messages"][0]["Body"])
    assert received_body["task_id"] == fixed_task_id


def test_processor_handles_invalid_message(processor_handler, sqs_fifo_queue):
    """
    E2E test: Processor handles invalid message by raising exception.

    Verifies:
    - Invalid JSON in message
    - Processor raises exception (triggers SQS retry/DLQ)
    """
    sqs, queue_url = sqs_fifo_queue

    # Send invalid message
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody="invalid json{",
        MessageGroupId="tasks",
        MessageDeduplicationId="invalid-msg-123",
    )

    messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
    assert "Messages" in messages

    lambda_event = {"Records": [{"body": messages["Messages"][0]["Body"]}]}

    # Processor should raise exception
    try:
        processor_handler(lambda_event, None)
        assert False, "Expected processor to raise exception for invalid message"
    except json.JSONDecodeError:
        pass  # Expected


def test_processor_handles_missing_required_fields(processor_handler, sqs_fifo_queue):
    """
    E2E test: Processor validates required fields and raises exception.

    Verifies Pydantic validation catches missing fields.
    """
    sqs, queue_url = sqs_fifo_queue

    # Send message with missing task_id
    invalid_task = {
        "title": "Missing Task ID",
        "description": "This task has no task_id",
        "priority": "low",
    }

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(invalid_task),
        MessageGroupId="tasks",
        MessageDeduplicationId="missing-field-123",
    )

    messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
    assert "Messages" in messages

    lambda_event = {"Records": [{"body": messages["Messages"][0]["Body"]}]}

    # Processor should raise exception
    try:
        processor_handler(lambda_event, None)
        assert False, "Expected processor to raise exception for missing field"
    except Exception as e:
        assert "task_id" in str(e) or "field required" in str(e).lower()


def test_task_with_due_date(api_client, processor_handler, sqs_fifo_queue):
    """
    E2E test: Task with due_date is processed correctly.

    Verifies:
    - API accepts task with due_date
    - due_date is preserved in SQS message
    - Processor receives and processes task with due_date
    """
    sqs, queue_url = sqs_fifo_queue

    # Create task with due_date
    future_date = (datetime.now() + timedelta(days=7)).isoformat()
    task_payload = {
        "title": "Task with Due Date",
        "description": "This task has a deadline",
        "priority": "high",
        "due_date": future_date,
    }

    # Submit task
    response = api_client.post("/tasks", json=task_payload)
    assert response.status_code == 201
    task_id = response.json()["task_id"]

    # Receive message
    messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
    assert "Messages" in messages

    message_body = json.loads(messages["Messages"][0]["Body"])

    # Verify due_date is preserved (may include timezone)
    assert message_body["task_id"] == task_id
    assert message_body["due_date"].startswith(future_date.split("+")[0])

    # Process with Lambda handler
    lambda_event = {"Records": [{"body": messages["Messages"][0]["Body"]}]}
    processor_handler(lambda_event, None)


def test_batch_processing_multiple_records(api_client, processor_handler, sqs_fifo_queue):
    """
    E2E test: Processor handles batch of messages in single Lambda invocation.

    Verifies:
    - Multiple tasks submitted
    - Lambda receives multiple records at once
    - All records are processed successfully
    """
    sqs, queue_url = sqs_fifo_queue

    # Submit multiple tasks
    num_tasks = 5
    task_titles = [f"Batch Task {i}" for i in range(num_tasks)]

    for title in task_titles:
        response = api_client.post(
            "/tasks",
            json={
                "title": title,
                "description": f"Description for {title}",
                "priority": "medium",
            },
        )
        assert response.status_code == 201

    # Receive all messages
    messages = sqs.receive_message(
        QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=1
    )

    assert "Messages" in messages
    assert len(messages["Messages"]) == num_tasks

    # Create Lambda event with multiple records (batch processing)
    lambda_event = {"Records": [{"body": msg["Body"]} for msg in messages["Messages"]]}

    # Process entire batch
    processor_handler(lambda_event, None)  # Should process all records
