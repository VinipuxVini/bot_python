from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboards.keyboard_admin import admin_main_kb
from bot.services.admin_service import add_user, check_admin_code, make_admin

router = Router()

class LoginState(StatesGroup):
    waiting_admin_code = State()
    
@router.message(Command("start"))
async def start_handler(message: Message):
    await add_user(message)
    await message.answer("Добро пожаловать! Для доступа к функциям введите /admin_login и код." )

@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer("Помощь по командам")

@router.message(Command("admin_login"))
async def admin_login_start_handler(message: Message, state: FSMContext):
    try:
        await message.answer("Введите 4-значный код администратора:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(LoginState.waiting_admin_code)
    except:
        await message.answer("Недостаточно прав")

@router.message(LoginState.waiting_admin_code)
async def admin_login_check_handler(message: Message, state: FSMContext):
    code = (message.text or "").strip()
    if await check_admin_code(code):
        await make_admin(message.from_user.id)
        await message.answer("Вы авторизованы как администратор!", reply_markup=admin_main_kb())
    else:
        await message.answer("Неверный код. Вы не админ.")
    await state.clear()