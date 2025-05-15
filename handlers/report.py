from aiogram import types, Dispatcher, Bot
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
import logging

logger = logging.getLogger(__name__)


REPORT_CHANNEL_ID = -1002650053883

async def handle_report(message: types.Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer("Пожалуйста, используйте команду /report в ответ на сообщение.")
        return

    reported_msg = message.reply_to_message
    sender = reported_msg.from_user
    sender_name = f"@{sender.username}" if sender.username else f"{sender.full_name} ({sender.id})"
    reporter = message.from_user
    reporter_name = f"@{reporter.username}" if reporter.username else f"{reporter.full_name} ({reporter.id})"

    chat = message.chat
    msg_text = reported_msg.text or "<без текста>"

    link = "Ссылка недоступна (приватный чат)"
    if chat.username:
        link = f"https://t.me/{chat.username}/{reported_msg.message_id}"
    else:
        try:
            link = f"chat_id: {chat.id}, message_id: {reported_msg.message_id}"
        except:
            pass

    report_text = (
        f"🚨 {hbold('Поступил репорт')}\n\n"
        f"{hbold('От кого:')} {reporter_name}\n"
        f"{hbold('На кого:')} {sender_name}\n"
        f"{hbold('Сообщение:')}\n{msg_text}\n\n"
        f"{hbold('Ссылка:')} {link}"
    )

    try:
        await bot.send_message(REPORT_CHANNEL_ID, report_text, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        logger.warning(f"Не удалось отправить репорт в канал: {e}")
        await message.answer("⚠️ Не удалось отправить репорт. Свяжитесь с админом.")
        return

    await message.answer("✅ Репорт отправлен модераторам.")

def register_report_handler(dp: Dispatcher):
    dp.message.register(handle_report, Command("report"))
