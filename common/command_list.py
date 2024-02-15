from aiogram.types import BotCommand

from config.texts import command_start_text, command_help_text

private = [
    BotCommand(command='start', description=command_start_text),
    BotCommand(command='help', description=command_help_text),
]
