import os

from aiogram import Bot


async def send_message_admin(*, bot: Bot, message: str):
    admins = list(map(int, os.getenv('ADMINS').split(',')))
    for admin_id in admins:
        await bot.send_message(admin_id, message)
