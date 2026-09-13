# Import FastAPI
from fastapi import FastAPI

# Import normal task routes
from api.routes import router

# Import AI agent routes
from api.agent_routes import router as agent_router


# Create the FastAPI application
app = FastAPI(
    title="Single Agent Task Assistant",
    description="COIT12204 Assessment 3",
    version="1.0.0"
)


# Register normal task routes
app.include_router(router)

# Register AI agent routes
app.include_router(agent_router)


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Single Agent Task Assistant API"
    }