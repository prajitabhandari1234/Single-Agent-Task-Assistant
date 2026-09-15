from models.task import Task
from services.task_service import task_service
from agents.tools import lookup_task


def test_lookup_existing_task():
    """
    Test that lookup_task returns information
    about an existing task.
    """

    # Create a task in the shared task service
    task = task_service.create_task(
        Task(
            title="Complete Assessment 3",
            description="Finish coding and testing",
            priority="high"
        )
    )

    # Call the LangChain tool
    result = lookup_task.invoke(
        {
            "task_id": task.id
        }
    )

    # Check that expected task information is returned
    assert "Task ID: 1" in result
    assert "Complete Assessment 3" in result
    assert "Finish coding and testing" in result
    assert "Priority: high" in result
    assert "Due date: Not set" in result


def test_lookup_missing_task():
    """
    Test that lookup_task handles a task
    that does not exist.
    """

    result = lookup_task.invoke(
        {
            "task_id": 999
        }
    )

    assert result == "Task not found"


def test_lookup_task_with_no_description():
    """
    Test that a task without a description
    is handled correctly.
    """

    task = task_service.create_task(
        Task(
            title="Study pytest",
            priority="normal"
        )
    )

    result = lookup_task.invoke(
        {
            "task_id": task.id
        }
    )

    assert "Study pytest" in result
    assert "Description: No description" in result
    assert "Priority: normal" in result


def test_lookup_task_does_not_modify_task():
    """
    Test that using the lookup tool does not
    unexpectedly modify the stored task.
    """

    task = task_service.create_task(
        Task(
            title="Original task",
            description="Original description",
            priority="low"
        )
    )

    original_title = task.title
    original_description = task.description
    original_priority = task.priority

    lookup_task.invoke(
        {
            "task_id": task.id
        }
    )

    stored_task = task_service.get_task(
        task.id
    )

    assert stored_task.title == original_title
    assert stored_task.description == original_description
    assert stored_task.priority == original_priority