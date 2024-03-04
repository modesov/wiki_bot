from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter, or_f, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.formatting import Bold
from sqlalchemy.ext.asyncio import AsyncSession

from config.texts import greeting_text, go_search_text, not_find_text
from services.wiki import Wiki
from database.orm_query import orm_add_user

user_private_router = Router()


class ReadAnswer(StatesGroup):
    wiki = State()
    read = State()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    await orm_add_user(session=session, user=dict(message.from_user))
    await message.answer(greeting_text.replace('[name]', message.from_user.first_name))


@user_private_router.message(Command('help'))
async def start_cmd(message: types.Message):
    await message.answer('Здесь надо рассказать как пользоваться Вики Ботом')


@user_private_router.edited_message(F.text)
@user_private_router.message(F.text)
async def start_search(message: types.Message, state: FSMContext):
    if not StateFilter(None):
        await state.clear()
    msg = await message.answer(go_search_text, reply_markup=ReplyKeyboardRemove())
    wiki = Wiki(text_search=message.text)
    await wiki.init()
    text = await wiki.getInfo()
    found_option = await wiki.getFoundOptions()
    if text == not_find_text and found_option:
        await msg.delete()
        await message.answer(text=text, reply_markup=wiki.getButtons())
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
            title = f'{Bold(section["title"]).as_html()}\n\n'
            words = text.split(' ')
            chunks = []
            chunk = ''
            i = 0
            for substr in words:
                if len(chunk) + len(substr) < chart_limit:
                    chunk += f' {substr}'
                else:
                    chunks.append(title + chunk if i > 0 else chunk)
                    chunk = substr
                    i += 1
            if len(chunk) < chart_limit:
                chunks.append(title + chunk)

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
        print(error)
        await message.message.edit_text(text=not_find_text)


@user_private_router.callback_query(F.data.startswith('btn_section:'))
async def get_info_by_section_error(message: types.CallbackQuery, state: FSMContext):
    if not StateFilter(None):
        await state.clear()
    await message.message.edit_text(text='Что то пошло не так. Попробуйте ввести запрос заново.')


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
async def pagination(message: types.CallbackQuery, state: FSMContext):
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
