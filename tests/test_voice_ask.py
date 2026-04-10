from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_voice_ask_runs_pipeline_from_transcript(monkeypatch) -> None:
    monkeypatch.setattr(settings, "asr_backend", "faster_whisper")

    def fake_transcribe(audio_bytes: bytes, suffix: str) -> str:
        return "I sent money to the wrong person"

    monkeypatch.setattr(
        "app.asr.transcribe._transcribe_with_faster_whisper_bytes",
        fake_transcribe,
    )

    response = client.post(
        "/voice-ask",
        files={"file": ("sample.wav", b"fake-audio-bytes", "audio/wav")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["transcript"] == "I sent money to the wrong person"
    assert payload["evidence"][0]["source"] == "wrong_recipient.md"
    assert payload["escalate"] is True