from services.downloader import download_video
from services.converter import download_audio


def download_instagram_video(url: str):
    return download_video(url)


def download_instagram_audio(url: str):
    return download_audio(url)
