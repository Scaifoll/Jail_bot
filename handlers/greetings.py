from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import DEFAULT_WELCOME_MSG

welcome_message = DEFAULT_WELCOME_MSG  # Стандартное приветствие

async def greet_new_user(message: types.Message):
    for user in message.new_chat_members:
        await message.reply(f"Привет, {user.full_name}!\n{welcome_message}")

async def set_welcome_message(message: types.Message):
    global welcome_message
    new_message = message.text.split('/create_firstmsg', maxsplit=1)[-1].strip()
    if new_message:
        welcome_message = new_message
        await message.reply("Приветственное сообщение обновлено.")
    else:
        await message.reply("Введите сообщение после команды.")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(greet_new_user, content_types=types.ContentType.NEW_CHAT_MEMBERS)
    dp.register_message_handler(set_welcome_message, commands=["create_firstmsg"])
