from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "West Africa Voice Support Agent"
    environment: str = "development"
    log_level: str = "INFO"

    confidence_threshold: float = 0.60
    retrieval_top_k: int = 3

    asr_backend: str = "faster_whisper"
    faster_whisper_model_size: str = "small"
    faster_whisper_device: str = "cpu"
    faster_whisper_compute_type: str = "int8"
    faster_whisper_beam_size: int = 5
    faster_whisper_language: str | None = "en"
    faster_whisper_condition_on_previous_text: bool = False

    database_url: str = "sqlite:///./app.db"
    max_audio_upload_mb: int = 25

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()