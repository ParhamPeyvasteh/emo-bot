import asyncio
import json
from collections import deque
import numpy as np
from vosk import Model, KaldiRecognizer
from src.core.message_bus import MessageBus, EventType, Message
from src.workers.base_worker import BaseWorker
from src.core.config import settings
from src.core.logging_config import setup_logging

logger = setup_logging()

class STTWorker(BaseWorker):
    def __init__(self, bus: MessageBus):
        super().__init__(bus)
        self.model = None
        self.rec = None
        self.is_listening = False
        self.audio_buffer = []
        self.sample_rate = settings.sample_rate
        self.chunk_duration_ms = settings.chunk_duration_ms
        self.chunk_samples = int(self.sample_rate * self.chunk_duration_ms / 1000)
        self.silence_threshold = 7
        self.silence_duration_needed = 3
        self.max_listen_seconds = 10.0
        self.last_speech_time = None
        self.listen_task = None

        # Ring buffer for continuous pre‑listen audio (store up to 1.5 seconds)
        pre_buffer_seconds = 2
        pre_buffer_chunks = int(pre_buffer_seconds * 1000 / self.chunk_duration_ms)
        self.ring_buffer = deque(maxlen=pre_buffer_chunks)

        self.bus.subscribe(EventType.START_LISTENING, self.start_listening)
        self.bus.subscribe(EventType.AUDIO_CHUNK, self.handle_audio_chunk)

    async def run(self):
        logger.info(f"Loading Vosk model from {settings.vosk_model_path}")
        try:
            self.model = Model(settings.vosk_model_path)
            logger.info("Vosk model loaded")
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
        while True:
            await asyncio.sleep(1)

    async def start_listening(self, message: Message):
        if self.is_listening:
            logger.warning("Already listening, ignoring START_LISTENING")
            return
        logger.info("[COMMAND] Starting listening session – prepending ring buffer")
        self.is_listening = True
        # Prepend ring buffer content to audio_buffer
        self.audio_buffer = list(self.ring_buffer)  # copy the deque content
        logger.debug(f"[COMMAND] Prepend {len(self.ring_buffer)} chunks from ring buffer")
        self.last_speech_time = asyncio.get_event_loop().time()
        self.rec = KaldiRecognizer(self.model, self.sample_rate)
        if self.listen_task:
            self.listen_task.cancel()
        self.listen_task = asyncio.create_task(self.fallback_timeout())

    async def fallback_timeout(self):
        await asyncio.sleep(self.max_listen_seconds)
        if self.is_listening:
            logger.warning(f"[COMMAND] Max listen time ({self.max_listen_seconds}s) reached, forcing STT")
            await self.process_audio()
            self.is_listening = False

    def audio_energy(self, chunk: np.ndarray) -> float:
        return float(np.sqrt(np.mean(chunk.astype(np.float32)**2)))

    async def handle_audio_chunk(self, message: Message):
        chunk = message.payload
        # Always store the most recent chunk in the ring buffer (even when not listening)
        self.ring_buffer.append(chunk)

        if not self.is_listening:
            return

        self.audio_buffer.append(chunk)
        energy = self.audio_energy(chunk)
        now = asyncio.get_event_loop().time()
        if energy > self.silence_threshold:
            self.last_speech_time = now
            logger.debug(f"[COMMAND] Speech energy: {energy:.5f}")
        else:
            silence_duration = now - self.last_speech_time
            if silence_duration >= self.silence_duration_needed:
                logger.info(f"[COMMAND] Silence for {silence_duration:.2f}s – stopping STT")
                await self.process_audio()
                self.is_listening = False
                if self.listen_task:
                    self.listen_task.cancel()

    async def process_audio(self):
        if not self.audio_buffer:
            logger.warning("[COMMAND] No audio captured for STT")
            return
        audio_bytes = b''.join(chunk.astype(np.int16).tobytes() for chunk in self.audio_buffer)
        logger.debug(f"[COMMAND] Processing {len(audio_bytes)} bytes of audio")
        if self.rec.AcceptWaveform(audio_bytes):
            result = json.loads(self.rec.Result())
            text = result.get("text", "").strip()
        else:
            partial = json.loads(self.rec.PartialResult())
            text = partial.get("partial", "").strip()
        if text:
            logger.info(f"[COMMAND] STT result: '{text}'")
            await self.bus.publish(Message(
                type=EventType.USER_TRANSCRIPT,
                payload={"text": text}
            ))
        else:
            logger.warning("[COMMAND] STT returned empty text")
        self.audio_buffer.clear()

    async def stop(self):
        if self.listen_task:
            self.listen_task.cancel()
        await super().stop()