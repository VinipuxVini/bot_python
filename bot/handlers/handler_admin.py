from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from bot.filters.role import RoleFilter
from bot.keyboards.keyboard_admin import admin_main_kb
from bot.services import group_service
from bot.services.admin_service import get_admins, isAdmin, send_announcement

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
    await message.answer(await send_announcement(text, message.bot))
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
        
        