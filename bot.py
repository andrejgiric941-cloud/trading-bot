import os
from telegram.ext import Updater, CommandHandler

# Забираем токен из переменной окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")

def start(update, context):
    update.message.reply_text("Привет! Бот запущен и готов слушать команды ✅")

def help_command(update, context):
    update.message.reply_text("Команды: /start и /help")

def main():
    if not TOKEN:
        raise RuntimeError("Ошибка: TELEGRAM_TOKEN не задан в Config Vars!")

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # Удаляем вебхук (если был) и запускаем polling
    updater.bot.delete_webhook()
    print("Бот успешно запущен, слушает polling...")
    updater.start_polling()
    updater.idle()

if name == "__main__":
    main()
