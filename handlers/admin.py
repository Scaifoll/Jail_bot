from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

async def admin_menu_handler(message: Message):
    await message.answer("Админ-меню:\n/mute - Мутить участника\n/ban - Банить участника")

async def mute_handler(message: Message):
    await message.answer("Участник замучен!")

async def ban_handler(message: Message):
    await message.answer("Участник забанен!")

def register_admin_handlers(dp: Dispatcher):
    dp.message.register(admin_menu_handler, Command("admin_menu"))
    dp.message.register(mute_handler, Command("mute"))
    dp.message.register(ban_handler, Command("ban"))
