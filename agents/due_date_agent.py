# Import the shared Gemini client function
# This keeps LLM configuration outside the agent
from utils.llm_client import generate_response


def suggest_due_date(
    title: str,
    description: str = "",
    priority: str = "normal"
) -> str:
    """
    Suggest a due date for a task using Gemini.

    This is the initial version of the Due Date Agent.
    Validation, state management and guardrails will be
    added in later development phases.
    """

    # Build the prompt using information about the task
    prompt = f"""
    You are a task management assistant.

    Suggest a suitable due date for the task below.

    Task title: {title}
    Description: {description}
    Priority: {priority}

    Return only one date using this format:
    YYYY-MM-DD
    """

    # Send the prompt to Gemini through the LLM abstraction layer
    response = generate_response(prompt)

    # Return the raw suggestion
    # Validation will be added in a later phase
    return response