# Import date utilities for creating test dates
from datetime import date, timedelta

# Import AIMessage so mocked responses look like LangChain responses
from langchain_core.messages import AIMessage

# Import the Due Date Agent module
from agents import due_date_agent

# Import shared agent state
from agents.agent_state import agent_state


class MockChain:
    """
    Simple fake LangChain chain used during testing.

    This allows the tests to control the LLM response
    without making a real Gemini API request.
    """

    def __init__(self, response=None, error=None):
        # Store the response that should be returned
        self.response = response

        # Store an optional error that should be raised
        self.error = error

    def invoke(self, data):
        """
        Simulate the invoke method used by
        the real LangChain workflow.
        """

        # Raise the configured error when testing failures
        if self.error is not None:
            raise self.error

        # Return a LangChain-style AI response
        return AIMessage(
            content=self.response
        )


def test_validate_valid_future_date():
    """
    Test that a correctly formatted future date
    is accepted by the validation function.
    """

    future_date = (
        date.today() + timedelta(days=5)
    ).isoformat()

    result = due_date_agent.validate_due_date(
        future_date
    )

    assert result is True


def test_validate_past_date():
    """
    Test that a date in the past is rejected.
    """

    past_date = (
        date.today() - timedelta(days=1)
    ).isoformat()

    result = due_date_agent.validate_due_date(
        past_date
    )

    assert result is False


def test_validate_invalid_date_format():
    """
    Test that a date using the wrong format
    is rejected.
    """

    result = due_date_agent.validate_due_date(
        "21/09/2026"
    )

    assert result is False


def test_fallback_high_priority():
    """
    Test the deterministic fallback for
    a high-priority task.
    """

    expected = (
        date.today() + timedelta(days=3)
    ).isoformat()

    result = due_date_agent.get_fallback_date(
        "high"
    )

    assert result == expected


def test_fallback_normal_priority():
    """
    Test the deterministic fallback for
    a normal-priority task.
    """

    expected = (
        date.today() + timedelta(days=7)
    ).isoformat()

    result = due_date_agent.get_fallback_date(
        "normal"
    )

    assert result == expected


def test_fallback_low_priority():
    """
    Test the deterministic fallback for
    a low-priority task.
    """

    expected = (
        date.today() + timedelta(days=14)
    ).isoformat()

    result = due_date_agent.get_fallback_date(
        "low"
    )

    assert result == expected


def test_extract_normal_response():
    """
    Test extraction from a normal
    LangChain AIMessage.
    """

    response = AIMessage(
        content="2026-09-25"
    )

    result = due_date_agent.extract_response_text(
        response
    )

    assert result == "2026-09-25"


def test_agent_with_mocked_valid_llm(monkeypatch):
    """
    Test the complete agent with a valid
    mocked LLM response.

    No real Gemini API request is made.
    """

    future_date = (
        date.today() + timedelta(days=5)
    ).isoformat()

    # Create a fake chain that returns a valid date
    mock_chain = MockChain(
        response=future_date
    )

    # Replace the real LangChain workflow
    # with the fake chain during this test
    monkeypatch.setattr(
        due_date_agent,
        "due_date_chain",
        mock_chain
    )

    result = due_date_agent.suggest_due_date(
        title="Complete Assessment 3",
        description="Finish testing",
        priority="high"
    )

    # Check the returned suggestion
    assert result == future_date

    # Check that agent state was updated
    assert (
        agent_state.last_suggestion
        == future_date
    )


def test_agent_invalid_llm_uses_fallback(monkeypatch):
    """
    Test that invalid LLM output causes
    the deterministic fallback to be used.
    """

    # Simulate Gemini returning an invalid date
    mock_chain = MockChain(
        response="next Friday"
    )

    # Replace the real LangChain workflow
    monkeypatch.setattr(
        due_date_agent,
        "due_date_chain",
        mock_chain
    )

    # Expected fallback for high priority
    expected = due_date_agent.get_fallback_date(
        "high"
    )

    # Store current error count
    previous_error_count = (
        agent_state.error_count
    )

    result = due_date_agent.suggest_due_date(
        title="Important assessment",
        priority="high"
    )

    # Agent should use fallback
    assert result == expected

    # State should contain fallback suggestion
    assert (
        agent_state.last_suggestion
        == expected
    )

    # Invalid output should increase error count
    assert (
        agent_state.error_count
        == previous_error_count + 1
    )


def test_agent_empty_llm_output_uses_fallback(
    monkeypatch
):
    """
    Test that an empty LLM response
    causes fallback logic to run.
    """

    # Simulate an empty Gemini response
    mock_chain = MockChain(
        response=""
    )

    # Replace the real LangChain workflow
    monkeypatch.setattr(
        due_date_agent,
        "due_date_chain",
        mock_chain
    )

    # Expected normal-priority fallback
    expected = due_date_agent.get_fallback_date(
        "normal"
    )

    result = due_date_agent.suggest_due_date(
        title="Study pytest",
        priority="normal"
    )

    # Agent should return fallback
    assert result == expected

    # State should store fallback
    assert (
        agent_state.last_suggestion
        == expected
    )


def test_agent_llm_exception_uses_fallback(
    monkeypatch
):
    """
    Test that an unexpected LLM error
    does not crash the agent.
    """

    # Create a fake chain that raises an error
    mock_chain = MockChain(
        error=RuntimeError(
            "Mock Gemini failure"
        )
    )

    # Replace the real LangChain workflow
    monkeypatch.setattr(
        due_date_agent,
        "due_date_chain",
        mock_chain
    )

    # Expected fallback for low priority
    expected = due_date_agent.get_fallback_date(
        "low"
    )

    # Store current error count
    previous_error_count = (
        agent_state.error_count
    )

    result = due_date_agent.suggest_due_date(
        title="Low priority task",
        priority="low"
    )

    # Agent should recover using fallback
    assert result == expected

    # State should store fallback suggestion
    assert (
        agent_state.last_suggestion
        == expected
    )

    # The error should be recorded
    assert (
        agent_state.error_count
        == previous_error_count + 1
    )