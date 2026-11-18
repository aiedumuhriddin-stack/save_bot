from services.downloader import download_video
from services.converter import download_audio


def download_youtube_video(url: str):
    return download_video(url)


def download_youtube_audio(url: str):
    return download_audio(url)
