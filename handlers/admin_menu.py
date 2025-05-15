import asyncio
import json
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import (
    Message, 
    CallbackQuery, 
    ChatMemberOwner, 
    ChatMemberAdministrator,
    ChatMember
)
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_IDS, LOG_CHAT_ID
import logging

logger = logging.getLogger(__name__)
router = Router()

# Путь к файлу с предупреждениями
WARNINGS_FILE = 'data/warnings.json'

class AdminMenu:
    def __init__(self):
        self.muted_users = {}
        self.banned_users = {}
        self.warnings = self.load_warnings()

    def load_warnings(self):
        try:
            with open(WARNINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"chats": {}}

    def save_warnings(self):
        with open(WARNINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.warnings, f, indent=4, ensure_ascii=False)

    def get_user_warnings(self, chat_id: str, user_id: str) -> int:
        chat_id, user_id = str(chat_id), str(user_id)
        return self.warnings["chats"].get(chat_id, {}).get(user_id, 0)

    def add_warning(self, chat_id: str, user_id: str) -> int:
        chat_id, user_id = str(chat_id), str(user_id)
        if chat_id not in self.warnings["chats"]:
            self.warnings["chats"][chat_id] = {}
        if user_id not in self.warnings["chats"][chat_id]:
            self.warnings["chats"][chat_id][user_id] = 0
        self.warnings["chats"][chat_id][user_id] += 1
        self.save_warnings()
        return self.warnings["chats"][chat_id][user_id]

admin_menu = AdminMenu()

def get_admin_keyboard():
    """Создает клавиатуру админ-меню"""
    kb = InlineKeyboardBuilder()
    kb.button(text="Мут", callback_data="admin_mute")
    kb.button(text="Размут", callback_data="admin_unmute")
    kb.button(text="Бан", callback_data="admin_ban")
    kb.button(text="Разбан", callback_data="admin_unban")
    kb.button(text="Варн", callback_data="admin_warn")
    kb.button(text="Список варнов", callback_data="admin_warn_stats")
    kb.adjust(2)  # Размещаем кнопки по 2 в ряд
    return kb.as_markup()

@router.message(Command("admin_menu"))
async def show_admin_menu(message: Message):
    """Показывает админ-меню"""
    logger.info(f"ID пользователя: {message.from_user.id}, Имя пользователя: {message.from_user.username}")
    
    if message.from_user.id not in ADMIN_IDS:
        await message.reply(f"У вас нет прав администратора! Ваш ID: {message.from_user.id}")
        return
    
    await message.reply(
        "Панель управления администратора:",
        reply_markup=get_admin_keyboard()
    )

async def get_chat_members_keyboard(chat_id: int, bot, page: int = 0, action: str = ""):
    """Создает клавиатуру со списком участников чата"""
    kb = InlineKeyboardBuilder()
    
    try:
        # Получаем информацию о чате
        chat = await bot.get_chat(chat_id)
        
        # Получаем список участников
        members = []
        count = await bot.get_chat_member_count(chat_id)
        
        # Получаем участников порциями
        for offset in range(0, min(count, 50), 10):  # Ограничиваем первыми 50 участниками
            chunk = await bot.get_chat_administrators(chat_id)
            for member in chunk:
                if not isinstance(member.status, (ChatMemberOwner, ChatMemberAdministrator)):
                    members.append(member)
        
        # Разбиваем на страницы по 5 пользователей
        page_size = 5
        start_idx = page * page_size
        page_members = members[start_idx:start_idx + page_size]
        
        # Добавляем кнопки с пользователями
        for member in page_members:
            user = member.user
            name = f"{user.first_name}"
            if user.last_name:
                name += f" {user.last_name}"
            if len(name) > 20:
                name = name[:20] + "..."
            kb.button(
                text=name,
                callback_data=f"select_user_{action}_{user.id}"
            )
        
        kb.adjust(1)  # По одной кнопке в ряд
        
        # Добавляем навигационные кнопки
        row = []
        if page > 0:
            row.append(InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"page_{action}_{page-1}"
            ))
        if len(members) > (page + 1) * page_size:
            row.append(InlineKeyboardButton(
                text="Вперед ▶️",
                callback_data=f"page_{action}_{page+1}"
            ))
        if row:
            kb.row(*row)
        
        # Кнопка возврата в главное меню
        kb.row(InlineKeyboardButton(text="🔙 В меню", callback_data="admin_back"))
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка участников: {e}")
        kb.button(text="🔙 В меню", callback_data="admin_back")
    
    return kb.as_markup()

