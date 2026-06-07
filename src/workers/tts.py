# src/workers/tts.py
import asyncio
import subprocess
from src.core.message_bus import MessageBus, EventType, Message
from src.workers.base_worker import BaseWorker
from src.core.logging_config import setup_logging

logger = setup_logging()

class TTSWorker(BaseWorker):
    def __init__(self, bus: MessageBus):
        super().__init__(bus)
        self.bus.subscribe(EventType.TTS_REQUEST, self.speak)

    async def run(self):
        while True:
            await asyncio.sleep(1)

    async def speak(self, message: Message):
        text = message.payload.get("text", "")
        if not text:
            return
        logger.info(f"[TTS] Speaking: {text}")
        safe_text = text.replace('"', '\\"')
        ps_cmd = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak("{safe_text}")'
        await asyncio.to_thread(subprocess.run, ["powershell", "-Command", ps_cmd], capture_output=True)
        logger.info("[TTS] Speech finished")
        # Notify that TTS is done
        await self.bus.publish(Message(type=EventType.TTS_FINISHED, payload={"text": text}))