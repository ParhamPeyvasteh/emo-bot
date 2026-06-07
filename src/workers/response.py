import asyncio
from src.core.message_bus import MessageBus, EventType, Message
from src.workers.base_worker import BaseWorker
from src.core.logging_config import setup_logging

logger = setup_logging()

class ResponseWorker(BaseWorker):
    def __init__(self, bus: MessageBus):
        super().__init__(bus)
        self.bus.subscribe(EventType.USER_TRANSCRIPT, self.handle_transcript)

    async def run(self):
        while True:
            await asyncio.sleep(1)

    async def handle_transcript(self, message: Message):
        user_text = message.payload.get("text", "")
        logger.info(f"User said: {user_text}")
        # Simple canned response
        response_text = f"You said: {user_text}. I am Emo Bot, your assistant."
        logger.info(f"Response: {response_text}")
        await self.bus.publish(Message(
            type=EventType.TTS_REQUEST,
            payload={"text": response_text}
        ))