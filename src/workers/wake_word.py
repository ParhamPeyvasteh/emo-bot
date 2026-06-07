import asyncio
import numpy as np
from pathlib import Path
from openwakeword.model import Model
from src.core.message_bus import MessageBus, EventType, Message
from src.workers.base_worker import BaseWorker
from src.core.config import settings
from src.core.logging_config import setup_logging

logger = setup_logging()

class WakeWordWorker(BaseWorker):
    def __init__(self, bus: MessageBus):
        super().__init__(bus)
        self.model = None
        self.threshold = settings.wake_word_threshold
        self.model_path = Path("src/models")
        self.bus.subscribe(EventType.AUDIO_CHUNK, self.handle_audio_chunk)

    def _resolve_model_path(self) -> str:
        # Automatically pick the first .onnx file in models folder
        model_files = list(self.model_path.glob("*.onnx"))
        if not model_files:
            raise FileNotFoundError(f"No .onnx model found in {self.model_path}")
        # Prefer alexa model if exists, otherwise take first
        for f in model_files:
            if "alexa" in f.name.lower():
                return str(f)
        return str(model_files[0])

    async def run(self):
        try:
            model_file = self._resolve_model_path()
            logger.info(f"Loading wake word model from {model_file}")
            self.model = Model(wakeword_models=[model_file])
            logger.info("Wake word engine ready (listening)")
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            return
        while True:
            await asyncio.sleep(1)

    async def handle_audio_chunk(self, message: Message):
        if self.model is None:
            return
        audio = message.payload
        if audio.dtype != np.int16:
            audio = audio.astype(np.int16)
        try:
            prediction = self.model.predict(audio)
            # Get the highest confidence keyword
            best = max(prediction.items(), key=lambda x: x[1])
            word, conf = best
            if conf > self.threshold:
                logger.info(f"Wake word '{word}' detected (conf={conf:.3f})")
                await self.bus.publish(Message(
                    type=EventType.WAKE_WORD_DETECTED,
                    payload={"wake_word": word, "confidence": conf}
                ))
        except Exception as e:
            logger.error(f"Prediction error: {e}")

    async def stop(self):
        await super().stop()