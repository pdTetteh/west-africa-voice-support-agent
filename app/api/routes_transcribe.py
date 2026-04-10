from fastapi import APIRouter, File, UploadFile

from app.agent.pipeline import run_support_pipeline
from app.asr.transcribe import transcribe_audio
from app.core.schemas import AskResponse, TranscribeResponse

router = APIRouter()


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...)) -> TranscribeResponse:
    transcript = await transcribe_audio(file)
    return TranscribeResponse(transcript=transcript)


@router.post("/voice-ask", response_model=AskResponse)
async def voice_ask(file: UploadFile = File(...)) -> AskResponse:
    transcript = await transcribe_audio(file)
    return run_support_pipeline(query=transcript, transcript=transcript)