from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from bot.filters.role import OnlyRole
from bot.keyboards.keyboard_admin import admin_main_kb
from bot.services.admin_service import add_user, check_admin_code, make_admin, get_users

router = Router()

class AdminLogin(StatesGroup):
    waiting_code = State()

@router.message(Command("start"), OnlyRole())
async def start_handler(message: Message):
    users = await get_users()
    print(users)
    await add_user(message)
    await message.answer("Добро пожаловать! Для доступа к функциям введите /admin_login и код." )

@router.message(Command("admin_login"), OnlyRole(allowed_commands=["/start", "/admin_login"]))
async def admin_login_start(message: Message, state: FSMContext):
    await message.answer("Введите 4-значный код администратора:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminLogin.waiting_code)

@router.message(AdminLogin.waiting_code)
async def admin_login_check(message: Message, state: FSMContext):
    code = message.text.strip()
    if await check_admin_code(code):
        await make_admin(message.from_user.id)
        await message.answer("Вы авторизованы как администратор!", reply_markup=admin_main_kb())
    else:
        await message.answer("Неверный код. Вы не админ.")
    await state.clear()

@router.message(OnlyRole())
async def block_other_commands(message: Message):
    await message.answer("Недостаточно прав. Доступно только /start и авторизация.")

# @router.message()
# async def echo_handler(message: Message):
#     await message.answer("Неправильное значение")