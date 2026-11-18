import os

import yt_dlp

from config import DOWNLOAD_DIR, MAX_FILE_SIZE_BYTES
from services.downloader import (
    _base_options,
    _download_dir,
    _ffmpeg_options,
    _remove_job_dir,
)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_audio(url: str):
    job_dir = _download_dir()
    output_template = os.path.join(job_dir, "%(id)s.%(ext)s")
    options = _base_options(output_template)
    options.update(_ffmpeg_options())
    options.update({
        # Prefer M4A audio where possible; it is commonly a direct stream and
        # avoids an unnecessary container conversion before MP3 encoding.
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
    })

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title") or "audio"

        candidates = [
            os.path.join(job_dir, name)
            for name in os.listdir(job_dir)
            if os.path.isfile(os.path.join(job_dir, name)) and name.lower().endswith(".mp3")
        ]
        if not candidates:
            raise FileNotFoundError("MP3 fayli yaratilmadi.")
        filepath = max(candidates, key=os.path.getmtime)
        if os.path.getsize(filepath) > MAX_FILE_SIZE_BYTES:
            raise ValueError(
                "MP3 fayli Telegram yuborish limitidan katta. Qisqaroq audio tanlang."
            )
        return filepath, title
    except Exception:
        _remove_job_dir(job_dir)
        raise