@router.callback_query(F.data.startswith("admin_"))
async def handle_admin_callback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("У вас нет прав администратора!", show_alert=True)
        return

    action = callback.data.split("_")[1]
    
    if action == "mute":
        keyboard = await get_chat_members_keyboard(
            callback.message.chat.id,
            callback.bot,
            action="mute"
        )
        await callback.message.edit_text(
            "Выберите пользователя для мута:",
            reply_markup=keyboard
        )
    elif action == "ban":
        keyboard = await get_chat_members_keyboard(
            callback.message.chat.id,
            callback.bot,
            action="ban"
        )
        await callback.message.edit_text(
            "Выберите пользователя для бана:",
            reply_markup=keyboard
        )
    elif action == "warn":
        kb = InlineKeyboardBuilder()
        kb.button(text="◀️ Назад", callback_data="admin_back")
        await callback.message.edit_text(
            "Введите ID пользователя для выдачи предупреждения:",
            reply_markup=kb.as_markup()
        )
    elif action == "back":
        await callback.message.edit_text(
            "Панель управления администратора:",
            reply_markup=get_admin_keyboard()
        )

@router.callback_query(F.data.startswith("select_user_"))
async def handle_user_selection(callback: CallbackQuery):
    """Обработчик выбора пользователя"""
    if callback.from_user.id not in ADMIN_IDS:
        return
    
    _, action, user_id = callback.data.split("_")[1:]
    user_id = int(user_id)
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Назад", callback_data=f"admin_{action}")
    
    if action == "mute":
        kb.button(text="5 минут", callback_data=f"mute_{user_id}_5")
        kb.button(text="30 минут", callback_data=f"mute_{user_id}_30")
        kb.button(text="1 час", callback_data=f"mute_{user_id}_60")
        kb.button(text="1 день", callback_data=f"mute_{user_id}_1440")
        kb.adjust(2)
        await callback.message.edit_text(
            f"Выберите длительность мута для пользователя:",
            reply_markup=kb.as_markup()
        )
    elif action == "ban":
        kb.button(text="1 час", callback_data=f"ban_{user_id}_60")
        kb.button(text="1 день", callback_data=f"ban_{user_id}_1440")
        kb.button(text="1 неделя", callback_data=f"ban_{user_id}_10080")
        kb.button(text="Навсегда", callback_data=f"ban_{user_id}_0")
        kb.adjust(2)
        await callback.message.edit_text(
            f"Выберите длительность бана для пользователя:",
            reply_markup=kb.as_markup()
        )

@router.callback_query(F.data.startswith(("mute_", "ban_")))
async def handle_action_duration(callback: CallbackQuery):
    """Обработчик выбора длительности действия"""
    if callback.from_user.id not in ADMIN_IDS:
        return
    
    action, user_id, duration = callback.data.split("_")
    user_id = int(user_id)
    duration = int(duration)
    
    if action == "mute":
        await mute_user(callback.message.chat.id, user_id, duration, callback.message)
    elif action == "ban":
        await ban_user(callback.message.chat.id, user_id, duration, callback.message)
    
    # Возвращаемся в главное меню
    await callback.message.edit_text(
        "Панель управления администратора:",
        reply_markup=get_admin_keyboard()
    )

@router.callback_query(F.data.startswith("page_"))
async def handle_page_navigation(callback: CallbackQuery):
    """Обработчик навигации по страницам"""
    if callback.from_user.id not in ADMIN_IDS:
        return
    
    _, action, page = callback.data.split("_")
    page = int(page)
    
    keyboard = await get_chat_members_keyboard(
        callback.message.chat.id,
        callback.bot,
        page,
        action
    )
    await callback.message.edit_text(
        f"Выберите пользователя для {action}:",
        reply_markup=keyboard
    )

