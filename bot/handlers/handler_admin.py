from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove
import pytz
from datetime import datetime, timedelta

from bot.filters.role import RoleFilter
from bot.keyboards.keyboard_admin import admin_main_kb
from bot.services import group_service
from bot.services.admin_service import get_admins, isAdmin, send_announcement
from bot.services.group_service import get_sent_messages_in_range, delete_sent_messages_in_range, get_sent_message_time_ranges

router = Router()
router.message.filter(F.chat.type.in_({"private"}))
router.message.filter(RoleFilter(["admin"]))

class SetDescription(StatesGroup):
    waiting_description = State()

class SendFile(StatesGroup):
    waiting_file = State()
    waiting_group = State()

class SendMedia(StatesGroup):
    waiting_media = State()
    waiting_caption = State() 

class Announcement(StatesGroup):
    waiting_text = State()

class DeleteLast(StatesGroup):
    waiting_group = State()
class DeleteAdmin(StatesGroup):
    waiting_admin_id = State()
    
class DeleteMessagesFSM(StatesGroup):
    waiting_time_range = State()
    waiting_confirm = State()

# Обработка кнопок
@router.message(Command("report"))
async def report_button_handler(message: Message):
    await message.answer("Отчёт за неделю...")

@router.message(lambda m: m.text == "Список админов")
async def admin_list_button_handler(message: Message):
    admins = await get_admins()
    await message.answer(f"Список админов:\n{admins}")


@router.message(lambda m: m.text == "Отправить файл")
async def send_file_button_handler(message: Message, state: FSMContext):
    await message.answer("Отправьте файл для рассылки:")
    await state.set_state(SendFile.waiting_file)

@router.message(lambda m: m.text == "Отправить медиа")
async def send_media_button_handler(message: Message, state: FSMContext):
    await message.answer("Отправьте фото или видео для рассылки:")
    await state.set_state(SendMedia.waiting_media)

@router.message(lambda m: m.text == "Объявление")
async def announcement_button_handler(message: Message, state: FSMContext):
    await message.answer("Введите текст объявления для всех групп:")
    await state.set_state(Announcement.waiting_text)

@router.message(lambda m: m.text == "Список групп")
async def group_list_button_handler(message: Message):
    groups = await group_service.get_all_active_groups()  # Заглушка
    await message.answer(
        "Список групп:\n" +
        "\n".join([f"{i+1}. {g['title']} (ID:{g['chat_id']})" for i, g in enumerate(groups)])
    )
 
@router.message(lambda m: m.text == "Удалить последнее")
async def delete_last_button_handler(message: Message, state: FSMContext):
    await message.answer("Введите ID группы для удаления последнего сообщения:")
    await state.set_state(DeleteLast.waiting_group)

@router.message(lambda m: m.text == "Удалить везде")
async def delete_last_all_button_handler(message: Message):
    await message.answer("Последние сообщения удалены во всех группах")

@router.message(lambda m: m.text == "Установить описание")
async def set_description_button_handler(message: Message, state: FSMContext):
    await message.answer("Введите описание для файлов:")
    await state.set_state(SetDescription.waiting_description)

@router.message(lambda m: m.text == "<- Меню")
async def back_button_handler(message: Message):
    await message.answer("Возврат в главное меню", reply_markup=admin_main_kb())

@router.message(Announcement.waiting_text)
async def dannouncement(message: Message, state: FSMContext):
    text = message.text
    await message.answer(await send_announcement(message.from_user.id, text, message.bot))
    await state.clear()

@router.message(Command("delete_last"))
async def start_delete_last(message: Message, state: FSMContext):
    # Получаем доступные диапазоны времени из базы
    ranges = await get_sent_message_time_ranges()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}", callback_data=f"range_{start.strftime('%H_%M')}_{end.strftime('%H_%M')}")]
        for start, end in ranges
    ] + [[InlineKeyboardButton(text="Ввести вручную", callback_data="manual_input")]])
    await message.answer("Выберите диапазон времени или введите вручную:", reply_markup=kb)
    await state.set_state(DeleteMessagesFSM.waiting_time_range)

@router.callback_query(DeleteMessagesFSM.waiting_time_range)
async def process_time_range_callback(call: CallbackQuery, state: FSMContext):
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.now(tz)
    today = now.date()
    if call.data.startswith("range_"):
        # Парсим время из callback_data
        _, start_h, start_m, end_h, end_m = call.data.split("_")
        start_time = datetime.combine(today, datetime.strptime(f"{start_h}:{start_m}", "%H:%M").time(), tz)
        end_time = datetime.combine(today, datetime.strptime(f"{end_h}:{end_m}", "%H:%M").time(), tz)
        start_time = start_time.replace(tzinfo=None)
        end_time = end_time.replace(tzinfo=None)
        await state.update_data(start_time=start_time, end_time=end_time)
        messages = await get_sent_messages_in_range(start_time, end_time)
        if not messages:
            await call.message.answer("Сообщения не найдены в этом диапазоне.")
            await state.clear()
            return
        text = f"Будут удалены {len(messages)} сообщений. Подтвердить?"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_delete")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_delete")]
        ])
        await call.message.answer(text, reply_markup=kb)
        await state.set_state(DeleteMessagesFSM.waiting_confirm)
    elif call.data == "manual_input":
        await call.message.answer("Введите диапазон времени в формате HH:MM-HH:MM")

@router.message(DeleteMessagesFSM.waiting_time_range)
async def process_manual_time_range(message: Message, state: FSMContext):
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.now(tz)
    today = now.date()
    try:
        time_range = message.text.replace(" ", "")
        start_str, end_str = time_range.split("-")
        start_time = datetime.combine(today, datetime.strptime(start_str, "%H:%M").time(), tz)
        end_time = datetime.combine(today, datetime.strptime(end_str, "%H:%M").time(), tz)
    except Exception:
        await message.answer("Некорректный формат. Введите в формате HH:MM-HH:MM")
        return
    # Делаем naive datetime
    start_time = start_time.replace(tzinfo=None)
    end_time = end_time.replace(tzinfo=None)
    await state.update_data(start_time=start_time, end_time=end_time)
    messages = await get_sent_messages_in_range(start_time, end_time)
    if not messages:
        await message.answer("Сообщения не найдены в этом диапазоне.")
        await state.clear()
        return
    text = f"Будут удалены {len(messages)} сообщений. Подтвердить?"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_delete")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_delete")]
    ])
    await message.answer(text, reply_markup=kb)
    await state.set_state(DeleteMessagesFSM.waiting_confirm)

@router.callback_query(DeleteMessagesFSM.waiting_confirm)
async def confirm_delete_callback(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    start_time = data["start_time"]
    end_time = data["end_time"]
    await call.message.answer(await delete_sent_messages_in_range(start_time, end_time, call.bot))
    await state.clear()

@router.callback_query(lambda c: c.data == "cancel_delete")
async def cancel_delete_callback(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Удаление отменено.")
    await state.clear()

# @router.message()
# async def block_other_commands(message: Message):
#     user_id = message.from_user.id if message.from_user else None
#     if not user_id:
#         await message.answer("Ошибка: не удалось определить пользователя.")
#         return
#     if not await isAdmin(user_id):
#         await message.answer(f"Недостаточно прав. \nДля доступа к функциям введите /admin_login и код.")
#     else:
#         await message.answer(f"Вы админ. \nНе доступная команда")
        
        