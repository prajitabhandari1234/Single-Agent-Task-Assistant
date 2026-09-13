# Stores the internal state of the single AI agent
class AgentState:
    """
    Tracks information about previous agent activity.

    The state helps the agent remember its most recent
    suggestion, errors, actions, and tool usage.
    """

    def __init__(self):
        # Stores the most recent due-date suggestion
        self.last_suggestion = None

        # Counts how many agent errors have occurred
        self.error_count = 0

        # Stores a history of important agent actions
        self.history = []

        # Stores the name of the most recently used tool
        self.last_tool_call = None

    def update_suggestion(self, suggestion: str):
        """
        Store the latest suggestion produced by the agent.
        """

        self.last_suggestion = suggestion

    def record_action(self, action: str):
        """
        Add an agent action to the history.
        """

        self.history.append(action)

    def record_tool_call(self, tool_name: str):
        """
        Store the name of the most recently used tool.
        """

        self.last_tool_call = tool_name

    def record_error(self):
        """
        Increase the number of recorded agent errors.
        """

        self.error_count += 1


# Create one shared state object for the Due Date Agent
agent_state = AgentState()