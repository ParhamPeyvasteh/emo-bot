import json
import asyncio
from datetime import datetime
from pathlib import Path
from src.core.message_bus import MessageBus, EventType, Message
from src.workers.base_worker import BaseWorker
from src.core.logging_config import setup_logging

logger = setup_logging()

class CacheWorker(BaseWorker):
    def __init__(self, bus: MessageBus):
        super().__init__(bus)
        self.cache_file = Path("user_inputs.json")
        self.lock = asyncio.Lock()
        self.bus.subscribe(EventType.USER_TRANSCRIPT, self.save_transcript)

    async def run(self):
        # Ensure the cache file exists with an empty array
        if not self.cache_file.exists():
            with open(self.cache_file, "w") as f:
                json.dump([], f)
        logger.info(f"CacheWorker ready, saving to {self.cache_file}")
        while True:
            await asyncio.sleep(1)

    async def save_transcript(self, message: Message):
        text = message.payload.get("text", "").strip()
        if not text:
            return
        entry = {
            "timestamp": datetime.now().isoformat(),
            "text": text
        }
        async with self.lock:
            try:
                # Read existing data
                with open(self.cache_file, "r") as f:
                    data = json.load(f)
                # Append new entry
                data.append(entry)
                # Write back
                with open(self.cache_file, "w") as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Cached user input: '{text}'")
            except Exception as e:
                logger.error(f"Failed to write to cache: {e}")