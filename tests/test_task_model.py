import pytest

from pydantic import ValidationError

from models.task import Task


def test_create_valid_task():
    """
    Test that a valid Task object can be created.
    """

    task = Task(
        title="Complete Assessment 3",
        description="Finish the assessment",
        priority="high"
    )

    assert task.title == "Complete Assessment 3"
    assert task.description == "Finish the assessment"
    assert task.priority == "high"
    assert task.id is None
    assert task.due_date is None


def test_task_default_priority():
    """
    Test that priority defaults to normal.
    """

    task = Task(
        title="Study pytest"
    )

    assert task.priority == "normal"


def test_task_title_cannot_be_empty():
    """
    Test that an empty title is rejected.
    """

    with pytest.raises(ValidationError):
        Task(
            title=""
        )


def test_task_title_cannot_exceed_100_characters():
    """
    Test that titles longer than 100 characters are rejected.
    """

    with pytest.raises(ValidationError):
        Task(
            title="A" * 101
        )