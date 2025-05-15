import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from aiogram.filters import Command


# Настройка логирования
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# Настройка корневого логирования (Что бы увидеть DEBUG - сообщения всех модулей)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def main():
    try:
        # Регистрация всех обработчиков
        from handlers import register_all_handlers
        register_all_handlers(dp)
        logger.info("Бот запущен")
        # Запуск бота
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
    finally:
        await bot.session.close()
from aiogram.types import Message

@dp.message(Command("start"))
async def _debug_ping(message: Message):
    await message.reply("Привет, я бот который следит за порядком в этой беседе. /help - список команд")
    logger.debug(f"Стартовое сообщение отправленно. ID пользователя: {message.from_user.id}, Имя пользователя: {message.from_user.username}")



if __name__ == '__main__':
    asyncio.run(main())
