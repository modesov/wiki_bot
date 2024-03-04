from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

admin_kb = InlineKeyboardBuilder()
admin_kb.add(
    InlineKeyboardButton(text='Список пользователей', callback_data='admin_user_list'),
    InlineKeyboardButton(text='Частые запросы', callback_data='admin_requests'),
    InlineKeyboardButton(text='Логи ошибок', callback_data='admin_logs_error_list'),
)
admin_kb.adjust(2, 1)
