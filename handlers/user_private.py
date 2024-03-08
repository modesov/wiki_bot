import logging
import os

from emoji import emojize
from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter, or_f, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.formatting import Bold
from sqlalchemy.ext.asyncio import AsyncSession

from config.texts import greeting_text, go_search_text, not_find_text, no_such_find, help_command_description_text
from services.wiki import Wiki
from database.orm_query import orm_add_user, orm_add_user_phrase

user_private_router = Router()

logging.basicConfig(filename=os.path.abspath('logs/handler_errors.log'), format="%(asctime)s %(levelname)s %(message)s")


class ReadAnswer(StatesGroup):
    wiki = State()
    read = State()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    await orm_add_user(session=session, user=dict(message.from_user))
    await message.answer(greeting_text.replace('[name]', message.from_user.first_name))


@user_private_router.message(Command('help'))
async def start_cmd(message: types.Message):
    await message.answer(help_command_description_text)


@user_private_router.edited_message(F.text)
@user_private_router.message(F.text)
async def start_search(message: types.Message, state: FSMContext, session: AsyncSession):
    await orm_add_user_phrase(session=session, phrase=message.text, user_id=message.from_user.id)
    if not StateFilter(None):
        await state.clear()
    msg = await message.answer(go_search_text, reply_markup=ReplyKeyboardRemove())
    wiki = Wiki(text_search=message.text)
    await wiki.init()
    found_option = await wiki.getFoundOptions()
    text = await wiki.getInfo()
    if text == not_find_text and found_option:
        await msg.delete()
        await message.answer(text=text, reply_markup=wiki.getButtons())
    elif text == no_such_find:
        await msg.delete()
        await message.answer(text=text)
    else:
        await msg.delete()
        await state.update_data(wiki=wiki)
        await message.answer(text=text, reply_markup=wiki.getButtons())
        await state.set_state(ReadAnswer.wiki)


@user_private_router.callback_query(ReadAnswer.wiki, F.data.startswith('btn_section:'))
async def get_info_by_section(message: types.CallbackQuery, state: FSMContext):
    try:
        chart_limit = 2000
        section_slug = message.data.split(':')[-1]
        data = await state.get_data()
        wiki: Wiki | None = data.get('wiki', None)
        section = wiki.getSectionBySlug(slug=section_slug) if wiki else None
        parent = section['title'] if section else ''
        text = section['text'] or section['title'] if section else await wiki.getInfo()
        if section and len(text) > chart_limit:
            title = f'Категория «{section["title"]}» по запросу «{wiki.getTextSearch()}»' if section[
                                                                                                 "title"] != '...продолжение сводки' else f"Сводка по запросу «{wiki.getTextSearch()}» (продолжение)"
            words = text.split(' ')
            chunks = []
            chunk = ''
            i = 0
            for substr in words:
                if len(chunk) + len(substr) < chart_limit:
                    chunk += f' {substr}'
                else:
                    tail = f' стр. {i + 1}' if i > 0 else ''
                    title += tail

                    chunks.append(f'{Bold(title).as_html()}\n\n {chunk}' if i > 0 else chunk)
                    chunk = substr
                    i += 1
            if len(chunk) < chart_limit:
                tail = f'стр. {i + 1}\n' if i > 0 else ''
                title = tail + title
                chunks.append(f'{Bold(title).as_html()}\n\n {chunk}')

            read = {
                'chunks': chunks,
                'section': section,
                'current_page': 1
            }

            await state.update_data(read=read)

            await message.message.edit_text(text=chunks[0],
                                            reply_markup=wiki.getPagination(count=len(chunks), current_page=1))
            await state.set_state(ReadAnswer.read)
        elif len(text) > chart_limit:
            text = text[:chart_limit] + '...'
            await message.message.edit_text(text=text, reply_markup=wiki.getButtons(parent=parent))
        else:
            await message.message.edit_text(text=text, reply_markup=wiki.getButtons(parent=parent))
    except Exception as error:
        logging.error(error)
        await message.message.edit_text(text=no_such_find)


@user_private_router.callback_query(F.data.startswith('btn_section:'))
async def get_info_by_section_error(message: types.CallbackQuery, state: FSMContext):
    if not StateFilter(None):
        await state.clear()
    await message.message.edit_text(
        text=f'{emojize(":face_with_monocle:")} Что то пошло не так. Попробуйте ввести запрос заново.')


@user_private_router.callback_query(ReadAnswer.read, or_f(F.data == 'pagination_next', F.data == 'pagination_previous'))
async def pagination(message: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    wiki: Wiki | None = data.get('wiki', None)
    read: dict | None = data.get('read', None)
    if wiki and read:

        if message.data == 'pagination_next':
            read['current_page'] += 1
        else:
            read['current_page'] -= 1

        chunks: list[str] = read['chunks']
        await state.update_data(read=read)
        await message.message.edit_text(text=chunks[read['current_page'] - 1],
                                        reply_markup=wiki.getPagination(count=len(chunks),
                                                                        current_page=read['current_page']))


@user_private_router.callback_query(ReadAnswer.read, F.data == 'pagination_back')
async def pagination_back(message: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    wiki: Wiki | None = data.get('wiki', None)
    read: dict | None = data.get('read', None)
    if wiki and read:
        section = read['section']
        parent = section['parent'] if section else ''

        if parent:
            parent_section = wiki.getSectionByTitle(title=parent)
            text = parent_section['text'] or parent_section['title'] if parent_section else await wiki.getInfo()
        else:
            text = await wiki.getInfo()

        await state.update_data(read={})
        await state.set_state(ReadAnswer.wiki)
        await message.message.edit_text(text=text, reply_markup=wiki.getButtons(parent=parent))
