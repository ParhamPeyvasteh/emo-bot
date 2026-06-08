import asyncio
import sounddevice as sd
import numpy as np
from src.core.message_bus import MessageBus, EventType, Message
from src.workers.base_worker import BaseWorker
from src.core.config import settings
from src.core.logging_config import setup_logging
from src.vad import VoiceActivityDetector

logger = setup_logging()

class AudioCaptureWorker(BaseWorker):
    def __init__(self, bus: MessageBus):
        super().__init__(bus)
        self.sample_rate = settings.sample_rate
        self.chunk_duration_ms = settings.chunk_duration_ms
        self.chunk_samples = int(self.sample_rate * self.chunk_duration_ms / 1000)
        self.stream = None
        self.running = False
        self.vad = VoiceActivityDetector(sample_rate=self.sample_rate)
        self.loop = None

    async def run(self):
        self.running = True
        self.loop = asyncio.get_running_loop()
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.chunk_samples,
            dtype='int16',
            callback=self.audio_callback
        )
        self.stream.start()
        logger.info(f"Audio capture started (chunk={self.chunk_duration_ms}ms, {self.chunk_samples} samples)")

        while self.running:
            await asyncio.sleep(0.1)

    def audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Audio status: {status}")
        chunk = indata.flatten()
        energy = np.sqrt(np.mean(chunk.astype(np.float32)**2))
        logger.debug(f"Audio callback: energy={energy:.5f}")
        if energy > self.vad.threshold:
            logger.debug(f"Speech detected, energy={energy:.5f}")
            asyncio.run_coroutine_threadsafe(
                self.bus.publish(Message(type=EventType.AUDIO_CHUNK, payload=chunk)),
                self.loop
            )
        else:
            logger.debug(f"Silence (energy below {self.vad.threshold})")

    async def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        await super().stop()