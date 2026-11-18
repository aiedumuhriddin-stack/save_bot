import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import yt_dlp

from config import (
    DOWNLOAD_DIR,
    FFMPEG_DIR,
    MAX_FILE_SIZE_BYTES,
    MAX_SOURCE_FILE_SIZE_BYTES,
)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _download_dir() -> str:
    return tempfile.mkdtemp(prefix="job_", dir=DOWNLOAD_DIR)


def _remove_job_dir(path: str) -> None:
    shutil.rmtree(path, ignore_errors=True)


def _ffmpeg_executable() -> str:
    """Find FFmpeg from explicit config, PATH, or the bundled imageio-ffmpeg wheel."""
    candidates = []
    if FFMPEG_DIR:
        candidates.extend([
            os.path.join(FFMPEG_DIR, "ffmpeg.exe" if os.name == "nt" else "ffmpeg"),
            FFMPEG_DIR,
        ])
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        candidates.append(system_ffmpeg)

    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate

    try:
        import imageio_ffmpeg
        bundled = imageio_ffmpeg.get_ffmpeg_exe()
        if bundled and os.path.isfile(bundled):
            return bundled
    except Exception:
        pass

    raise RuntimeError(
        "FFmpeg topilmadi. requirements.txt dagi imageio-ffmpeg kutubxonasini "
        "o'rnating yoki FFmpeg'ni PATH ga qo'shing."
    )


def _ffmpeg_options() -> dict:
    return {"ffmpeg_location": _ffmpeg_executable()}


def _size_limit_hook(status: dict) -> None:
    if status.get("status") != "downloading":
        return
    total = status.get("total_bytes") or status.get("total_bytes_estimate")
    downloaded = status.get("downloaded_bytes", 0)
    if (total and total > MAX_SOURCE_FILE_SIZE_BYTES) or downloaded > MAX_SOURCE_FILE_SIZE_BYTES:
        raise ValueError(
            f"Manba fayl {MAX_SOURCE_FILE_SIZE_BYTES // (1024 * 1024)} MB dan katta."
        )


def _base_options(output_template: str) -> dict:
    return {
        "outtmpl": output_template,
        "noplaylist": True,
        # Shorter network timeouts/retries prevent a dead connection from
        # leaving a user's request apparently stuck for several minutes.
        "socket_timeout": 15,
        "retries": 2,
        "fragment_retries": 2,
        "extractor_retries": 2,
        "file_access_retries": 2,
        "concurrent_fragment_downloads": 4,
        "buffersize": 1024 * 1024,
        "progress_hooks": [_size_limit_hook],
        "quiet": True,
        "no_warnings": True,
        "overwrites": True,
        "continuedl": False,
        "windowsfilenames": True,
    }


def _compress_video_if_needed(filepath: str, duration: float | None) -> str:
    """Return an MP4 that fits Telegram's upload limit, transcoding only when needed."""
    needs_mp4 = Path(filepath).suffix.lower() != ".mp4"
    too_large = os.path.getsize(filepath) > MAX_FILE_SIZE_BYTES
    if not needs_mp4 and not too_large:
        return filepath
    if not duration or duration <= 0:
        raise ValueError("Video davomiyligini aniqlab bo'lmadi; MP4 tayyorlanmadi.")

    ffmpeg = _ffmpeg_executable()
    output = str(Path(filepath).with_name("telegram_ready.mp4"))
    # Aim for 46 MiB to leave room for container overhead and Telegram's limit.
    target_bytes = 46 * 1024 * 1024
    audio_kbps = 96
    total_kbps = int((target_bytes * 8 / duration) / 1000)
    video_kbps = max(250, total_kbps - audio_kbps)

    command = [
        ffmpeg, "-y", "-i", filepath,
        "-map", "0:v:0", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "ultrafast", "-threads", "0",
        "-b:v", f"{video_kbps}k", "-maxrate", f"{video_kbps}k",
        "-bufsize", f"{video_kbps * 2}k",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", f"{audio_kbps}k",
        "-movflags", "+faststart", "-t", str(duration), output,
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0 or not os.path.isfile(output):
        details = (result.stderr or "FFmpeg xatosi")[-1200:]
        raise RuntimeError(f"Video MP4 formatiga o'tkazilmadi: {details}")
    if os.path.getsize(output) > MAX_FILE_SIZE_BYTES:
        os.remove(output)
        raise ValueError(
            "Video Telegram yuborish limitidan katta bo'lib qoldi. "
            "Qisqaroq video yoki MP3 formatini tanlang."
        )
    os.remove(filepath)
    return output


def download_video(url: str):
    job_dir = _download_dir()
    output_template = os.path.join(job_dir, "%(id)s.%(ext)s")
    options = _base_options(output_template)
    options.update(_ffmpeg_options())
    options.update({
        # Prefer a single pre-merged MP4 stream: avoids downloading separate
        # video/audio tracks and waiting for an FFmpeg merge. Falls back to the
        # best single-file format if MP4 is unavailable.
        "format": "best[ext=mp4]/best",
        "merge_output_format": "mp4",
    })

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title") or "video"
            duration = info.get("duration")

        candidates = [
            os.path.join(job_dir, name)
            for name in os.listdir(job_dir)
            if os.path.isfile(os.path.join(job_dir, name))
            and not name.endswith(".part")
            and Path(name).suffix.lower() in (".mp4", ".mkv", ".webm", ".mov", ".m4v")
        ]
        if not candidates:
            raise FileNotFoundError("Yuklangan video fayli topilmadi.")
        filepath = max(candidates, key=os.path.getmtime)
        filepath = _compress_video_if_needed(filepath, duration)
        return filepath, title
    except Exception:
        _remove_job_dir(job_dir)
        raise
