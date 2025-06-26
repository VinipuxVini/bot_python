import datetime
from aiogram import Router
from aiogram.types import  ChatMemberUpdated, Message
from bot.database.database import get_admins
from bot.services import group_service
from aiogram import Bot

router = Router()


@router.my_chat_member()
async def group_membership_handler(event: ChatMemberUpdated, bot: Bot):
    await group_service.process_group_membership_change(event, bot)
    

@router.message()
async def group_title_changed_handler(message: Message, bot: Bot):
    if message.new_chat_title:
        await group_service.handle_group_title_changed(
            group_id=message.chat.id,
            new_title=message.new_chat_title,
            bot=bot,
            admin_ids=[a["telegram_id"] for a in await get_admins() if isinstance(a, dict) and "telegram_id" in a],
            now=datetime.datetime.now().strftime('%d.%m.%Y, %H:%M:%S')
        )