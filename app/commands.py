from aiogram import Bot
from aiogram.types import BotCommand

async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start / Меню"),
        BotCommand(command="help", description="Help / Помощь"),
        BotCommand(command="changerole", description="Switch Role / Сменить роль"),
        BotCommand(command="mypost", description="My Active Ride / Моя поездка"),
        BotCommand(command="edit", description="Refile / Пересоздать"),
        BotCommand(command="stop", description="Stop / Удалить")
    ]
    await bot.set_my_commands(commands)
