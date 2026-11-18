import re
from urllib.parse import urlparse, urlunparse

YOUTUBE_HOSTS = {"youtube.com", "youtu.be", "youtube-nocookie.com"}
INSTAGRAM_HOSTS = {"instagram.com", "instagr.am"}


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url.strip())
        return (
            parsed.scheme.lower() in ("http", "https")
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
        )
    except (TypeError, ValueError):
        return False


def _host_matches(host: str | None, allowed: set[str]) -> bool:
    if not host:
        return False
    host = host.lower().rstrip(".")
    return any(host == domain or host.endswith("." + domain) for domain in allowed)


def is_youtube_url(url: str) -> bool:
    try:
        return _host_matches(urlparse(url).hostname, YOUTUBE_HOSTS)
    except (TypeError, ValueError):
        return False


def is_instagram_url(url: str) -> bool:
    try:
        return _host_matches(urlparse(url).hostname, INSTAGRAM_HOSTS)
    except (TypeError, ValueError):
        return False


def clean_filename(filename: str) -> str:
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename)
    return filename.strip(" .")[:150] or "media"


def extract_supported_url(text: str) -> str | None:
    """Extract the first supported YouTube/Instagram URL from a message."""
    if not isinstance(text, str):
        return None
    for match in re.finditer(r"https?://[^\s<>\"']+", text, flags=re.IGNORECASE):
        candidate = match.group(0).rstrip(".,!?;:)]}")
        if is_valid_url(candidate) and (is_youtube_url(candidate) or is_instagram_url(candidate)):
            return candidate
    return None


def normalize_url(url: str) -> str:
    """Remove surrounding whitespace without changing signed/query parameters."""
    return url.strip()
