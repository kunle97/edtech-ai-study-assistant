from fastapi import FastAPI

from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.chat.router import router as chat_router
from app.core.config import settings
from app.imports.router import router as imports_router


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered study assistant platform",
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(imports_router)
app.include_router(chat_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
