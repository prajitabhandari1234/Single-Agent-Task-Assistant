# Import FastAPI tools for creating API routes and handling errors
from fastapi import APIRouter, HTTPException

# Import the Task model
from models.task import Task

# Import the service layer that contains task business logic
from services.task_service import TaskService


# Create a router for task-related endpoints
router = APIRouter()

# Create one TaskService instance for managing tasks in memory
task_service = TaskService()


# Create a new task
@router.post("/tasks")
def create_task(task: Task):
    return task_service.create_task(task)


# Get all tasks
@router.get("/tasks")
def get_all_tasks():
    return task_service.get_all_tasks()


# Get one task by ID
@router.get("/tasks/{task_id}")
def get_task(task_id: int):

    # Ask the service layer to find the task
    task = task_service.get_task(task_id)

    # Return 404 if the task does not exist
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# Update an existing task
@router.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task):

    # Ask the service layer to update the task
    task = task_service.update_task(
        task_id,
        updated_task
    )

    # Return 404 if the task does not exist
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# Delete a task
@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):

    # Ask the service layer to delete the task
    deleted = task_service.delete_task(task_id)

    # Return 404 if the task does not exist
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {
        "message": "Task deleted successfully"
    }