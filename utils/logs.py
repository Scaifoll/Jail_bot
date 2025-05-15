from aiogram import Bot

async def log_action(bot: Bot, chat_id: int, message: str):
    await bot.send_message(chat_id, f"ЛОГ: {message}")
