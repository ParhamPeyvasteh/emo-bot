from abc import ABC, abstractmethod
import asyncio
from src.core.message_bus import MessageBus
from src.core.logging_config import setup_logging

logger = setup_logging()

class BaseWorker(ABC):
    def __init__(self, bus: MessageBus):
        self.bus = bus
        self._task = None

    @abstractmethod
    async def run(self):
        pass

    async def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self.run())
            logger.info(f"{self.__class__.__name__} started")

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            logger.info(f"{self.__class__.__name__} stopped")