@router.message()
async def handle_admin_actions(message: Message):
    """Обработчик действий админа после нажатия кнопок"""
    if message.from_user.id not in ADMIN_IDS:
        return

    # Получаем последнее сообщение с командой
    reply_to = message.reply_to_message
    if not reply_to or not hasattr(reply_to, 'text'):
        return

    try:
        if "время мута" in reply_to.text:
            user_id, duration = map(int, message.text.split())
            await mute_user(message.chat.id, user_id, duration, message)
        
        elif "время бана" in reply_to.text:
            user_id, duration = map(int, message.text.split())
            await ban_user(message.chat.id, user_id, duration, message)
        
        elif "для выдачи предупреждения" in reply_to.text:
            user_id = int(message.text)
            warnings = admin_menu.add_warning(message.chat.id, user_id)
            await message.reply(
                f"Пользователю {user_id} выдано предупреждение (всего: {warnings})"
            )
            
            # Автоматический мут при достижении порога варнов
            if warnings >= 3:
                await mute_user(message.chat.id, user_id, 60, message)  # Мут на час
                
    except ValueError: 
        await message.reply("Неверный формат данных! Попробуйте еще раз.")
    except Exception as e:
        logger.error(f"Ошибка при выполнении админ-действия: {e}")
        await message.reply("Произошла ошибка при выполнении действия.")

async def mute_user(chat_id: int, user_id: int, duration: int, message: Message):
    """Мутит пользователя"""
    try:
        until_date = datetime.now() + timedelta(minutes=duration)
        await message.bot.restrict_chat_member(
            chat_id, user_id,
            until_date=until_date,
            permissions={"can_send_messages": False}
        )
        
        # Сохраняем информацию о муте
        admin_menu.muted_users[user_id] = {
            "until": until_date,
            "chat_id": chat_id
        }
        
        await message.reply(f"Пользователь {user_id} замучен на {duration} минут.")
        
        # Запускаем таймер размута
        asyncio.create_task(auto_unmute(chat_id, user_id, duration, message.bot))
        
    except Exception as e:
        logger.error(f"Ошибка при муте пользователя: {e}")
        await message.reply("Не удалось замутить пользователя.")

async def auto_unmute(chat_id: int, user_id: int, duration: int, bot):
    """Автоматически размучивает пользователя после истечения времени"""
    await asyncio.sleep(duration * 60)
    try:
        await bot.restrict_chat_member(
            chat_id, user_id,
            permissions={"can_send_messages": True}
        )
        admin_menu.muted_users.pop(user_id, None)
        logger.info(f"Пользователь {user_id} автоматически размучен")
    except Exception as e:
        logger.error(f"Ошибка при автоматическом размуте: {e}")

async def ban_user(chat_id: int, user_id: int, duration: int, message: Message):
    """Банит пользователя"""
    try:
        if duration > 0:
            until_date = datetime.now() + timedelta(minutes=duration)
            admin_menu.banned_users[user_id] = {
                "until": until_date,
                "chat_id": chat_id
            }
            asyncio.create_task(auto_unban(chat_id, user_id, duration, message.bot))
        else:
            until_date = None  # Перманентный бан
            
        await message.bot.ban_chat_member(chat_id, user_id, until_date=until_date)
        ban_type = "временно" if duration > 0 else "навсегда"
        await message.reply(f"Пользователь {user_id} забанен {ban_type}.")
        
    except Exception as e:
        logger.error(f"Ошибка при бане пользователя: {e}")
        await message.reply("Не удалось забанить пользователя.")

async def auto_unban(chat_id: int, user_id: int, duration: int, bot):
    """Автоматически разбанивает пользователя после истечения времени"""
    await asyncio.sleep(duration * 60)
    try:
        await bot.unban_chat_member(chat_id, user_id)
        admin_menu.banned_users.pop(user_id, None)
        logger.info(f"Пользователь {user_id} автоматически разбанен")
    except Exception as e:
        logger.error(f"Ошибка при автоматическом разбане: {e}")

def register_admin_handlers(dp):
    """Регистрация обработчиков админ-меню"""
    dp.include_router(router)
