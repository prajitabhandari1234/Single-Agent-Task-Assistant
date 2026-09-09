from fastapi import FastAPI

app = FastAPI(
    title="Single Agent Task Assistant",
    description="COIT12204 Assessment 3",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Single Agent Task Assistant API"
    }