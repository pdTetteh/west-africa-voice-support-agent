from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import HTTPException, UploadFile
from faster_whisper import WhisperModel

from app.core.config import settings


ALLOWED_AUDIO_SUFFIXES = {
    ".flac",
    ".m4a",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".ogg",
    ".wav",
    ".webm",
}

_MODEL: WhisperModel | None = None


def _validate_audio_upload(filename: str | None, audio_bytes: bytes) -> str:
    suffix = Path(filename or "").suffix.lower()

    if suffix not in ALLOWED_AUDIO_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported audio format: {suffix or 'unknown'}. "
                f"Supported formats: {', '.join(sorted(ALLOWED_AUDIO_SUFFIXES))}"
            ),
        )

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

    max_bytes = settings.max_audio_upload_mb * 1024 * 1024
    if len(audio_bytes) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Audio file exceeds the {settings.max_audio_upload_mb} MB upload limit.",
        )

    return suffix


def _get_faster_whisper_model() -> WhisperModel:
    global _MODEL

    if _MODEL is None:
        _MODEL = WhisperModel(
            settings.faster_whisper_model_size,
            device=settings.faster_whisper_device,
            compute_type=settings.faster_whisper_compute_type,
        )

    return _MODEL


def _transcribe_with_faster_whisper_bytes(audio_bytes: bytes, suffix: str) -> str:
    model = _get_faster_whisper_model()

    with NamedTemporaryFile(suffix=suffix, delete=True) as temp_file:
        temp_file.write(audio_bytes)
        temp_file.flush()

        segments, info = model.transcribe(
            temp_file.name,
            beam_size=settings.faster_whisper_beam_size,
            language=settings.faster_whisper_language,
            condition_on_previous_text=settings.faster_whisper_condition_on_previous_text,
        )

        segment_list = list(segments)
        text = " ".join(segment.text.strip() for segment in segment_list).strip()

    if not text:
        raise HTTPException(status_code=502, detail="ASR backend returned an empty transcript.")

    return text


async def transcribe_audio(file: UploadFile) -> str:
    audio_bytes = await file.read()
    suffix = _validate_audio_upload(file.filename, audio_bytes)

    if settings.asr_backend == "stub":
        return f"Transcription placeholder for uploaded file: {file.filename}"

    if settings.asr_backend == "faster_whisper":
        return _transcribe_with_faster_whisper_bytes(audio_bytes, suffix)

    raise HTTPException(
        status_code=500,
        detail=f"Unsupported ASR backend configured: {settings.asr_backend}",
    )