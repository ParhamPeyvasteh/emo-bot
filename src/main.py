import asyncio
import signal
from src.core.config import settings
from src.core.message_bus import MessageBus
from src.workers.audio_capture import AudioCaptureWorker
from src.workers.wake_word import WakeWordWorker
# ... other workers

async def main():
    bus = MessageBus()
    bus.start()
    
    # Instantiate workers (order matters for subscriptions)
    workers = [
        AudioCaptureWorker(bus, settings),
        WakeWordWorker(bus, settings),
        # STT, emotion, etc. will be added later
    ]
    
    # Start them concurrently
    await asyncio.gather(*[w.start() for w in workers])
    
    # Graceful shutdown
    stop_event = asyncio.Event()
    def handle_signal():
        stop_event.set()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal)
    
    await stop_event.wait()
    # Cancel all workers (they should clean up)
    for w in workers:
        await w.stop()

if __name__ == "__main__":
    asyncio.run(main())