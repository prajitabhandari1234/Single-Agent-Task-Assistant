from models.task import Task

from services.task_service import TaskService


def test_create_task():
    """
    Test that TaskService creates a task
    and automatically assigns an ID.
    """

    service = TaskService()

    task = Task(
        title="Learn pytest"
    )

    created_task = service.create_task(task)

    assert created_task.id == 1
    assert created_task.title == "Learn pytest"
    assert len(service.tasks) == 1


def test_get_existing_task():
    """
    Test retrieving a task that exists.
    """

    service = TaskService()

    created_task = service.create_task(
        Task(
            title="Complete assignment"
        )
    )

    result = service.get_task(
        created_task.id
    )

    assert result is not None
    assert result.id == 1
    assert result.title == "Complete assignment"


def test_get_missing_task_returns_none():
    """
    Test retrieving a task that does not exist.
    """

    service = TaskService()

    result = service.get_task(999)

    assert result is None


def test_get_all_tasks():
    """
    Test retrieving all stored tasks.
    """

    service = TaskService()

    service.create_task(
        Task(title="Task 1")
    )

    service.create_task(
        Task(title="Task 2")
    )

    tasks = service.get_all_tasks()

    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"


def test_update_task():
    """
    Test updating an existing task.
    """

    service = TaskService()

    created_task = service.create_task(
        Task(
            title="Original task"
        )
    )

    updated_task = Task(
        title="Updated task",
        priority="high"
    )

    result = service.update_task(
        created_task.id,
        updated_task
    )

    assert result is not None
    assert result.id == created_task.id
    assert result.title == "Updated task"
    assert result.priority == "high"


def test_update_missing_task_returns_none():
    """
    Test updating a task that does not exist.
    """

    service = TaskService()

    updated_task = Task(
        title="Updated task"
    )

    result = service.update_task(
        999,
        updated_task
    )

    assert result is None


def test_delete_task():
    """
    Test deleting an existing task.
    """

    service = TaskService()

    created_task = service.create_task(
        Task(
            title="Delete me"
        )
    )

    result = service.delete_task(
        created_task.id
    )

    assert result is True
    assert len(service.tasks) == 0


def test_delete_missing_task_returns_false():
    """
    Test deleting a task that does not exist.
    """

    service = TaskService()

    result = service.delete_task(999)

    assert result is False