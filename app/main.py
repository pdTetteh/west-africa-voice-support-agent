from fastapi import FastAPI

from app.api.routes_ask import router as ask_router
from app.api.routes_eval import router as eval_router
from app.api.routes_health import router as health_router
from app.api.routes_transcribe import router as transcribe_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Voice-first multilingual support agent scaffold for low-resource customer support.",
)

app.include_router(health_router, tags=["health"])
app.include_router(ask_router, tags=["support"])
app.include_router(transcribe_router, tags=["voice"])
app.include_router(eval_router, tags=["evaluation"])