import asyncio
import signal
from src.core.message_bus import MessageBus
from src.core.logging_config import setup_logging
from src.workers.audio_capture import AudioCaptureWorker
from src.workers.wake_word import WakeWordWorker
from src.workers.stt import STTWorker
from src.workers.emotion import EmotionWorker
from src.workers.llm import LLMWorker
from src.workers.tts import TTSWorker
from src.workers.ble import BLEWorker

logger = setup_logging()

async def main():
    logger.info("Starting Emo-Bot Voice Assistant")
    
    # Initialize message bus
    bus = MessageBus()
    bus.start()
    
    # Initialize workers
    workers = [
        AudioCaptureWorker(bus),
        WakeWordWorker(bus),
        STTWorker(bus),
        EmotionWorker(bus),
        LLMWorker(bus),
        TTSWorker(bus),
        BLEWorker(bus),
    ]
    
    # Start all workers concurrently
    for worker in workers:
        await worker.start()
    
    logger.info("All workers started successfully")
    
    # Graceful shutdown handling
    stop_event = asyncio.Event()
    def handle_signal():
        logger.info("Shutdown signal received")
        stop_event.set()
    
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal)
    
    await stop_event.wait()
    
    # Stop all workers
    logger.info("Stopping workers...")
    for worker in workers:
        await worker.stop()
    
    await bus.stop()
    logger.info("Emo-Bot shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        raise