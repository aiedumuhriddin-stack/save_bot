import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
DOWNLOAD_DIR = str(BASE_DIR / "downloads")
LOG_DIR = str(BASE_DIR / "logs")
FFMPEG_DIR = os.getenv("FFMPEG_DIR", "").strip() or None

# Telegram cloud Bot API upload limit is around 50 MB; leave a safety margin.
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "48"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
# Source files may be larger than the Telegram limit: videos are compressed locally.
MAX_SOURCE_FILE_SIZE_MB = int(os.getenv("MAX_SOURCE_FILE_SIZE_MB", "500"))
MAX_SOURCE_FILE_SIZE_BYTES = MAX_SOURCE_FILE_SIZE_MB * 1024 * 1024

if not BOT_TOKEN or BOT_TOKEN.startswith("PASTE_"):
    raise ValueError("BOT_TOKEN topilmadi. .env fayliga yangi Telegram bot tokenini yozing.")
if not 1 <= MAX_FILE_SIZE_MB <= 49:
    raise ValueError("MAX_FILE_SIZE_MB 1 dan 49 gacha bo'lishi kerak.")
if MAX_SOURCE_FILE_SIZE_MB < MAX_FILE_SIZE_MB:
    raise ValueError("MAX_SOURCE_FILE_SIZE_MB MAX_FILE_SIZE_MB dan katta bo'lishi kerak.")
