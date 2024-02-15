import wikipediaapi
from aiogram import types, Router, F
from aiogram.filters import CommandStart
from config.texts import greeting_text, go_search_text, not_find_text
from keyboards import replay

user_private_router = Router()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        greeting_text.replace('{name}', message.from_user.first_name),
        reply_markup=replay.start_kb
    )


@user_private_router.edited_message(F.text)
@user_private_router.message(F.text)
async def start_cmd(message: types.Message):
    msg = await message.answer(go_search_text)
    i = 0
    text_message = message.text
    while True:
        try:
            wiki = wikipediaapi.Wikipedia(user_agent='MyProjectName (merlin@example.com)', language='ru',
                                          extract_format=wikipediaapi.ExtractFormat.WIKI)
            page = wiki.page(text_message)
            if page.exists():
                info = '\n\n'.join(list(page.summary.split('\n')))
                await msg.edit_text(info)
                break
            else:
                if i >= 3:
                    raise Exception()
                text_message = message.text.title()
                continue
        except BaseException as inst:
            print(inst, type(inst))

            if i >= 3:
                await msg.edit_text(not_find_text)
                break

            i += 1
