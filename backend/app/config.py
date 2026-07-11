from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aiavatar"
    secret_key: str = "change-this-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    gemini_api_key: str = ""
    whisper_model_size: str = "medium"
    whisper_device: str = "cuda"
    whisper_compute_type: str = "int8"
    kokoro_lang_code: str = "a"
    kokoro_voice: str = "af_heart"
    kokoro_device: str = "cpu"
    wav2lip_dir: Path = Path("./wav2lip")
    wav2lip_checkpoint: str = "Wav2Lip_GAN.pt"
    wav2lip_batch_size: int = 8
    wav2lip_face_det_batch: int = 4
    wav2lip_enabled: bool = True
    media_dir: Path = Path("./media")
    models_dir: Path = Path("./models")
    audio_retention_hours: int = 24
    video_retention_hours: int = 24
    max_audio_size_mb: int = 25
    max_avatar_size_mb: int = 5
    max_history_turns: int = 20
    default_system_prompt: str = "You are a helpful, friendly AI assistant."
    max_tts_chars: int = 2000
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

settings = Settings()
