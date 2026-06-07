from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # System
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Audio Capture
    sample_rate: int = Field(default=16000, alias="SAMPLE_RATE")
    chunk_duration_ms: int = Field(default=30, alias="CHUNK_DURATION_MS")
    input_device_index: Optional[int] = Field(default=None, alias="INPUT_DEVICE_INDEX")
    
    # Wake Word (Porcupine)
    porcupine_access_key: str = Field(default="", alias="PORCUPINE_ACCESS_KEY")
    porcupine_keyword_path: str = Field(
        default="src/models/hey_emo.ppn", 
        alias="PORCUPINE_KEYWORD_PATH"
    )
    porcupine_model_path: str = Field(
        default="src/models/porcupine_params.pv", 
        alias="PORCUPINE_MODEL_PATH"
    )
    
    # STT (Vosk)
    vosk_model_path: str = Field(
        default="src/models/vosk-model-small-fa-0.4", 
        alias="VOSK_MODEL_PATH"
    )
    
    # TTS (Coqui)
    coqui_model_name: str = Field(
        default="tts_models/fa/cv/vits", 
        alias="COQUI_MODEL_NAME"
    )
    
    # Cloud Fallback APIs
    gapgpt_api_key: str = Field(default="", alias="GAPGPT_API_KEY")
    gapgpt_api_url: str = Field(
        default="https://api.gapgpt.ai/v1/chat", 
        alias="GAPGPT_API_URL"
    )
    azure_tts_key: str = Field(default="", alias="AZURE_TTS_KEY")
    azure_tts_region: str = Field(default="eastus", alias="AZURE_TTS_REGION")
    
    # BLE
    ble_device_address: Optional[str] = Field(default=None, alias="BLE_DEVICE_ADDRESS")
    use_ble: bool = Field(default=True, alias="USE_BLE")
    
    # Emotion
    emotion_model_name: str = Field(
        default="j-hartmann/emotion-english-distilroberta-base", 
        alias="EMOTION_MODEL_NAME"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Allow lower-case env vars

settings = Settings()