# Import date so a task can store a due date
from datetime import date

# Optional is used for fields that are not always required
from typing import Optional

# BaseModel creates the Pydantic data model
# Field allows us to apply validation rules
from pydantic import BaseModel, Field


# Represents a task in the Single Agent Task Assistant system
class Task(BaseModel):

    # The task ID is optional because it can be assigned later
    id: Optional[int] = None

    # Every task must have a title
    # The title cannot be empty and is limited to 100 characters
    title: str = Field(
        min_length=1,
        max_length=100
    )

    # Description provides extra task information and is optional
    description: Optional[str] = None

    # Due date is optional because the AI agent may suggest it later
    due_date: Optional[date] = None

    # Priority defaults to "normal" when no value is provided
    priority: str = "normal"