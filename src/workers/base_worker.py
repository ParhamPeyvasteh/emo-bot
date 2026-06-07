from abc import ABC, abstractmethod
from src.core.message_bus import MessageBus
from src.core.config import Settings

class BaseWorker(ABC):
    def __init__(self, bus: MessageBus, settings: Settings):
        self.bus = bus
        self.settings = settings
        self._task = None

    @abstractmethod
    async def run(self):
        """Main worker loop"""
        pass

    async def start(self):
        self._task = asyncio.create_task(self.run())

    async def stop(self):
        if self._task:
            self._task.cancel()