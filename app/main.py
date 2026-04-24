from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes_ask import router as ask_router
from app.api.routes_chat import router as chat_router
from app.api.routes_eval import router as eval_router
from app.api.routes_health import router as health_router
from app.api.routes_transcribe import router as transcribe_router
from app.core.config import settings
from app.core.db import create_db_and_tables

BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Voice-first multilingual support agent for low-resource customer support.",
)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/", include_in_schema=False)
def serve_frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

app.include_router(health_router, tags=["health"])
app.include_router(ask_router, tags=["support"])
app.include_router(transcribe_router, tags=["voice"])
app.include_router(eval_router, tags=["evaluation"])
app.include_router(chat_router, tags=["chat"])