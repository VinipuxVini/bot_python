from config.config import config
from bot.database import database as db

async def checkUser(telegram_id):
    if await db.get_user_by_telegram_id(telegram_id):
        return True
    else:
        return False
    
async def add_user(message):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    role = 'user'
    if not await checkUser(telegram_id):
        await db.add_user(telegram_id,full_name,username,role)
    
async def isAdmin(telegram_id: int) -> bool:
    user = await db.get_user_by_telegram_id(telegram_id)
    if user:
        return user['role'] == 'admin' or user['role'] == 'moderator'
    return False

async def get_users():
    return await db.get_all_users()

async def check_admin_code(code: str) -> bool:
    return code == config.admin_code

async def make_admin(telegram_id: int):
    await db.set_user_role(telegram_id, "admin")
    
async def make_moderator(telegram_id: int):
    await db.set_user_role(telegram_id, "moderator")

