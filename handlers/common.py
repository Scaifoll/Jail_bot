from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

async def start_handler(message: Message):
    await message.answer("Привет! Я ваш бот.")

async def create_firstmsg_handler(message: Message):
    await message.answer("Стандартное приветственное сообщение создано!")

def register_common_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command("start"))
    dp.message.register(create_firstmsg_handler, Command("create_firstmsg"))
