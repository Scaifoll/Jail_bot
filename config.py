import os
from dotenv import load_dotenv

load_dotenv()

# Загружаем токен из .env файла
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не найден токен бота в переменных окружения!")

# ID чата для логов
LOG_CHAT_ID = 2450008433

# ID канала для репортов
REPORTS_CHANNEL_ID = 2256196645

# Список админов
ADMIN_IDS = []
ADMIN_IDS.append(983670870)  # Ваш ID

# ID чата для логов
LOG_CHAT_ID = 2450008433  # Можно указать ID чата для логирования действий


