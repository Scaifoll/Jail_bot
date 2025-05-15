from aiogram import types, Dispatcher, Bot
from aiogram.filters import Command
import logging
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)


user_delete_counts = defaultdict(list)

SPAM_TIMEFRAME = 5  
SPAM_THRESHOLD = 3   


async def delete_replied_message(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

    now = asyncio.get_event_loop().time()
    user_delete_counts[user_id] = [t for t in user_delete_counts[user_id] if now - t < SPAM_TIMEFRAME]
    user_delete_counts[user_id].append(now)


    if len(user_delete_counts[user_id]) >= SPAM_THRESHOLD:
        try:
            await message.delete()
        except:
            pass
        await message.answer(f"{username}, не надо спамить командой.")
        return

   
    if not message.reply_to_message:
        await message.answer(f"{username}, не стоит использовать эту команду просто так.")
        return

    
    original = message.reply_to_message
    me = await bot.get_me()

    if original.from_user and original.from_user.is_bot and original.from_user.id != me.id:
        markup = original.reply_markup
        if isinstance(markup, types.InlineKeyboardMarkup):
            for row in markup.inline_keyboard:
                for button in row:
                    if button.url:
                        try:
                            await original.delete()
                            await message.delete()  
                            logger.info(f"Удалено сообщение {original.message_id} и команда /delete")
                        except Exception as e:
                            logger.warning(f"Ошибка при удалении: {e}")
                        return

    
    await message.answer(f"{username}, сообщение не нарушает правила беседы.")


def register_delete_ads_handlers(dp: Dispatcher):
    dp.message.register(delete_replied_message, Command("delete"))
