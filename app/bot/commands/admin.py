from aiogram.types import BotCommand
from aiogram.types.bot_command_scope_chat import BotCommandScopeChat

from app.bot.bot import bot
from app.config.config import SUPER_ADMIN_CHAT_ID


async def set_admit_commands():
    admin_commands = [
        BotCommand(command="/new_category",
                   description="Добавить новую категорию"),
        BotCommand(command="/cancel",
                   description="Отмена")
    ]

    await bot.set_my_commands(commands=admin_commands,
                              scope=BotCommandScopeChat(chat_id=SUPER_ADMIN_CHAT_ID))
