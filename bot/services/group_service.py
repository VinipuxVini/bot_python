from typing import Optional, Dict, Any
import asyncpg
from bot.database import database as db


async def get_all_active_groups():
    groups = await db.get_all_groups()
    return [g for g in groups if g.get('is_active', True)]

async def add_group(chat_id: int, title: str):
    await db.add_group(chat_id, title)

async def update_group(chat_id: int, title: str):
    await db.update_group(chat_id, title)

async def deactivate_group(chat_id: int):
    await db.deactivate_group(chat_id)

async def get_group_by_chat_id(chat_id: int) -> Optional[Dict[str, Any]]:
    return await db.get_group_by_chat_id(chat_id)

async def update_group_chat_id(old_chat_id: int, new_chat_id: int):
    # Обновление chat_id, если группа стала супергруппой
    _db_pool: Optional[asyncpg.Pool] = db._db_pool
    if _db_pool is None:
        raise Exception('Database pool is not initialized')
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE groups SET chat_id = $1 WHERE chat_id = $2",
            new_chat_id, old_chat_id
        )

async def get_active_groups_by_title(title: str):
    _db_pool = db._db_pool
    if _db_pool is None:
        raise Exception('Database pool is not initialized')
    rows = await _db_pool.fetch("SELECT * FROM groups WHERE title = $1 AND is_active = TRUE", title)
    return [dict(row) for row in rows]

async def handle_group_added(group_id: int, group_title: str, bot, admin_ids, now):
    group = await db.get_group_by_chat_id(group_id)
    if group:
        if not group.get("is_active", True):
            await db.activate_group(group_id, group_title)
            text = f"📢 ➕ Добавление группы\n📅 Дата: {now}\n👥 Название: {group_title}\n🆔 ID: {group_id}"
            for admin_id in admin_ids:
                try:
                    await bot.send_message(admin_id, text)
                except Exception:
                    pass
        # Если уже активна — ничего не делаем
        return
    # Если группы с этим chat_id нет, ищем по title (смена chat_id)
    all_groups = await db.get_active_groups_by_title(group_title)
    for g in all_groups:
        await db.delete_group(g["chat_id"])
    await db.add_group(group_id, group_title)
    text = f"📢 ➕ Добавление группы\n📅 Дата: {now}\n👥 Название: {group_title}\n🆔 ID: {group_id}"
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass

async def handle_group_removed(group_id: int, group_title: str, bot, admin_ids, now):
    await db.deactivate_group(group_id)
    text = f"📢 ➖ Удаление группы\n📅 Дата: {now}\n👥 Название: {group_title}\n🆔 ID: {group_id}"
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass

async def handle_group_title_changed(group_id: int, new_title, bot, admin_ids, now):
    group = await db.get_group_by_chat_id(group_id)
    old_title = ""
    if not group:
        await db.add_group(group_id, new_title)
        
    if group is not None and isinstance(group, dict):
        old_title = group.get("title") or ""
    await db.update_group(group_id, new_title)
    text = f"📢 ✏️ Изменение названия группы\n📅 Дата: {now}\n👥 Было: {old_title}\n👥 Стало: {new_title}\n🆔 ID: {group_id}"
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass

async def process_group_membership_change(event, bot):
    chat: Chat = event.chat
    new_status = event.new_chat_member.status
    old_status = event.old_chat_member.status
    now = datetime.datetime.now().strftime('%d.%m.%Y, %H:%M:%S')
    group_id = chat.id
    group_title = chat.title or "Без названия"
    admins = await db.get_admins()
    admin_ids = [a["telegram_id"] for a in admins if isinstance(a, dict) and "telegram_id" in a]

    group = await db.get_group_by_chat_id(group_id)
    # Проверка на изменение названия
    if group and group.get("is_active", True) and group.get("title") != group_title:
        old_title = group.get("title") or ""
        await handle_group_title_changed(group_id, old_title, group_title, bot, admin_ids, now)

    if new_status in ("member", "administrator") and old_status == "left":
        await handle_group_added(group_id, group_title, bot, admin_ids, now)
    elif new_status == "left" and old_status in ("member", "administrator"):
        await handle_group_removed(group_id, group_title, bot, admin_ids, now)

async def get_sent_messages_in_range(start_time, end_time):
    return await db.get_sent_messages_in_range(start_time, end_time)

async def delete_sent_messages_in_range(start_time, end_time, bot):
    messages = await db.get_sent_messages_in_range(start_time, end_time)
    deleted = 0
    failed_count = 0
    for msg in messages:
        try:
            await bot.delete_message(msg["chat_id"], msg["message_id"])
            await db.delete_sent_message(msg["chat_id"], msg["message_id"])
            deleted += 1
        except Exception:
            await db.add_log(msg["chat_id"], str(e), "error")
            failed_count += 1
            pass
    return f"Всего {len(messages)}\n✅ Удалено: {deleted}\n❌ Не удалено: {failed_count} "

async def get_sent_message_time_ranges(interval_minutes=30):
    return await db.get_sent_message_time_ranges(interval_minutes)