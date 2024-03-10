import asyncio

from aiogram import types
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from handlers.user_private import user_private_router
from handlers.admin_private import admin_router
from common.command_list import private
from database.engine import create_db, drop_db, session_maker
from middlewares.db import DataBaseSession
from config.main_config import bot, dp

dp.include_router(admin_router)
dp.include_router(user_private_router)


async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    print('Вики Бот прилег отдохнуть...')


async def main() -> None:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
