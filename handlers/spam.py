from aiogram import Router, types
import antispam  # Импортируем библиотеку антис–пама

router = Router()

# Путь к файлу модели спама
SPAM_MODEL_FILE = "spam_model.json"

# Создаем или загружаем модель через детектор, передавая путь к файлу.
# Если файла нет, можно установить create_new=True для создания новой модели.
detector = antispam.Detector(SPAM_MODEL_FILE, create_new=False)

# Установим порог оценки, выше которого сообщение считается спамом.
SPAM_THRESHOLD = 0.2

@router.message()
async def check_ads(message: types.Message):
    # Собираем текст для проверки: сообщение или подпись (caption)
    text_to_check = ""
    if message.text:
        text_to_check = message.text.lower()
    elif message.caption:
        text_to_check = message.caption.lower()

    if text_to_check:
        score = detector.score(text_to_check)
        print(f"Spam score: {score}")  # Для отладки можно выводить оценку в консоль

        if score > SPAM_THRESHOLD:
            await message.delete()
            await message.answer(f"🚫 @{message.from_user.username}, ваше сообщение похоже на спам!")
            
            # Обучаем модель, чтобы улучшить классификацию в будущем.
            detector.train(text_to_check, is_spam=True)
            detector.save()  # Сохраняем обновленную модель
