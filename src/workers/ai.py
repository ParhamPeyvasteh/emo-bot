import json
import asyncio
import httpx
from src.core.message_bus import MessageBus, EventType, Message
from src.workers.base_worker import BaseWorker
from src.core.config import settings
from src.core.logging_config import setup_logging

logger = setup_logging()

class AIWorker(BaseWorker):
    def __init__(self, bus: MessageBus):
        super().__init__(bus)
        self.api_url = settings.ai_api_url
        self.api_key = settings.ai_api_key
        self.model = settings.ai_model
        self.timeout = settings.ai_timeout
        self.bus.subscribe(EventType.USER_TRANSCRIPT, self.handle_user_input)

    async def run(self):
        if not self.api_key:
            logger.warning("AI_API_KEY not set – AIWorker will not function")
        logger.info("AIWorker ready")
        while True:
            await asyncio.sleep(1)

    async def handle_user_input(self, message: Message):
        user_text = message.payload.get("text", "").strip()
        if not user_text:
            return
        logger.info(f"[AI] Sending to AI: {user_text}")

        # Build prompt (you can include conversation history from cache if desired)
        prompt = f"User said: {user_text}\nAssistant response (short, friendly, one sentence):"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are Emo, a helpful voice assistant for a smart robot. Keep answers very short (one sentence)."},
                {"role": "user", "content": user_text}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.api_url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                # Handle both OpenAI and GapGPT formats
                if "choices" in result:
                    assistant_text = result["choices"][0]["message"]["content"].strip()
                else:
                    # Fallback – try to extract
                    assistant_text = result.get("response", result.get("text", "Sorry, I could not understand."))
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