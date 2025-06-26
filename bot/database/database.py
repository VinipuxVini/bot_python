import asyncpg
from typing import Optional, Dict, Any, List
import pytz
from datetime import datetime, timedelta

_db_pool: Optional[asyncpg.Pool] = None


async def connect_db(dsn: str):
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=5)

# USERS
async def get_all_users() -> List[Dict[str, Any]]:
    async with _db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM users")
        return [dict(row) for row in rows]

async def get_admins() -> List[Dict[str, Any]]:
    async with _db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM users WHERE role = 'admin' or role = 'moderator'")
        return [dict(row) for row in rows]

async def get_user_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    async with _db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
        return dict(row) if row else None

async def add_user(telegram_id: int, full_name: str, username: str, role: str = 'user'):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (telegram_id, full_name, username, role) VALUES ($1, $2, $3, $4) ON CONFLICT (telegram_id) DO NOTHING",
            telegram_id, full_name, username, role
        )

async def update_user(telegram_id: int, full_name: str = None, username: str = None):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET full_name = COALESCE($2, full_name), username = COALESCE($3, username) WHERE telegram_id = $1",
            telegram_id, full_name, username
        )

async def set_user_role(telegram_id: int, role: str):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET role = $2 WHERE telegram_id = $1",
            telegram_id, role
        )

async def deactivate_user(telegram_id: int):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET is_active = FALSE WHERE telegram_id = $1",
            telegram_id
        )

# GROUPS
async def get_group_by_chat_id(chat_id: int) -> Optional[Dict[str, Any]]:
    async with _db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM groups WHERE chat_id = $1", chat_id)
        return dict(row) if row else None

async def add_group(chat_id: int, title: str):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO groups (chat_id, title) VALUES ($1, $2) ON CONFLICT (chat_id) DO NOTHING",
            chat_id, title
        )

async def update_group(chat_id: int, title: str):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE groups SET title = $2 WHERE chat_id = $1",
            chat_id, title
        )

async def deactivate_group(chat_id: int):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE groups SET is_active = FALSE WHERE chat_id = $1",
            chat_id
        )
        
async def delete_group(chat_id: int):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM groups WHERE chat_id = $1",
            chat_id
        )

async def get_all_groups():
    async with _db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM groups WHERE is_active = TRUE")
        return [dict(row) for row in rows]

async def activate_group(chat_id: int, title: str = None):
    async with _db_pool.acquire() as conn:
        if title:
            await conn.execute(
                "UPDATE groups SET is_active = TRUE, title = $2 WHERE chat_id = $1",
                chat_id, title
            )
        else:
            await conn.execute(
                "UPDATE groups SET is_active = TRUE WHERE chat_id = $1",
                chat_id
            )

async def get_active_groups_by_title(title: str):
    async with _db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM groups WHERE title = $1 AND is_active = TRUE", title)
        return [dict(row) for row in rows]

# REPORTS
async def add_report(week: int, date_from, date_to, total_files: int, success_files: int, failed_files: list, sent_groups: list):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO reports (week, date_from, date_to, total_files, success_files, failed_files, sent_groups) VALUES ($1, $2, $3, $4, $5, $6, $7)",
            week, date_from, date_to, total_files, success_files, failed_files, sent_groups
        )

async def get_report_by_week(week: int) -> Optional[Dict[str, Any]]:
    async with _db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM reports WHERE week = $1 ORDER BY created_at DESC LIMIT 1", week)
        return dict(row) if row else None

async def get_last_report() -> Optional[Dict[str, Any]]:
    async with _db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM reports ORDER BY created_at DESC LIMIT 1")
        return dict(row) if row else None

# LOGS (ERRORS)
async def add_log(user_id: int, error_text: str, level: str = 'error'):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO logs (user_id, error_text, level) VALUES ($1, $2, $3)",
            user_id, error_text, level
        )

async def get_logs_by_user(user_id: int) -> List[Dict[str, Any]]:
    async with _db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM logs WHERE user_id = $1 ORDER BY created_at DESC", user_id)
        return [dict(row) for row in rows]

async def get_all_errors() -> List[Dict[str, Any]]:
    async with _db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM logs WHERE level = 'error' ORDER BY created_at DESC")
        return [dict(row) for row in rows]





async def save_sent_message(chat_id: int, message_id: int, sent_at):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO sent_messages (chat_id, message_id, sent_at) VALUES ($1, $2, $3)",
            chat_id, message_id, sent_at
        )

async def get_sent_messages_in_range(start_time, end_time):
    async with _db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM sent_messages WHERE sent_at BETWEEN $1 AND $2",
            start_time, end_time
        )
        return [dict(row) for row in rows]

async def delete_sent_message(chat_id: int, message_id: int):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM sent_messages WHERE chat_id = $1 AND message_id = $2",
            chat_id, message_id
        )

async def delete_old_sent_messages():
    # Удаляет сообщения старше 24 часов (GMT+5)
    tz = pytz.timezone('Asia/Tashkent')  # GMT+5
    now = datetime.now(tz)
    cutoff = now - timedelta(hours=24)
    async with _db_pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM sent_messages WHERE sent_at < $1",
            cutoff
        )

async def get_sent_message_time_ranges(interval_minutes=30):
    # Возвращает список уникальных временных диапазонов (start, end) для сообщений за последние 24 часа
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.now(tz).replace(tzinfo=None)
    cutoff = now - timedelta(hours=24)
    async with _db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT sent_at FROM sent_messages WHERE sent_at >= $1 ORDER BY sent_at ASC",
            cutoff
        )
        times = [row['sent_at'] for row in rows]
    # Группируем по интервалам
    ranges = set()
    for t in times:
        minutes = (t.hour * 60 + t.minute) // interval_minutes * interval_minutes
        start = t.replace(hour=minutes // 60, minute=minutes % 60, second=0, microsecond=0)
        end = start + timedelta(minutes=interval_minutes)
        ranges.add((start, end))
    return sorted(list(ranges))

