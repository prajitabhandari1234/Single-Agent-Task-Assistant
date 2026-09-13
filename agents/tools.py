# Import the LangChain tool decorator
from langchain_core.tools import tool

# Import the shared TaskService instance
from services.task_service import task_service


@tool
def lookup_task(task_id: int) -> str:
    """
    Look up an existing task using its task ID.

    The tool returns task information that can be used
    by the AI agent when making a due-date suggestion.
    """

    # Ask TaskService to find the requested task
    task = task_service.get_task(task_id)

    # Return a clear message when the task does not exist
    if task is None:
        return "Task not found"

    # Convert the task information into text for the agent
    return (
        f"Task ID: {task.id}; "
        f"Title: {task.title}; "
        f"Description: {task.description or 'No description'}; "
        f"Priority: {task.priority}; "
        f"Due date: {task.due_date or 'Not set'}"
    )