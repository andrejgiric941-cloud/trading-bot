        import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def start(update, context):
    update.message.reply_text("Бот запущен ✅")

def handle_text(update, context):
    txt = (update.message.text or "").strip()
    update.message.reply_text(f"Принял: «{txt}»")

def main():
    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Нет TELEGRAM_TOKEN")
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    logging.info("Бот успешно запущен, слушает polling...")
    updater.start_polling(drop_pending_updates=True, timeout=30)
    updater.idle()

if name == "__main__":
    main()
