import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.database import database as db
from config.config import load_config
from bot.handlers.handler_admin import router as admin_router
from bot.handlers.handler_user import router as user_router

# Настройка логов
logging.basicConfig(level=logging.INFO)
config = load_config()

async def main():
    # Подключение к базе данных
    
    await db.connect_db(config.pg_url)

    bot = Bot(token=config.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация роутеров
    dp.include_router(admin_router)
    dp.include_router(user_router)

    print("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⛔ Бот остановлен вручную.")
