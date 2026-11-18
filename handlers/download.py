from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from utils.helpers import extract_supported_url, is_youtube_url, is_instagram_url
from utils.logger import logger


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message is None or not message.text:
        return

    if context.user_data.get("download_in_progress"):
        await message.reply_text("⏳ Joriy yuklash tugashini kuting, keyin yangi havola yuboring.")
        return

    # Accept a plain URL, a URL surrounded by explanatory text, or a Telegram
    # text-link entity. Do not accept arbitrary domains or URL lookalikes.
    url = next(
        (entity.url for entity in (message.entities or [])
         if entity.type == "text_link" and entity.url
         and (is_youtube_url(entity.url) or is_instagram_url(entity.url))),
        None,
    )
    url = url or extract_supported_url(message.text)
    if not url:
        await message.reply_text(
            "❌ YouTube yoki Instagram havolasini yuboring.\n"
            "Masalan: https://youtu.be/... yoki https://www.instagram.com/reel/..."
        )
        return

    context.user_data["url"] = url
    context.user_data["url_owner_id"] = update.effective_user.id
    platform = "YouTube" if is_youtube_url(url) else "Instagram"
    logger.info("%s havola qabul qilindi (user_id=%s)", platform, update.effective_user.id)

    keyboard = [
        [InlineKeyboardButton("🎥 Video (MP4)", callback_data="choose_video")],
        [InlineKeyboardButton("🎵 Audio (MP3)", callback_data="audio")],
    ]
    prompt = await message.reply_text(
        f"✅ {platform} havolasi qabul qilindi.\n\nQaysi formatda yuklaymiz?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    context.user_data["url_prompt"] = (prompt.chat_id, prompt.message_id)
