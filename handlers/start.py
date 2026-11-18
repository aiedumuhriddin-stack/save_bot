from telegram import Update
from telegram.ext import ContextTypes


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name if user and user.first_name else "do'stim"
    context.user_data.pop("url", None)
    context.user_data.pop("url_prompt", None)
    await update.effective_message.reply_text(
        f"👋 Salom, {name}!\n\n"
        "🎬 SAVE BOT'ga xush kelibsiz.\n\n"
        "YouTube yoki Instagram havolasini yuboring.\n"
        "Keyin formatni tanlang:\n"
        "🎥 Video — MP4 (avtomatik sifat)\n"
        "🎵 Audio — MP3\n\n"
        "ℹ️ Faqat o'zingiz yuklashga ruxsatingiz bo'lgan, ommaga ochiq kontentdan foydalaning.\n"
        "Bekor qilish: /cancel"
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("download_in_progress"):
        await update.effective_message.reply_text(
            "Yuklash allaqachon boshlangan. U tugaguncha kuting; keyingi so'rovni bekor qildim."
        )
        return
    context.user_data.pop("url", None)
    context.user_data.pop("url_prompt", None)
    await update.effective_message.reply_text("✅ Tanlangan havola bekor qilindi. Yangi link yuborishingiz mumkin.")
