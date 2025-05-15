from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

async def help_command(message: types.Message):
    help_text = (
        """<b>📜 Правила беседы:</b>

<b>1.</b> 🚫 Запрещены <b>оскорбления</b> участников беседы.  
<b>2.</b> 🔞 Запрещена <b>порнография</b>, <b>обнажёнка</b> (включая рисованную), <b>шок-контент</b> (мертвые люди/животные, расчленёнка и прочее).  
<b>3.</b> 📢 Запрещена <b>реклама</b> любых сторонних ресурсов (беседы, паблики, Instagram и пр.).  
<b>4.</b> 💸 Запрещено просить или давать <b>деньги, аккаунты и т.д.</b> в долг — даже с благими намерениями.  
<b>5.</b> 🕵️‍♂️ Запрещается <b>слив личной информации</b>.  
<b>6.</b> 🔥 Запрещены <b>розжиги межнациональных конфликтов</b>.  
<b>7.</b> 🗯 Запрещён <b>флуд и спам</b>.


👮‍♂️ <b>Администрация</b> оставляет за собой право <b>исключить или забанить</b> вас без объяснения причин.

❗️<b>Незнание правил</b> не освобождает от ответственности.
🚪 <i>Вернуться в беседу (после кика)</i> можно <b>только через куратора режима</b> — <u>по его желанию</u>.

"""
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Правила режима", url="https://docs.google.com/document/d/1837ipUjm0tiHW74V2BTFHVJPZTy0nG7tLe7BN6ZFtZI"),
            InlineKeyboardButton(text="📞 ТГ Канал режима", url="https://t.me/jail_cybershoke")
        ]
    ])

    await message.answer(help_text, parse_mode="HTML", reply_markup=keyboard)

def register_rules_handler(dp: Dispatcher):
    dp.message.register(help_command, Command("rules"))
