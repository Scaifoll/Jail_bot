from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from config import ADMIN_IDS, REPORTS_CHANNEL_ID
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("report"))
async def report_message(message: Message):
    """Обработчик команды /report"""
    try:
        if not message.reply_to_message:
            await message.reply("❌ Эта команда должна быть использована в ответ на сообщение.")
            return

        reported_msg = message.reply_to_message
        reporter = message.from_user
        reported_user = reported_msg.from_user

        # Формируем текст репорта
        report_text = (
            "📢 <b>Новый репорт!</b>\n\n"
            f"👤 <b>Отправитель:</b> {reporter.full_name} (ID: {reporter.id})\n"
            f"👥 <b>На пользователя:</b> {reported_user.full_name} (ID: {reported_user.id})\n"
            f"💭 <b>Чат:</b> {message.chat.title}\n"
            f"📝 <b>Сообщение:</b>\n"
            f"{reported_msg.text or '[медиа-контент]'}\n\n"
            f"🔗 <a href='https://t.me/c/{str(message.chat.id)[4:]}/{reported_msg.message_id}'>Перейти к сообщению</a>"
        )

        # Отправляем репорт в канал
        await message.bot.send_message(
            REPORTS_CHANNEL_ID,
            report_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

        # Уведомляем пользователя
        await message.reply(
            "✅ Жалоба отправлена администраторам.\n"
            "Спасибо за вашу бдительность!"
        )

        # Логируем действие
        logger.info(
            f"Новый репорт от {reporter.full_name} (ID: {reporter.id}) "
            f"на пользователя {reported_user.full_name} (ID: {reported_user.id}) "
            f"в чате {message.chat.title}"
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке репорта: {e}")
        await message.reply(
            "❌ Произошла ошибка при отправке жалобы.\n"
            "Пожалуйста, попробуйте позже."
        )

def register_report_handlers(dp):
    """Регистрация обработчиков репортов"""
    dp.include_router(router)
