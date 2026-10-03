"""
Veritabanı modülü (database.py)
aiosqlite kullanarak hatırlatıcıların SQLite üzerinde asenkron ve kalıcı olarak tutulmasını sağlar.
"""

import aiosqlite
import time
from typing import List, Optional, Dict, Any

DB_PATH = "reminders.db"


async def init_db():
    """Veritabanını ve gerekli tabloları ilklendirir."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER,
                remind_text TEXT NOT NULL,
                target_timestamp REAL NOT NULL,
                created_timestamp REAL NOT NULL,
                is_completed INTEGER DEFAULT 0
            )
        """)
        # Hızlı sorgulama için indeksler
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_due_reminders 
            ON reminders (is_completed, target_timestamp)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_reminders 
            ON reminders (user_id, is_completed)
        """)
        await db.commit()


async def add_reminder(user_id: int, channel_id: Optional[int], remind_text: str, target_timestamp: float) -> int:
    """Yeni bir hatırlatıcı ekler ve eklenen kaydın ID'sini döndürür."""
    created_timestamp = time.time()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO reminders (user_id, channel_id, remind_text, target_timestamp, created_timestamp, is_completed)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (user_id, channel_id, remind_text, target_timestamp, created_timestamp))
        await db.commit()
        return cursor.lastrowid


async def get_due_reminders() -> List[Dict[str, Any]]:
    """Vakti gelmiş veya geçmiş tamamlanmamış hatırlatıcıları getirir."""
    now = time.time()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT id, user_id, channel_id, remind_text, target_timestamp, created_timestamp
            FROM reminders
            WHERE is_completed = 0 AND target_timestamp <= ?
            ORDER BY target_timestamp ASC
        """, (now,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def mark_reminder_completed(reminder_id: int):
    """Hatırlatıcıyı tamamlandı olarak işaretler."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE reminders
            SET is_completed = 1
            WHERE id = ?
        """, (reminder_id,))
        await db.commit()


async def get_user_reminders(user_id: int) -> List[Dict[str, Any]]:
    """Belirli bir kullanıcının bekleyen hatırlatıcılarını getirir."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT id, remind_text, target_timestamp, created_timestamp
            FROM reminders
            WHERE user_id = ? AND is_completed = 0
            ORDER BY target_timestamp ASC
        """, (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def delete_reminder(reminder_id: int, user_id: int) -> bool:
    """Kullanıcıya ait bir hatırlatıcıyı siler. Başarılı ise True döner."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            DELETE FROM reminders
            WHERE id = ? AND user_id = ?
        """, (reminder_id, user_id))
        await db.commit()
        return cursor.rowcount > 0
