"""Processor Lambda Handler Tests"""

from unittest.mock import patch

import pytest

from services.processor.handler import handle


def test_handler_success(sqs_event):
    """Successful processing should not raise exception"""
    # Should not raise
    handle(sqs_event, None)


def test_handler_failure_triggers_retry(sqs_event):
    """Processing failure should raise exception for retry"""

    def fail(task):
        raise RuntimeError("Processing failed")

    with patch(
        "services.processor.services.task_processor.TaskProcessor.process",
        side_effect=fail,
    ):
        with pytest.raises(RuntimeError):
            handle(sqs_event, None)


def test_handler_invalid_json_triggers_retry():
    """Invalid JSON should raise exception for retry"""
    event = {"Records": [{"body": "not-valid-json"}]}

    with pytest.raises(Exception):
        handle(event, None)


def test_multiple_records_processed_in_order(multiple_records_event):
    """Multiple records should be processed sequentially in order"""
    calls = []

    def record_call(task):
        calls.append(task["task_id"])

    with patch(
        "services.processor.services.task_processor.TaskProcessor.process",
        side_effect=record_call,
    ):
        handle(multiple_records_event, None)

    assert calls == ["1", "2"]
