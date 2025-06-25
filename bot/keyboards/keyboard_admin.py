from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def admin_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отчёт"), KeyboardButton(text="Список групп")],
            [KeyboardButton(text="Удалить последнее"), KeyboardButton(text="Выйти из админки")]
        ],
        resize_keyboard=True
    )
