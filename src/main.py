import asyncio
from src.core.message_bus import MessageBus
from src.core.logging_config import setup_logging
from src.workers.audio_capture import AudioCaptureWorker
from src.workers.wake_word import WakeWordWorker

logger = setup_logging()

async def main():
    logger.info("Starting Emo-Bot Voice Assistant")

    bus = MessageBus()
    bus.start()

    workers = [
        AudioCaptureWorker(bus),
        WakeWordWorker(bus),
    ]

    for w in workers:
        await w.start()

    logger.info("All workers started. Say your wake word.")

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Stopping workers...")
        for w in workers:
            await w.stop()
        await bus.stop()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")