import numpy as np

class VoiceActivityDetector:
    def __init__(self, mode: int = 1, sample_rate: int = 16000, frame_duration_ms: int = 30):
        self.threshold = 0.01   # normal sensitivity

    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        energy = np.sqrt(np.mean(audio_chunk.astype(np.float32)**2))
        return energy > self.threshold