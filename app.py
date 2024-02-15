import asyncio
import os

from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv, find_dotenv

from handlers.user_private import user_private_router
from handlers.admin_private import admin_private_router
from common.command_list import private

load_dotenv(find_dotenv())


bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

dp.include_routers(user_private_router, admin_private_router)


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)


asyncio.run(main())
