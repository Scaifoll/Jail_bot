from aiogram import types, Dispatcher, Bot
from aiogram.filters import Command
import logging
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)

user_delete_counts = defaultdict(list)
bot_warn_messages = []

SPAM_TIMEFRAME = 5  
SPAM_THRESHOLD = 5

async def delete_replied_message(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

    now = asyncio.get_event_loop().time()
    user_delete_counts[user_id] = [t for t in user_delete_counts[user_id] if now - t < SPAM_TIMEFRAME]
    user_delete_counts[user_id].append(now)

    # Спам фильтр
    if len(user_delete_counts[user_id]) >= SPAM_THRESHOLD:
        try:
            msg = await message.answer(f"{username}, не надо спамить командой!")

            # Добавляем сообщение бота в отслеживаемые
            bot_warn_messages.append((msg.message_id, now))

            # Очищаем список от устаревших
            bot_warn_messages[:] = [(mid, ts) for mid, ts in bot_warn_messages if now - ts < SPAM_TIMEFRAME]

            # Если более одного — удаляем все кроме последнего
            if len(bot_warn_messages) > 1:
                for mid, _ in bot_warn_messages[:-1]:
                    try:
                        await bot.delete_message(chat_id=message.chat.id, message_id=mid)
                    except Exception as e:
                        logger.warning(f"Не удалось удалить предупреждение: {e}")
                # Оставляем только последнее сообщение
                bot_warn_messages[:] = [bot_warn_messages[-1]]

        except Exception as e:
            logger.warning(f"Ошибка при отправке предупреждения: {e}")

        try:
            await message.delete()
        except:
            pass
        return

    # Проверка, есть ли reply
    if not message.reply_to_message:
        await message.answer(f"{username}, не стоит использовать эту команду просто так.")
        await message.delete()
        return

    original = message.reply_to_message
    me = await bot.get_me()

    # Если сообщение от бота и содержит URL
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
