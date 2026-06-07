import asyncio
from typing import Dict, List, Callable, Awaitable
from enum import Enum
from dataclasses import dataclass, field
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
    TTS_FINISHED = "tts_finished"
    START_LISTENING = "start_listening"

@dataclass
class Message:
    type: EventType
    payload: any
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

class MessageBus:
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Message], Awaitable[None]]]] = {}
        self._queue = asyncio.Queue()
        self._running = False
        self._dispatch_task = None

    def subscribe(self, event_type: EventType, callback: Callable[[Message], Awaitable[None]]):
        self._subscribers.setdefault(event_type, []).append(callback)
        logger.debug(f"Subscribed to {event_type.value}")

    async def publish(self, message: Message):
        await self._queue.put(message)
        logger.debug(f"Published {message.type.value}")

    async def _dispatch(self):
        while self._running:
            try:
                msg = await self._queue.get()
                for callback in self._subscribers.get(msg.type, []):
                    asyncio.create_task(callback(msg))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Dispatch error: {e}")

    def start(self):
        if not self._running:
            self._running = True
            self._dispatch_task = asyncio.create_task(self._dispatch())
            logger.info("Message bus started")

    async def stop(self):
        if self._running:
            self._running = False
            if self._dispatch_task:
                self._dispatch_task.cancel()
                await self._dispatch_task
            logger.info("Message bus stopped")