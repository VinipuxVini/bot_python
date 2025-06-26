from aiogram.types import User
from bot.services import group_service
from config.config import config
from bot.database import database as db

async def checkUser(telegram_id):
    if await db.get_user_by_telegram_id(telegram_id):
        return True
    else:
        return False
    
async def get_user_by_telegram_id(telegram_id):
   user = await db.get_user_by_telegram_id(int(telegram_id))
   if user:
       return user
   else:
       return "Нет пользователя с таким id"

async def add_user(message):
    telegram_id=message.from_user.id
    full_name=message.from_user.full_name
    username=message.from_user.username
    role = 'user'
    if not await checkUser(telegram_id):
        await db.add_user(telegram_id,full_name,username,role)
    
async def isAdmin(telegram_id: int) -> bool:
    user = await db.get_user_by_telegram_id(telegram_id)
    if user:
        return user['role'] == 'admin'
    return False

async def get_users():
    return await db.get_all_users()

async def check_admin_code(code: str) -> bool:
    return code == config.admin_code

async def get_admins():
    admin_list= await db.get_admins()
    admin_str = ""
    for admin in admin_list:
        admin_str += f"{admin['full_name']} - @{admin['username']} - tg_id:{admin['telegram_id']} - {admin['role']} \n"
    return admin_str

async def make_admin(telegram_id: int):
    await db.set_user_role(telegram_id, "admin")
    
async def delete_admin_role(admin_id:str):
    await db.set_user_role(int(admin_id), "user")

async def send_announcement(text, bot):
    groups = await group_service.get_all_active_groups()
    succes_count = 0
    failed_count = 0
    for group in groups:
        try:
            await bot.send_message(group['chat_id'], text)
            succes_count += 1
        except Exception as e:
            await db.add_log(group['title'], str(e), "error")
            failed_count += 1
            await bot.send_message(config.admin_id, f"Ошибка при отправке объявления в группу {group['title']}:\n{str(e)}")
            pass
    return f"✅ Отправлено: {succes_count}\n❌ Не отправлено: {failed_count}"