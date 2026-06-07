import sys
from loguru import logger
from .config import settings

def setup_logging():
    """Configure application-wide logging."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    logger.add(
        "logs/emo-bot.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    return logger