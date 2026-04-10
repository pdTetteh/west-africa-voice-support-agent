from fastapi import APIRouter

from app.core.schemas import EvalSummary
from app.evaluation.run_eval import run_eval

router = APIRouter()


@router.post("/eval/run", response_model=EvalSummary)
def run_evaluation() -> EvalSummary:
    return run_eval()