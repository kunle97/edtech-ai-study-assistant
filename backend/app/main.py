from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.admin.router import router as admin_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered study assistant platform",
)

app.include_router(auth_router)
app.include_router(admin_router)

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "healthy"}