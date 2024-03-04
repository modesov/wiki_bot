from emoji import emojize

greeting_text = (f"{emojize(':waving_hand:')} Привет, [name]!\n{emojize(':face_with_monocle:')} Меня зовут Вики Бот! "
                 f"\nМоя {emojize(':collision:')} миссия помогать {emojize(':pink_heart:')} людям получать информацию из wikipedia не выходя из телеграма.\nНапиши мне то что ты хочешь узнать...")
go_search_text = 'Подожди я пошел искать инфу...'
not_find_text = 'Что то такого нет в wikipedia. Попробуйте другой запрос...'

# Команды
command_start_text = 'Кто такой Вики Бот?'
command_help_text = 'Советы по использованию Вики Бота'
