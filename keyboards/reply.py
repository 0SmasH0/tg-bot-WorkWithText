from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Проверить орфографию✍️'),
            KeyboardButton(text='Проверить оформление📝'),
        ],
        [
            KeyboardButton(text='Поддержать авторов💸'),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Что вас интересует?',
)

back_to_start = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Вернуться в начало🏠'),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Что вас интересует?',
)

back_to_start_and_back = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Вернуться в начало🏠'),
            KeyboardButton(text='Вернуться назад🔙'),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Что вас интересует?',
)


yes_or_no = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Да'),
            KeyboardButton(text='Нет'),
        ],
    ],
    resize_keyboard=True,
)


