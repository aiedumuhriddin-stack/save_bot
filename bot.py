from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from handlers.callbacks import (
    audio_selected,
    choose_video,
)
from handlers.download import handle_url
from handlers.start import cancel_command, start_command
from utils.logger import logger


def main() -> None:
    print("🤖 SAVE BOT ishga tushmoqda...")
    application = Application.builder().token(BOT_TOKEN).concurrent_updates(8).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    application.add_handler(CallbackQueryHandler(choose_video, pattern=r"^choose_video$"))
    application.add_handler(CallbackQueryHandler(audio_selected, pattern=r"^audio$"))

    async def on_error(update, context):
        error = context.error
        logger.error("Update xatosi: %s", type(error).__name__ if error else "unknown")

    application.add_error_handler(on_error)
    print("✅ Bot polling rejimida ishga tushdi. To'xtatish: Ctrl+C")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
