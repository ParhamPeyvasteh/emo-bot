import asyncio
from typing import Dict, List, Callable, Awaitable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from .logging_config import setup_logging

logger = setup_logging()

class EventType(Enum):
    AUDIO_CHUNK = "audio_chunk"
    WAKE_WORD_DETECTED = "wake_word_detected"
    VAD_SPEECH_SEGMENT = "vad_speech_segment"
    USER_TRANSCRIPT = "user_transcript"
    USER_EMOTION = "user_emotion"
    LLM_REQUEST = "llm_request"
    ASSISTANT_RESPONSE = "assistant_response"
    ASSISTANT_EMOTION = "assistant_emotion"
    TTS_REQUEST = "tts_request"
    AUDIO_OUTPUT = "audio_output"
    BLE_COMMAND = "ble_command"
    SYSTEM_ERROR = "system_error"

@dataclass
class Message:
    type: EventType
    payload: any
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().timestamp()

class MessageBus:
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Message], Awaitable[None]]]] = {}
        self._queue = asyncio.Queue()
        self._running = False
        self._dispatch_task = None

    def subscribe(self, event_type: EventType, callback: Callable[[Message], Awaitable[None]]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed callback to {event_type.value}")

    async def publish(self, message: Message):
        await self._queue.put(message)
        logger.debug(f"Published message: {message.type.value}")

    async def _dispatch(self):
        while self._running:
            try:
                msg = await self._queue.get()
                if msg.type in self._subscribers:
                    for callback in self._subscribers[msg.type]:
                        asyncio.create_task(callback(msg))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error dispatching message {msg.type}: {e}")

    def start(self):
        if self._running:
            logger.warning("Message bus already running")
            return
        self._running = True
        self._dispatch_task = asyncio.create_task(self._dispatch())
        logger.info("Message bus started")

    async def stop(self):
        if not self._running:
            return
        self._running = False
        if self._dispatch_task:
            self._dispatch_task.cancel()
            try:
                await self._dispatch_task
            except asyncio.CancelledError:
                pass
        logger.info("Message bus stopped")