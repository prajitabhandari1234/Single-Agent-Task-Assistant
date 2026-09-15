import pytest

from fastapi.testclient import TestClient

from main import app

from services.task_service import task_service


@pytest.fixture
def client():
    """
    Provide a FastAPI TestClient for API tests.
    """

    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_task_service():
    """
    Reset the shared in-memory task service
    before and after every test.

    This prevents one test from affecting another.
    """

    task_service.tasks.clear()
    task_service.next_id = 1

    yield

    task_service.tasks.clear()
    task_service.next_id = 1