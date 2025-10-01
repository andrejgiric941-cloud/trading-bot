import os
from telegram.ext import Updater, CommandHandler

# Забираем токен из переменной окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")

def start(update, context):
    update.message.reply_text("Привет! Бот запущен и готов слушать команды.")

def help_command(update, context):
    update.message.reply_text("Напиши /start чтобы проверить работу бота.")

def main():
    if not TOKEN:
        print("Ошибка: токен не найден. Проверь, что TELEGRAM_TOKEN задан в Config Vars на Heroku.")
        return

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # команды
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    print("Бот запущен...")
    updater.start_polling()
    updater.idle()

if name == "__main__":
    main()
