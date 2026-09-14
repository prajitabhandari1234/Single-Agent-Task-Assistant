# Import logging so API activity can be recorded
import logging

# Import FastAPI routing and HTTP error tools
from fastapi import APIRouter, HTTPException

# Import Pydantic for request and response validation
from pydantic import BaseModel, Field

# Import the Due Date Agent
from agents.due_date_agent import suggest_due_date

# Import shared agent state
from agents.agent_state import agent_state

# Create a logger for this API module
logger = logging.getLogger(__name__)

# Ensure INFO messages from this module are displayed
logger.setLevel(logging.INFO)

# Create a router specifically for AI agent endpoints
router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"]
)


# Defines the request body for the due-date agent
class DueDateRequest(BaseModel):
    """
    Represents input sent to the Due Date Agent.
    """

    # Existing task ID is optional
    task_id: int | None = None

    # Task title is required
    # It must contain between 1 and 100 characters
    title: str = Field(
        min_length=1,
        max_length=100
    )

    # Description is optional
    description: str = ""

    # Priority defaults to normal
    priority: str = "normal"


# Defines the structured response returned by the agent endpoint
class DueDateResponse(BaseModel):
    """
    Represents the structured output returned by the agent.
    """

    # Final due date returned by the agent
    suggested_due_date: str

    # Indicates whether processing completed successfully
    status: str


# Agent endpoint for generating a due-date suggestion
@router.post(
    "/suggest_due_date",
    response_model=DueDateResponse
)
def suggest_due_date_endpoint(
    request: DueDateRequest
):
    """
    Generate a due-date suggestion using the single AI agent.
    """

    # Log the incoming request
    logger.info(
        "Due date request received for task: %s",
        request.title
    )

    try:
        # Call the Due Date Agent using the request data
        suggestion = suggest_due_date(
            title=request.title,
            description=request.description,
            priority=request.priority,
            task_id=request.task_id
        )

        # Log the final value returned by the agent
        logger.info(
            "Agent endpoint returning due date: %s",
            suggestion
        )

        # Return structured API output
        return DueDateResponse(
            suggested_due_date=suggestion,
            status="success"
        )

    except Exception as error:
        # Record the failure in AgentState
        agent_state.record_error()

        # Record the API failure in the agent history
        agent_state.record_action(
            f"Agent endpoint error: {str(error)}"
        )

        # Log the complete exception for debugging
        logger.exception(
            "Due date agent endpoint failed"
        )

        # Return HTTP 500 if an unexpected error reaches the API layer
        raise HTTPException(
            status_code=500,
            detail="Agent failed to generate due date."
        ) from error