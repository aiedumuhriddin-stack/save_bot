import logging
import os

from config import LOG_DIR

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "bot.log"), encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("video_downloader_bot")

# Telegram's HTTP request URLs contain the bot token. Never log them.
for name in ("httpx", "httpcore", "telegram", "telegram.ext", "telegram.request"):
    logging.getLogger(name).setLevel(logging.WARNING)
