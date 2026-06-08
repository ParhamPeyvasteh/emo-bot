from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # System
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Audio
    sample_rate: int = Field(default=16000, alias="SAMPLE_RATE")
    chunk_duration_ms: int = Field(default=80, alias="CHUNK_DURATION_MS")
    input_device_index: int = Field(default=0, alias="INPUT_DEVICE_INDEX")
    
    # Wake word
    openwakeword_model_path: str = Field(default="src/models", alias="OPENWAKEWORD_MODEL_PATH")
    wake_word_threshold: float = Field(default=0.5, alias="WAKE_WORD_THRESHOLD")
    
    # STT
    vosk_model_path: str = Field(default="src/models/vosk-model-small-en-us-0.15", alias="VOSK_MODEL_PATH")
    stt_timeout_seconds: float = Field(default=3.0, alias="STT_TIMEOUT_SECONDS")
    stt_silence_seconds: float = Field(default=1.0, alias="STT_SILENCE_SECONDS")
    
    # AI (GapGPT)
    ai_api_url: str = Field(default="", alias="AI_API_URL")
    ai_api_key: str = Field(default="", alias="AI_API_KEY")
    ai_model: str = Field(default="", alias="AI_MODEL")
    ai_timeout: int = Field(default=30, alias="AI_TIMEOUT")
    
    # BLE (optional)
    ble_device_address: str = Field(default="", alias="BLE_DEVICE_ADDRESS")
    use_ble: bool = Field(default=False, alias="USE_BLE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Allow extra fields? If you want to ignore extra env vars, set extra = "ignore"
        # But better to define all fields.
        extra = "forbid"   # or "ignore" if you prefer to ignore unknown env vars

settings = Settings()