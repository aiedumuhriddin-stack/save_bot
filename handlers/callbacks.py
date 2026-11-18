import asyncio
import os
import re
import shutil

from telegram import Update
from telegram.ext import ContextTypes

from config import DOWNLOAD_DIR, MAX_FILE_SIZE_BYTES
from services.youtube import download_youtube_audio, download_youtube_video
from services.instagram import download_instagram_audio, download_instagram_video
from utils.helpers import is_youtube_url, is_instagram_url
from utils.logger import logger

_DOWNLOAD_SLOTS = asyncio.Semaphore(3)


def _safe_error(error: Exception) -> str:
    message = str(error) or type(error).__name__
    message = re.sub(r"https?://\S+", "[URL yashirildi]", message)
    message = re.sub(r"\b\d{8,}:AA[A-Za-z0-9_-]+", "[TOKEN yashirildi]", message)
    return message[:700]


async def _owns_prompt(query, context: ContextTypes.DEFAULT_TYPE) -> bool:
    owner_id = context.user_data.get("url_owner_id")
    prompt = context.user_data.get("url_prompt")
    message = query.message
    owns = (
        message is not None
        and owner_id == query.from_user.id
        and prompt == (message.chat_id, message.message_id)
    )
    if not owns:
        await query.answer("Bu tugma boshqa foydalanuvchi uchun yoki eskirgan.", show_alert=True)
    return owns


def _download_function(url: str, kind: str):
    if is_youtube_url(url):
        return download_youtube_video if kind == "video" else download_youtube_audio
    if is_instagram_url(url):
        return download_instagram_video if kind == "video" else download_instagram_audio
    raise ValueError("Faqat YouTube va Instagram havolalari qo'llab-quvvatlanadi.")


def _remove_download(filepath: str | None) -> None:
    if not filepath:
        return
    try:
        parent = os.path.abspath(os.path.dirname(filepath))
        root = os.path.abspath(DOWNLOAD_DIR)
        if os.path.commonpath((root, parent)) == root and parent != root:
            shutil.rmtree(parent, ignore_errors=True)
    except (OSError, ValueError):
        logger.exception("Vaqtinchalik yuklama papkasini tozalab bo'lmadi")


def _user_error(error: Exception) -> str:
    text = str(error).lower()
    if "ffmpeg" in text:
        return "FFmpeg tayyor emas. Bot papkasida: python -m pip install -r requirements.txt buyrug'ini bajaring."
    if "limit" in text or "mb dan katta" in text:
        return "Fayl hajmi juda katta. Boshqa video yoki MP3 formatini tanlang."
    if "private" in text or "login" in text or "sign in" in text:
        return "Bu kontent yopiq yoki login talab qiladi. Faqat ommaga ochiq havolani yuboring."
    if "unsupported url" in text:
        return "Bu havola turi qo'llab-quvvatlanmaydi. YouTube yoki Instagram linkini yuboring."
    if "429" in text or "too many requests" in text:
        return "Platforma vaqtincha ko'p so'rov sabab chekladi. Biroz kutib qayta urinib ko'ring."
    if "video unavailable" in text or "not available" in text:
        return "Video mavjud emas, o'chirilgan yoki hududiy cheklovda."
    return "Yuklash amalga oshmadi. Birozdan so'ng qayta urinib ko'ring. Agar xato takrorlansa, administrator logs/bot.log faylini tekshirishi kerak."


async def choose_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not await _owns_prompt(query, context):
        return
    await _download_and_send(update, context, "video")


async def audio_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not await _owns_prompt(query, context):
        return
    await _download_and_send(update, context, "audio")


async def _download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str):
    query = update.callback_query
    if context.user_data.get("download_in_progress"):
        await query.answer("Yuklash allaqachon davom etmoqda", show_alert=True)
        return
    context.user_data["download_in_progress"] = True
    filepath = None
    try:
        await query.answer()
        url = context.user_data.get("url")
        if not url or not (is_youtube_url(url) or is_instagram_url(url)):
            await query.edit_message_text("Havola topilmadi yoki noto'g'ri. Linkni qaytadan yuboring.")
            return

        label = "MP4 video" if kind == "video" else "MP3 audio"
        await query.edit_message_text(
            f"⏳ {label} tayyorlanmoqda...\n\n"
            "Video hajmi Telegram limitidan katta bo'lsa, avtomatik siqiladi."
        )

        async with _DOWNLOAD_SLOTS:
            downloader = _download_function(url, kind)
            # yt-dlp and FFmpeg are blocking programs; keep them off the
            # Telegram event loop so the bot can answer other users meanwhile.
            filepath, title = await asyncio.to_thread(downloader, url)

        if not filepath or not os.path.isfile(filepath):
            raise FileNotFoundError("Yuklangan fayl topilmadi.")
        if os.path.getsize(filepath) > MAX_FILE_SIZE_BYTES:
            raise ValueError("Tayyor fayl Telegram yuborish limitidan katta.")

        await query.edit_message_text("📤 Fayl Telegramga yuborilmoqda...")
        with open(filepath, "rb") as media:
            if kind == "video":
                await query.message.reply_video(
                    video=media,
                    caption=f"🎬 {title[:900]}",
                    supports_streaming=True,
                    read_timeout=180,
                    write_timeout=180,
                    connect_timeout=30,
                    pool_timeout=30,
                )
            else:
                await query.message.reply_audio(
                    audio=media,
                    title=title[:64],
                    performer="SAVE BOT",
                    read_timeout=180,
                    write_timeout=180,
                    connect_timeout=30,
                    pool_timeout=30,
                )

        if context.user_data.get("url") == url:
            context.user_data.pop("url", None)
            context.user_data.pop("url_owner_id", None)
            context.user_data.pop("url_prompt", None)
        logger.info("%s fayl yuborildi (user_id=%s)", kind, query.from_user.id)
        await query.message.reply_text("✅ Tayyor! Yana YouTube yoki Instagram havolasini yuboring.")
    except Exception as error:
        logger.error("%s yuklash/yuborish xatosi: %s: %s", kind, type(error).__name__, _safe_error(error))
        try:
            await query.message.reply_text(f"❌ {_user_error(error)}")
        except Exception:
            logger.exception("Xatolik xabarini foydalanuvchiga yuborib bo'lmadi")
    finally:
        _remove_download(filepath)
        context.user_data.pop("download_in_progress", None)
