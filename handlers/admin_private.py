from aiogram import types, Router, F
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.inline import admin_kb
from aiogram.utils.formatting import Bold, as_marked_section
from database.orm_query import orm_get_users

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())


@admin_router.message(Command('admin'))
async def admin_cmd(message: types.Message):
    await message.answer('Приветствую админ! Что изволите сударь?', reply_markup=admin_kb.as_markup())


@admin_router.callback_query(F.data == 'admin_user_list')
async def get_user_list(message: types.CallbackQuery, session: AsyncSession):
    users = await orm_get_users(session=session)
    user_list = []
    for user in users:
        user_list.append(f'{user.tg_id} - {user.full_name}')

    text = as_marked_section(
        Bold(f'Всего пользователей {len(users)}'),
        *user_list,
        marker=' - '
    )

    await message.message.answer(text.as_html())

