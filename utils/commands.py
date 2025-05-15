from aiogram.types import BotCommand

async def set_commands(bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="admin_menu", description="Меню администратора"),
        BotCommand(command="create_firstmsg", description="Создать приветственное сообщение"),
        BotCommand(command="mute", description="Замутить участника"),
        BotCommand(command="ban", description="Забанить участника"),
    ]
    await bot.set_my_commands(commands)
