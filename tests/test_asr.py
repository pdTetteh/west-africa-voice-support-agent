from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_transcribe_endpoint_stub_backend(monkeypatch) -> None:
    monkeypatch.setattr(settings, "asr_backend", "stub")

    response = client.post(
        "/transcribe",
        files={"file": ("sample.wav", b"fake-audio-bytes", "audio/wav")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "Transcription placeholder" in payload["transcript"]


def test_transcribe_endpoint_faster_whisper_backend(monkeypatch) -> None:
    monkeypatch.setattr(settings, "asr_backend", "faster_whisper")

    def fake_transcribe(audio_bytes: bytes, suffix: str) -> str:
        assert suffix == ".wav"
        assert audio_bytes == b"fake-audio-bytes"
        return "my cash out failed but my balance was deducted"

    monkeypatch.setattr(
        "app.asr.transcribe._transcribe_with_faster_whisper_bytes",
        fake_transcribe,
    )

    response = client.post(
        "/transcribe",
        files={"file": ("sample.wav", b"fake-audio-bytes", "audio/wav")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["transcript"] == "my cash out failed but my balance was deducted"


def test_transcribe_rejects_unsupported_format(monkeypatch) -> None:
    monkeypatch.setattr(settings, "asr_backend", "stub")

    response = client.post(
        "/transcribe",
        files={"file": ("sample.txt", b"not-audio", "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported audio format" in response.json()["detail"]