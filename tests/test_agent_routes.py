# Import the agent routes module so its
# suggest_due_date function can be mocked
from api import agent_routes


def test_agent_endpoint_success(client, monkeypatch):
    """
    Test that the agent endpoint returns
    a successful structured response.
    """

    # Create a fake agent function
    def mock_suggest_due_date(
        title,
        description="",
        priority="normal",
        task_id=None
    ):
        return "2026-09-25"

    # Replace the real agent function
    # so Gemini is not called
    monkeypatch.setattr(
        agent_routes,
        "suggest_due_date",
        mock_suggest_due_date
    )

    response = client.post(
        "/api/agent/suggest_due_date",
        json={
            "title": "Complete Assessment 3",
            "description": "Finish testing",
            "priority": "high"
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "suggested_due_date": "2026-09-25",
        "status": "success"
    }


def test_agent_endpoint_with_task_id(
    client,
    monkeypatch
):
    """
    Test that a valid task ID can be
    supplied to the agent endpoint.
    """

    received_data = {}

    def mock_suggest_due_date(
        title,
        description="",
        priority="normal",
        task_id=None
    ):
        # Store values received from the API
        received_data["title"] = title
        received_data["priority"] = priority
        received_data["task_id"] = task_id

        return "2026-09-24"

    monkeypatch.setattr(
        agent_routes,
        "suggest_due_date",
        mock_suggest_due_date
    )

    response = client.post(
        "/api/agent/suggest_due_date",
        json={
            "task_id": 1,
            "title": "Existing task",
            "description": "Use stored task information",
            "priority": "normal"
        }
    )

    assert response.status_code == 200

    assert (
        response.json()["suggested_due_date"]
        == "2026-09-24"
    )

    # Verify that FastAPI passed the values
    # correctly to the agent
    assert received_data["title"] == "Existing task"
    assert received_data["priority"] == "normal"
    assert received_data["task_id"] == 1


def test_agent_endpoint_invalid_priority(client):
    """
    Test that an unsupported priority
    is rejected by Pydantic validation.
    """

    response = client.post(
        "/api/agent/suggest_due_date",
        json={
            "title": "Complete Assessment",
            "priority": "urgent"
        }
    )

    assert response.status_code == 422


def test_agent_endpoint_empty_title(client):
    """
    Test that an empty task title
    is rejected.
    """

    response = client.post(
        "/api/agent/suggest_due_date",
        json={
            "title": "",
            "priority": "normal"
        }
    )

    assert response.status_code == 422


def test_agent_endpoint_title_too_long(client):
    """
    Test that a title longer than
    100 characters is rejected.
    """

    response = client.post(
        "/api/agent/suggest_due_date",
        json={
            "title": "A" * 101,
            "priority": "normal"
        }
    )

    assert response.status_code == 422


def test_agent_endpoint_invalid_task_id(client):
    """
    Test that a task ID below 1
    is rejected.
    """

    response = client.post(
        "/api/agent/suggest_due_date",
        json={
            "task_id": 0,
            "title": "Test task",
            "priority": "normal"
        }
    )

    assert response.status_code == 422


def test_agent_endpoint_missing_title(client):
    """
    Test that the required title
    field cannot be omitted.
    """

    response = client.post(
        "/api/agent/suggest_due_date",
        json={
            "priority": "high"
        }
    )

    assert response.status_code == 422


def test_agent_endpoint_unexpected_error(
    client,
    monkeypatch
):
    """
    Test that an unexpected agent error
    produces HTTP 500.
    """

    def mock_suggest_due_date(
        title,
        description="",
        priority="normal",
        task_id=None
    ):
        raise RuntimeError(
            "Mock agent failure"
        )

    monkeypatch.setattr(
        agent_routes,
        "suggest_due_date",
        mock_suggest_due_date
    )

    response = client.post(
        "/api/agent/suggest_due_date",
        json={
            "title": "Failure test",
            "description": "Test API error handling",
            "priority": "high"
        }
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Agent failed to generate due date."
    }