import asyncio
from openai import OpenAI
from src.core.message_bus import MessageBus, EventType, Message
from src.workers.base_worker import BaseWorker
from src.core.logging_config import setup_logging
from src.core.config import settings

logger = setup_logging()

# Configure GapGPT client
API_KEY = settings.ai_api_key
BASE_URL = settings.ai_api_url
MODEL = settings.ai_model

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

class AIWorker(BaseWorker):
    def __init__(self, bus: MessageBus):
        super().__init__(bus)
        self.bus.subscribe(EventType.USER_TRANSCRIPT, self.handle_user_input)

    async def run(self):
        logger.info("AIWorker ready (GapGPT)")
        while True:
            await asyncio.sleep(1)

    async def handle_user_input(self, message: Message):
        user_text = message.payload.get("text", "").strip()
        if not user_text:
            return

        logger.info(f"[AI] Sending to GapGPT: {user_text}")

        try:
            # Run the synchronous OpenAI call in a thread pool to avoid blocking
            response = await asyncio.to_thread(
                client.responses.create,
                model=MODEL,
                input=user_text
            )
            assistant_text = response.output_text.strip()
            logger.info(f"[AI] Response: {assistant_text}")
            await self.bus.publish(Message(
                type=EventType.TTS_REQUEST,
                payload={"text": assistant_text}
            ))
        except Exception as e:
            logger.error(f"[AI] API call failed: {e}")
            fallback = "Sorry, I'm having trouble thinking right now."
            await self.bus.publish(Message(
                type=EventType.TTS_REQUEST,
                payload={"text": fallback}
            ))