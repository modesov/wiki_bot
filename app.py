import asyncio
import wikipediaapi
from aiogram import Bot, Dispatcher, types, exceptions
from aiogram.filters import CommandStart

bot = Bot(token="6738585701:AAEtbzxj7VRWluEaVSWe-Q9QVpnsBUYz_Kc")
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(f'Привет, {message.chat.first_name}!\nМеня зовут wiki бот. Введи то что ты хочешь узанать, а я схожу в wikipedia все узнаю и приду с ответом!')
    
    
@dp.message()
async def start_cmd(message: types.Message):
    msg = await message.answer('Подождите я пошел искать инфу...')
    i = 0
    text_message = message.text
    while True:
        try:        
            wiki = wikipediaapi.Wikipedia(user_agent='MyProjectName (merlin@example.com)', language='ru', extract_format=wikipediaapi.ExtractFormat.WIKI)
            page = wiki.page(text_message)
            info = '\n\n'.join(list(page.summary.split('\n')))
            print(page.fullurl)
            # text = page.text.split('\n')
            # print(text)
            sections = page.sections
            print_sections(sections)
            await msg.edit_text(info)
            break
        except exceptions.TelegramBadRequest as inst:
            print(inst, type(inst))   
            if i>=3:
                await msg.edit_text('Что то такого нет в wikipedia. Попробуйте другой запрос...')
                break
            text_message = message.text.title()
            i += 1
        except BaseException as inst:
            print(inst, type(inst))   
            
            if i>=3:
                await msg.edit_text('Что то такого нет в wikipedia. Попробуйте другой запрос...')
                break
                                   
            i += 1
            
            
def print_sections(sections, level=0):
        for s in sections:
                print("%s: %s - %s" % ("*" * (level + 1), s.title, s.text[0:40]))
                print_sections(s.sections, level + 1)
            
       
       
async def main() -> None:
    await dp.start_polling(bot)
    

asyncio.run(main())
