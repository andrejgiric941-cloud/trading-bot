import os
import re
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

VALID_AMOUNTS = {40, 100, 220}
VALID_MINUTES = {1, 2, 3, 4}

# Нормализация русских валютных слов в ISO-коды
RU_TO_ISO = {
    "ЕВРО": "EUR",
    "ДОЛЛАР": "USD", "ДОЛЛАРЫ": "USD", "ЮСД": "USD", "УСД": "USD",
    "ИЕНА": "JPY", "ЙЕНА": "JPY",
    "ФУНТ": "GBP", "СТЕРЛИНГ": "GBP",
    "ФРАНК": "CHF",
    "КАНАДЕЦ": "CAD", "КАНАДСКИЙ": "CAD",
    "АВСТРАЛИЕЦ": "AUD", "АВСТРАЛИЙСКИЙ": "AUD",
    "НОВОЗЕЛАНДЕЦ": "NZD", "КИВИ": "NZD",
    "РУБЛЬ": "RUB", "РУБ": "RUB",
}

def normalize_text(s: str) -> str:
    t = (s or "").upper()
    t = re.sub(r"[,$]", " ", t)
    t = re.sub(r"\bНА\b", " ", t)
    t = re.sub(r"\bМИН(?:УТА|УТЫ|УТ)?\b", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def build_symbol(first: str, second: str):
    a = RU_TO_ISO.get(first, first)
    b = RU_TO_ISO.get(second, second)
    if re.fullmatch(r"[A-Z]{3}", a) and re.fullmatch(r"[A-Z]{3}", b):
        return a + b
    return None

def parse_command(text: str):
    """
    Принимает:
      EURUSD 1 вверх 40
      EURUSD OTC 1 вверх 40
      ЕВРО USD 1 вверх 40
      ЕВРО USD OTC 1 вверх 40 $
    Минуты: 1–4; Сумма: 40/100/220; Направление: вверх/вниз или up/down
    """
    t = normalize_text(text)
    tokens = t.split()
    if not tokens:
        return None, "Пустая команда."

    # Найти 'OTC' (необязателен)
    i_otc = -1
    for i, tok in enumerate(tokens):
        if tok == "OTC":
            i_otc = i
            break

    # Пара слева от OTC (или с начала)
    left_end = i_otc if i_otc != -1 else len(tokens)
    if left_end < 1:
        return None, "Не вижу валютную пару."

    symbol = None
    used_left = 0

    # Вариант 1: один токен типа EURUSD
    if re.fullmatch(r"[A-Z]{6,10}", tokens[0]):
        symbol = tokens[0]
        used_left = 1

    # Вариант 2: два токена: ЕВРО USD / EUR USD
    if not symbol and left_end >= 2:
        symbol = build_symbol(tokens[0], tokens[1])
        if symbol:
            used_left = 2

    if not symbol:
        return None, "❌ Пара не распознана. Пример: EURUSD 1 вверх 40 или Евро USD 1 вверх 40"

    # Хвост после пары и (опционального) OTC
    rest = tokens[used_left:]
    if rest and rest[0] == "OTC":
        rest = rest[1:]

    if not rest:
        return None, "❌ Укажи время, направление и сумму. Пример: EURUSD 1 вверх 40"

    # Минуты
    if not rest[0].isdigit():
        return None, "❌ Время укажи числом от 1 до 4."
    minutes = int(rest[0])
    if minutes not in VALID_MINUTES:
        return None, "❌ Время только 1–4 минуты."
    rest = rest[1:]
    if not rest:
        return None, "❌ Укажи направление (вверх/вниз)."

    # Направление
    dir_token = rest[0]
    if dir_token in ("ВВЕРХ", "UP"):
        side = "LONG (вверх)"
    elif dir_token in ("ВНИЗ", "DOWN"):
        side = "SHORT (вниз)"
    else:
        return None, "❌ Направление: вверх/вниз (или UP/DOWN)."
    rest = rest[1:]
    if not rest:
        return None, "❌ Укажи сумму (40/100/220)."

    # Сумма
    m = re.search(r"\d+", " ".join(rest))
    if not m:
        return None, "❌ Сумма не распознана. Доступно: 40, 100, 220."
    amount = int(m.group(0))
    if amount not in VALID_AMOUNTS:
        return None, "❌ Сумма только 40, 100 или 220."

    return {"symbol": symbol, "minutes": minutes, "side": side, "amount": amount}, None

def cmd_start(update, context):
    update.message.reply_text(
        "Бот запущен ✅\n"
        "Формат (OTC необязательно):\n"
        "• EURUSD 1 вверх 40\n"
        "• EURUSD OTC 1 вверх 40\n"
        "• Евро USD 1 минута вверх на 40 $"
    )

def handle_text(update, context):
    text = update.message.text or ""
    data, err = parse_command(text)
    if err:
        update.message.reply_text(err)
        return
    update.message.reply_text(
        "✅ Принял команду:\n"
        f"• Пара: {data['symbol']}\n"
        f"• Срок: {data['minutes']} мин\n"f"• Направление: {data['side']}\n"
        f"• Сумма: {data['amount']}$\n"
        "(*пока подтверждение — без отправки сделки*)"
    )

def main():
    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Нет TELEGRAM_TOKEN")
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", cmd_start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    logging.info("Бот успешно запущен, слушает polling...")
    updater.start_polling(drop_pending_updates=True, timeout=30)
    updater.idle()

if __name__ == "__main__":
    main()
