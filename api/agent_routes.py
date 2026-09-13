# Import FastAPI routing and HTTP error tools
from fastapi import APIRouter, HTTPException

# Import Pydantic for request validation
from pydantic import BaseModel, Field

# Import the Due Date Agent
from agents.due_date_agent import suggest_due_date

# Import agent state so state information can be returned
from agents.agent_state import agent_state


# Create a router specifically for AI agent endpoints
router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"]
)


# Defines the request body for the due-date agent
class DueDateRequest(BaseModel):
    # Optional existing task ID
    task_id: int | None = None

    # A task title is required
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
    suggested_due_date: str
    status: str


# Agent endpoint for generating a due-date suggestion
@router.post(
    "/suggest_due_date",
    response_model=DueDateResponse
)
def suggest_due_date_endpoint(request: DueDateRequest):
    """
    Generate a due-date suggestion using the single AI agent.
    """

    try:
        # Call the Due Date Agent using the request data
        suggestion = suggest_due_date(
            title=request.title,
            description=request.description,
            priority=request.priority,
            task_id=request.task_id
        )

        # Return a structured API response
        return DueDateResponse(
            suggested_due_date=suggestion,
            status="success"
        )

    except Exception as error:
        # Record that the agent encountered an error
        agent_state.record_error()

        # Return an HTTP 500 response when the agent fails
        raise HTTPException(
            status_code=500,
            detail=f"Agent failed to generate due date: {error}"
        )