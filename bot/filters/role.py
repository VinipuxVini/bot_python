from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot.database.database import get_user_by_telegram_id

class RoleFilter(BaseFilter):
    def __init__(self, roles: list[str]):
        self.roles = roles

    async def __call__(self, message: Message):
        user_id = message.from_user.id if message.from_user else None
        if not user_id:
            await message.answer("Ошибка: не удалось определить пользователя.")
            return
        user = await get_user_by_telegram_id(user_id)
        return user and user['role'] in self.roles

class OnlyRole(BaseFilter):
    def __init__(self, allowed_commands: list[str]):
        self.allowed_commands = allowed_commands or ["/start"]

    async def __call__(self, message: Message):
        if message.text and any(message.text.startswith(cmd) for cmd in self.allowed_commands):
            return True
        user_id = message.from_user.id if message.from_user else None
        if not user_id:
            await message.answer("Ошибка: не удалось определить пользователя.")
            return
        user = await get_user_by_telegram_id(user_id)
        return user and user['role'] in ["admin", "moderator"]
