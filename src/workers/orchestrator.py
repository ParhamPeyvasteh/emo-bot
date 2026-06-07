import asyncio
from src.core.message_bus import MessageBus, EventType, Message
from src.workers.base_worker import BaseWorker
from src.core.logging_config import setup_logging

logger = setup_logging()

class OrchestratorWorker(BaseWorker):
    def __init__(self, bus: MessageBus):
        super().__init__(bus)
        self.state = "idle"   # idle, greeting, listening
        self.bus.subscribe(EventType.WAKE_WORD_DETECTED, self.on_wake_word)
        self.bus.subscribe(EventType.TTS_FINISHED, self.on_tts_finished)

    async def run(self):
        while True:
            await asyncio.sleep(1)

    async def on_wake_word(self, message: Message):
        if self.state != "idle":
            logger.info(f"[ORCH] Wake word ignored, state={self.state}")
            return
        logger.info("[WAKE] Wake word detected – sending greeting")
        self.state = "greeting"
        await self.bus.publish(Message(
            type=EventType.TTS_REQUEST,
            payload={"text": "Hi, how can I help you?"}
        ))

    async def on_tts_finished(self, message: Message):
        if self.state == "greeting":
            logger.info("[GREETING] TTS finished – starting command listening")
            self.state = "listening"
            await self.bus.publish(Message(
                type=EventType.START_LISTENING,
                payload={}
            ))
        elif self.state == "listening":
            # TTS finished after a response? (e.g., from ResponseWorker)
            logger.info("[RESPONSE] TTS finished – returning to idle")
            self.state = "idle"
        # Other states? Not needed yet.

    # Optional: listen for USER_TRANSCRIPT to transition to response state
    # You can add another subscription:
    # self.bus.subscribe(EventType.USER_TRANSCRIPT, self.on_transcript)
    async def on_transcript(self, message: Message):
        # Called when STT returns a command. Then we send a TTS response.
        # For now, ResponseWorker already does that, but we need to track state:
        if self.state == "listening":
            # after response is sent, we'll stay in listening until response TTS finishes?
            # Actually, ResponseWorker sends TTS_REQUEST and then TTSWorker publishes TTS_FINISHED.
            # So we don't need to change state here; on_tts_finished will handle it.
            pass