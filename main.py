# Import FastAPI
from fastapi import FastAPI

# Import task routes
from api.routes import router


# Create the FastAPI application
app = FastAPI(
    title="Single Agent Task Assistant",
    description="COIT12204 Assessment 3",
    version="1.0.0"
)


# Register the task API routes
app.include_router(router)


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Single Agent Task Assistant API"
    }