import asyncio
from typing import Dict, List, Callable, Awaitable
from src.messages import Message, EventType

class MessageBus:
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Message], Awaitable[None]]]] = {}
        self._queue = asyncio.Queue()
        self._running = False

    def subscribe(self, event_type: EventType, callback: Callable[[Message], Awaitable[None]]):
        self._subscribers.setdefault(event_type, []).append(callback)

    async def publish(self, message: Message):
        await self._queue.put(message)

    async def _dispatch(self):
        while self._running:
            msg = await self._queue.get()
            for callback in self._subscribers.get(msg.type, []):
                asyncio.create_task(callback(msg))

    def start(self):
        self._running = True
        asyncio.create_task(self._dispatch())