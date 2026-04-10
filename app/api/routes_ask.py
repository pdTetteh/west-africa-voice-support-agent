from fastapi import APIRouter

from app.agent.pipeline import run_support_pipeline
from app.core.schemas import AskRequest, AskResponse

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask_support_agent(payload: AskRequest) -> AskResponse:
    return run_support_pipeline(query=payload.query)