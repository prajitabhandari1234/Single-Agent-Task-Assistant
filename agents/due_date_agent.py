# Import logging so agent activity can be recorded
import logging

# Import date utilities for validation and fallback dates
from datetime import date, datetime, timedelta

# Import the LangChain prompt template
from langchain_core.prompts import ChatPromptTemplate

# Import the Gemini LangChain model
from utils.llm_client import get_langchain_model

# Import the task lookup tool
from agents.tools import lookup_task

# Import the shared agent state
from agents.agent_state import agent_state


# Create a logger for the Due Date Agent
logger = logging.getLogger(__name__)

# Ensure INFO messages from this module are displayed
logger.setLevel(logging.INFO)


# Create the Gemini model used by LangChain
llm = get_langchain_model()


# Define the structured prompt used by the Due Date Agent
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a task management assistant.

            Your role is to suggest an appropriate due date
            based on the task title, description, priority,
            stored task information, and today's date.

            Rules:
            - Return only one date.
            - Use YYYY-MM-DD format.
            - Do not return a date before today's date.
            - Do not include explanations.
            """
        ),
        (
            "human",
            """
            Today's date: {today}

            Task title: {title}
            Description: {description}
            Priority: {priority}

            Stored task information:
            {task_information}

            Suggest a suitable due date.
            """
        )
    ]
)


# Create the LangChain workflow
due_date_chain = prompt_template | llm


def get_fallback_date(priority: str) -> str:
    """
    Return a deterministic fallback date when
    the AI output cannot be safely used.
    """

    today = date.today()

    # Use different fallback periods based on priority
    if priority.lower() == "high":
        fallback = today + timedelta(days=3)

    elif priority.lower() == "low":
        fallback = today + timedelta(days=14)

    else:
        fallback = today + timedelta(days=7)

    return fallback.isoformat()


def validate_due_date(value: str) -> bool:
    """
    Check that the AI response is a valid ISO date
    and is not in the past.
    """

    try:
        # Convert text into a Python date
        suggested_date = datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

        # Reject past dates
        if suggested_date < date.today():
            return False

        return True

    except ValueError:
        # Invalid date format
        return False


def extract_response_text(response) -> str:
    """
    Extract text from either a normal LangChain response
    or Gemini structured content blocks.
    """

    # Handle a normal text response
    if isinstance(response.content, str):
        return response.content.strip()

    # Handle a structured list response
    if isinstance(response.content, list):
        text_parts = []

        for block in response.content:

            if isinstance(block, dict) and "text" in block:
                text_parts.append(block["text"])

            elif isinstance(block, str):
                text_parts.append(block)

        return "".join(text_parts).strip()

    # Handle an unexpected response type
    return str(response.content).strip()


def suggest_due_date(
    title: str,
    description: str = "",
    priority: str = "normal",
    task_id: int | None = None
) -> str:
    """
    Suggest a task due date using LangChain, Gemini,
    task tools, state management, validation and fallback logic.
    """

    # Save the state before this agent run
    previous_state = agent_state.get_state_snapshot()

    # Reset values that only belong to the current run
    agent_state.reset_run_state()

    # Log the state before execution
    logger.info(
        "Agent state before run: %s",
        previous_state
    )

    # Record the start of the agent run
    agent_state.record_action(
        f"Due date requested for task: {title}"
    )

    logger.info(
        "Due date agent started for task: %s",
        title
    )

    # Default information when no task ID is supplied
    task_information = "No stored task information available."

    try:
        # Use the lookup tool when a task ID is provided
        if task_id is not None:

            task_information = lookup_task.invoke(
                {
                    "task_id": task_id
                }
            )

            # Update state with tool usage
            agent_state.record_tool_call(
                "lookup_task"
            )

            agent_state.record_action(
                f"lookup_task called for task ID {task_id}"
            )

            logger.info(
                "lookup_task called for task ID %s",
                task_id
            )

        # Get today's date for the prompt
        today = date.today().isoformat()

        # Send task information through LangChain
        response = due_date_chain.invoke(
            {
                "today": today,
                "title": title,
                "description": description,
                "priority": priority,
                "task_information": task_information
            }
        )

        # Extract text from the Gemini response
        raw_suggestion = extract_response_text(
            response
        )

        logger.info(
            "Raw Gemini output: %s",
            raw_suggestion
        )

        # Validate the AI-generated date
        if validate_due_date(raw_suggestion):

            suggestion = raw_suggestion

            logger.info(
                "Valid due date accepted: %s",
                suggestion
            )

        else:
            # Use deterministic fallback if output is invalid
            suggestion = get_fallback_date(
                priority
            )

            agent_state.record_error()

            agent_state.record_action(
                f"Invalid AI output received: {raw_suggestion}"
            )

            agent_state.record_action(
                f"Fallback due date used: {suggestion}"
            )

            logger.warning(
                "Invalid AI output '%s'. Fallback used: %s",
                raw_suggestion,
                suggestion
            )

        # Store final suggestion in state
        agent_state.update_suggestion(
            suggestion
        )

        agent_state.record_action(
            f"Final due date suggestion: {suggestion}"
        )

        logger.info(
            "Final due date suggestion: %s",
            suggestion
        )

        # Capture and log updated state
        current_state = agent_state.get_state_snapshot()

        logger.info(
            "Agent state after run: %s",
            current_state
        )

        return suggestion

    except Exception as error:
        # Record unexpected agent errors
        agent_state.record_error()

        agent_state.record_action(
            f"Agent error: {str(error)}"
        )

        logger.exception(
            "Due date agent failed"
        )

        # Use fallback instead of allowing the agent to fail
        fallback = get_fallback_date(
            priority
        )

        agent_state.update_suggestion(
            fallback
        )

        agent_state.record_action(
            f"Fallback due date used after error: {fallback}"
        )

        logger.info(
            "Fallback due date after error: %s",
            fallback
        )

        # Log state after fallback
        current_state = agent_state.get_state_snapshot()

        logger.info(
            "Agent state after fallback: %s",
            current_state
        )

        return fallback