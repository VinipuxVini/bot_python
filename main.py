import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.database import database as db
from config.config import load_config
from bot.handlers.handler_admin import router
from bot.handlers.handler_user import router as router_user
# Настройка логов
logging.basicConfig(level=logging.INFO)
config = load_config()

async def main():
    # Подключение к базе данных
    
    await db.connect_db(config.pg_url)

    bot = Bot(token=config.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    await bot.set_my_commands([
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="help", description="Помощь по командам"),
        BotCommand(command="admin_login", description="Вход в админку"),
    ])
    # Регистрация роутеров
    dp.include_router(router_user)
    dp.include_router(router)

    print("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⛔ Бот остановлен вручную.")
