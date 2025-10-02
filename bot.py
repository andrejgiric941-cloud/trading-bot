download(custom_path=oga_path)
        ogg_to_wav(oga_path, wav_path)
        text = wit_ai_stt(wav_path).strip()
        if not text:
            reply(update, "❌ Не разобрал голос. Скажи: 'EURUSD OTC 1 вверх 40'")
            return
        data, err = parse_command(text)
        if err:
            reply(update, f"Распознал: «{text}»\n{err}")
            return
        reply(update,
              f"🎤 Голос распознан:\n"
              f"• Текст: {text}\n"
              f"• Пара: {data['symbol']}\n"
              f"• Срок: {data['minutes']} мин\n"
              f"• Направление: {data['side']}\n"
              f"• Сумма: {data['amount']}$\n"
              f"• Режим: {data['trade_mode']}\n"
              "(*ордер пока не отправляется — тест парсинга*)")
    except Exception as e:
        logging.exception("Ошибка голосовой обработки")
        reply(update, f"Ошибка: {e}")
    finally:
        for p in (oga_path, wav_path):
            try: os.remove(p)
            except: pass

# --- Команды ---
def start(update, context):
    if not is_allowed(update): return
    reply(update, "👋 Бот запущен.\nФормат: EURUSD OTC 1 вверх 40\nСуммы только: 40 / 100 / 220")

def help_cmd(update, context):
    if not is_allowed(update): return
    reply(update, "Примеры:\nEURUSD OTC 1 вверх 40\nUSDJPY OTC 2 вниз 100\nGBPUSD OTC 3 вверх 220")

def main():
    while True:
        try:
            updater = Updater(TELEGRAM_TOKEN, use_context=True)
            dp = updater.dispatcher
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(CommandHandler("help", help_cmd))
            dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
            dp.add_handler(MessageHandler(Filters.voice | Filters.audio, handle_voice))
            logging.info("Бот запущен...")
            updater.start_polling(drop_pending_updates=True, timeout=30)
            updater.idle()
        except Exception:
            logging.exception("Бот упал, перезапуск через 5 сек")
            time.sleep(5)

if __name__ == "__main__":
    main()
