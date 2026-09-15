from agents.agent_state import AgentState


def test_agent_state_initial_values():
    """
    Test the initial values of a new AgentState.
    """

    state = AgentState()

    assert state.last_suggestion is None
    assert state.error_count == 0
    assert state.history == []
    assert state.last_tool_call is None


def test_update_suggestion():
    """
    Test that the latest agent suggestion is stored.
    """

    state = AgentState()

    state.update_suggestion(
        "2026-09-21"
    )

    assert state.last_suggestion == "2026-09-21"


def test_record_action():
    """
    Test that agent actions are added to history.
    """

    state = AgentState()

    state.record_action(
        "Due date requested"
    )

    assert len(state.history) == 1
    assert state.history[0] == "Due date requested"


def test_record_multiple_actions():
    """
    Test that multiple actions remain in history.
    """

    state = AgentState()

    state.record_action("Agent started")
    state.record_action("Tool called")
    state.record_action("Suggestion generated")

    assert len(state.history) == 3

    assert state.history == [
        "Agent started",
        "Tool called",
        "Suggestion generated"
    ]


def test_record_tool_call():
    """
    Test that the latest tool call is stored.
    """

    state = AgentState()

    state.record_tool_call(
        "lookup_task"
    )

    assert state.last_tool_call == "lookup_task"


def test_record_error():
    """
    Test that error_count increases when
    an agent error is recorded.
    """

    state = AgentState()

    state.record_error()

    assert state.error_count == 1


def test_multiple_errors():
    """
    Test that multiple errors are counted.
    """

    state = AgentState()

    state.record_error()
    state.record_error()
    state.record_error()

    assert state.error_count == 3


def test_reset_run_state():
    """
    Test that run-specific tool state is reset
    before a new agent run.
    """

    state = AgentState()

    state.record_tool_call(
        "lookup_task"
    )

    assert state.last_tool_call == "lookup_task"

    state.reset_run_state()

    assert state.last_tool_call is None


def test_get_state_snapshot():
    """
    Test that a state snapshot contains
    the expected state information.
    """

    state = AgentState()

    state.update_suggestion(
        "2026-09-21"
    )

    state.record_action(
        "Suggestion generated"
    )

    state.record_tool_call(
        "lookup_task"
    )

    snapshot = state.get_state_snapshot()

    assert snapshot["last_suggestion"] == "2026-09-21"
    assert snapshot["error_count"] == 0
    assert snapshot["history_count"] == 1
    assert snapshot["last_tool_call"] == "lookup_task"