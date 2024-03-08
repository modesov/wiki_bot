from emoji import emojize
from aiogram.utils.formatting import Bold, as_marked_section

greeting_text = (f"{emojize(':waving_hand:')} Привет, [name]!\n\n{emojize(':face_with_monocle:')} Меня зовут Вики Бот! "
                 f"\nМоя {emojize(':collision:')} миссия помогать {emojize(':pink_heart:')} людям получать информацию из wikipedia не выходя из телеграма.\nНапиши мне то что ты хочешь узнать...")
go_search_text = f"Подожди не много я пошел {emojize(':face_with_monocle:')} искать инфу..."
not_find_text = f"{emojize(':face_with_monocle:')} Конкретно такого не нашел в wikipedia, но возможно подойдет что то из этого {emojize(':down_arrow:') * 3}"
no_such_find = f"{emojize(':face_with_monocle:')} Такого нет в wikipedia. Попробуй другой запрос..."


help_command_description_text = as_marked_section(
    Bold(f'{emojize(":information:")} Пользоваться Вики Ботом очень просто\n'),
    'Напиши ему то, что тебя интересует\n',
    'Вики найдет информацию в wikipedia, \n',
    'Разобьет текст на разделы и страницы\n',
    'Сделает по ним навигацию\n',
    'И пришлет тебе\n',
    'Плюс приложит ссылку на страницу в wikipedia\n',
    marker=emojize(':check_mark:')
).as_html()
# Команды
command_start_text = 'Знакомство с Вики Ботом'
command_help_text = 'Как пользоваться Вики Ботом'
