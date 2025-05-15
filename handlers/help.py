from aiogram import types, Dispatcher
from aiogram.filters import Command

# 📖 Хендлер команды /help
async def help_command(message: types.Message):
    help_text = (
        "📌 *Доступные команды:*\n\n"
        "/start — запуск бота\n"
        "/delete — удалить сообщение с кнопкой-ссылкой (нужно ответить этой командой на сообщение)\n"
        "/help — список всех команд\n"
        "/rules — Правила беседы"
    )
    await message.answer(help_text, parse_mode="Markdown")

# 📥 Регистрация хендлера
def register_help_handler(dp: Dispatcher):
    dp.message.register(help_command, Command("help"))
