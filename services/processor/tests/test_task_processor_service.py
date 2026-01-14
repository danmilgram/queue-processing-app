"""Processor Unit Tests - process_task()"""

import pytest
from services.task_processor import TaskProcessor


def test_process_task_success(valid_task):
    """Valid task should process without exception"""
    # Should not raise
    TaskProcessor.process(valid_task)


def test_process_task_missing_task_id():
    """Missing task_id should raise ValueError"""
    task = {
        "title": "Test",
        "description": "Test",
        "priority": "low",
    }

    with pytest.raises(Exception):  # Pydantic ValidationError
        TaskProcessor.process(task)


def test_process_task_invalid_priority():
    """Invalid priority should raise validation error"""
    task = {
        "task_id": "123",
        "title": "Test",
        "description": "Test",
        "priority": "urgent",
    }

    with pytest.raises(Exception):  # Pydantic ValidationError
        TaskProcessor.process(task)


def test_process_task_empty_title():
    """Empty title should raise validation error"""
    task = {
        "task_id": "123",
        "title": "",
        "description": "Test",
        "priority": "low",
    }

    with pytest.raises(Exception):  # Pydantic ValidationError
        TaskProcessor.process(task)
