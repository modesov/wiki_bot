from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Помощь'),
            KeyboardButton(text='Обо мне')
        ],
        [
            KeyboardButton(text='Советы по использоваанию меня'),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню или введите что хотите!'
)

# Вот так еще можно строить клавиатуру. Можно комбинировать. Смотри документацию...
# help_kb = ReplyKeyboardBuilder()
# help_kb.add(
#     KeyboardButton(text='Помощь'),
#     KeyboardButton(text='Обо мне'),
#     KeyboardButton(text='Советы по использоваанию меня'),
# )
# help_kb.adjust(2,1)

# Для удаления клавиатур
del_kb = ReplyKeyboardRemove()
