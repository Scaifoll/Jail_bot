from aiogram import Bot
from config import LOG_CHAT_ID

async def send_log(bot: Bot, log_message: str):
    """
    Отправляет лог-сообщение в лог-чат.
    """
    try:
        await bot.send_message(LOG_CHAT_ID, log_message)
    except Exception as e:
        print(f"Ошибка отправки логов: {e}")
