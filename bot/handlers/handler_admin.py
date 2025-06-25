from aiogram import Router, F
from aiogram.filters import Command
from bot.filters.role import RoleFilter
from aiogram.types import Message

router = Router()

@router.message(Command("get_report"), RoleFilter(["admin", "moderator"]))
async def get_report_handler(message: Message):
    # Логика получения отчёта
    await message.answer("Отчёт за неделю...")
    
@router.message(Command("help"), RoleFilter(["admin"]))
async def help_handler(message: Message):
    await message.answer("Помощь по командам")