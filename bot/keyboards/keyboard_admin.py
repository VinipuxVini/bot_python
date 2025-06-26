from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def admin_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить файл"), KeyboardButton(text="Отправить медиа")],
            [KeyboardButton(text="Объявление"), KeyboardButton(text="Список групп")],
            [KeyboardButton(text="Отчёт"), KeyboardButton(text="Список админов")],
            [KeyboardButton(text="Удалить последнее"), KeyboardButton(text="Удалить везде")]
        ],
        resize_keyboard=True
    )

def file_operations_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Установить описание"), KeyboardButton(text="Отправить файл")],
            [KeyboardButton(text="Отправить медиа"), KeyboardButton(text="<- Назад")]
        ],
        resize_keyboard=True
    )

def group_operations_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Список групп"), KeyboardButton(text="Удалить последнее")],
            [KeyboardButton(text="Удалить везде"), KeyboardButton(text="<- Назад")]
        ],
        resize_keyboard=True
    )

def inline_confirm_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")
            ]
        ]
    )

def inline_week_select_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Неделя 1", callback_data="week_1"),
                InlineKeyboardButton(text="Неделя 2", callback_data="week_2"),
                InlineKeyboardButton(text="Неделя 3", callback_data="week_3")
            ],
            [
                InlineKeyboardButton(text="Неделя 4", callback_data="week_4"),
                InlineKeyboardButton(text="Неделя 5", callback_data="week_5")
            ]
        ]
    )