from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Audio
    sample_rate: int = 16000
    chunk_duration_ms: int = 30          # 30ms frames
    input_device_index: int = 0          # default mic
    
    # Wake word
    porcupine_keyword_path: str = "models/hey_emo.ppn"
    porcupine_library_path: str = ""     # auto-detect
    
    # STT
    vosk_model_path: str = "models/vosk-model-small-fa-0.4"  # Persian small
    whisper_model_size: str = "tiny"     # fallback
    
    # TTS
    coqui_model_path: str = "models/coqui/farsi_fast"
    azure_tts_key: str = ""              # from .env
    azure_tts_region: str = "eastus"
    
    # LLM
    gapgpt_api_url: str = "https://api.gapgpt.ai/v1/chat"  # example
    gapgpt_api_key: str = ""             # from .env
    local_llm_model_path: str = "models/phi-3-mini"   # optional offline
    
    # BLE
    ble_device_address: str = ""         # ESP32 MAC, or COM port fallback
    use_ble: bool = True
    
    # System
    log_level: str = "INFO"
    enable_offline_fallback: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()