# Import the Task model so the service can create and manage tasks
from models.task import Task


# Handles business logic for task management
class TaskService:

    def __init__(self):
        # Store tasks in memory for now
        self.tasks = []

        # Track the next available task ID
        self.next_id = 1

    def create_task(self, task: Task) -> Task:
        """
        Create a new task and assign a unique ID.
        """

        # Assign the next available ID to the task
        task.id = self.next_id

        # Increase the ID counter for the next task
        self.next_id += 1

        # Store the task in the in-memory list
        self.tasks.append(task)

        # Return the newly created task
        return task

    def get_task(self, task_id: int):
        """
        Return a task using its ID.
        """

        # Search through all stored tasks
        for task in self.tasks:

            # Compare the task ID with the requested ID
            if task.id == task_id:
                return task

        # Return None when no matching task is found
        return None

    def get_all_tasks(self):
        """
        Return all stored tasks.
        """

        return self.tasks

    def update_task(self, task_id: int, updated_task: Task):
        """
        Update an existing task.
        """

        # Search for the task that needs to be updated
        for index, task in enumerate(self.tasks):

            if task.id == task_id:

                # Keep the original task ID
                updated_task.id = task_id

                # Replace the old task with the updated task
                self.tasks[index] = updated_task

                # Return the updated task
                return updated_task

        # Return None if the task does not exist
        return None

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task using its ID.
        """

        # Search for the task
        for index, task in enumerate(self.tasks):

            if task.id == task_id:

                # Remove the task from the list
                del self.tasks[index]

                # Return True when deletion is successful
                return True

        # Return False if the task was not found
        return False


# Create one shared TaskService instance
# The API routes and AI agent tools will use this same instance
# so they can access the same in-memory task data.
task_service = TaskService()