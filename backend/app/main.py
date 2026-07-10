from fastapi import FastAPI

app = FastAPI(
    title="LearnPath AI Study Assistant",
    version="0.1.0",
    description="AI-powered study assistant platform",
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "healthy"}