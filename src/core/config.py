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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()