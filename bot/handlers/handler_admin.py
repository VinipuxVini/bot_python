from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from bot.filters.role import OnlyRole, RoleFilter
from bot.keyboards.keyboard_admin import admin_main_kb
from bot.services.admin_service import get_admins, isAdmin

router = Router()
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
    
# Обработка кнопок
@router.message(lambda m: m.text == "Отчёт")
async def report_button_handler(message: Message):
    await message.answer("Отчёт за неделю...")

@router.message(lambda m: m.text == "Список админов")
async def admin_list_button_handler(message: Message):
    admins = await get_admins()
    await message.answer(f"Список админов:\n{admins}")

@router.message(lambda m: m.text == "Удалить админа")
async def delete_admin_button_handler(message: Message, state: FSMContext):
    await message.answer("Введите id пользователя")
    await state.set_state(DeleteAdmin.waiting_admin_id)

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
    groups = ["Группа 1", "Группа 2", "Группа 3"]  # Заглушка
    await message.answer(f"Список групп:\n" + "\n".join(groups))

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

@router.message(lambda m: m.text == "<- Назад")
async def back_button_handler(message: Message):
    await message.answer("Возврат в главное меню", reply_markup=admin_main_kb())

@router.message(DeleteAdmin.waiting_admin_id)
async def delete_admin_id_handler(message: Message, state: FSMContext):
    admin_id = message.text
    # Здесь логика удаления админа
    await message.answer(f"Админ {admin_id} удален")
    await state.clear()






@router.message()
async def block_other_commands(message: Message):
    if not await isAdmin(message.from_user.id):
        await message.answer(f"Недостаточно прав. \nДля доступа к функциям введите /admin_login и код.")
    else:
        await message.answer(f"Вы админ. \nНе доступная команда")
        
        