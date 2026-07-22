"""
╔══════════════════════════════════════════════════════════════╗
║              DATABASE MANAGER - Ma'lumotlar Bazasi           ║
║              SQLite3 + aiosqlite (Async)                     ║
╚══════════════════════════════════════════════════════════════╝
"""

import aiosqlite
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config import DATABASE_PATH, WARN_LIMIT, MUTE_DURATION_HOURS


class DatabaseManager:
    """Asinxron ma'lumotlar bazasi boshqaruvchisi"""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Bazaga ulanish"""
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        await self._create_tables()
        await self._migrate()
        await self._init_default_settings()
        return self

    async def close(self):
        """Bazadan uzilish"""
        if self._connection:
            await self._connection.close()

    async def _migrate(self):
        """Eski bazaga yangi ustunlarni qo'shish"""
        try:
            await self._connection.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'uz'")
        except Exception:
            pass  # Ustun allaqachon mavjud
        try:
            await self._connection.execute("ALTER TABLE users ADD COLUMN verified_by INTEGER")
        except Exception:
            pass
        try:
            await self._connection.execute("ALTER TABLE users ADD COLUMN verified_at TIMESTAMP")
        except Exception:
            pass
        try:
            await self._connection.execute("ALTER TABLE users ADD COLUMN is_female INTEGER DEFAULT 0")
        except Exception:
            pass
        try:
            await self._connection.execute("ALTER TABLE users ADD COLUMN notes TEXT")
        except Exception:
            pass

    async def _create_tables(self):
        """Barcha jadvallarni yaratish"""

        # Foydalanuvchilar jadvali
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                full_name TEXT,
                phone TEXT,
                photo_id TEXT,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending' CHECK(status IN ('active', 'banned', 'pending', 'rejected')),
                verified_by INTEGER,
                verified_at TIMESTAMP,
                is_female INTEGER DEFAULT 0,
                notes TEXT,
                language TEXT DEFAULT 'uz'
            )
        """)

        # Adminlar jadvali
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_owner INTEGER DEFAULT 0,
                name TEXT
            )
        """)

        # Sozlamalar jadvali
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Ogohlantirishlar jadvali
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                group_id INTEGER,
                reason TEXT,
                warned_by INTEGER,
                warned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                count INTEGER DEFAULT 1
            )
        """)

        # Loglar jadvali
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                user_id INTEGER,
                admin_id INTEGER,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Guruhlar jadvali
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER UNIQUE NOT NULL,
                group_name TEXT,
                group_link TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)

        # Verifikatsiya so'rovlari jadvali
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS verification_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                group_id INTEGER,
                full_name TEXT,
                phone TEXT,
                photo_id TEXT,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                processed_by INTEGER,
                admin_message_id INTEGER
            )
        """)

        await self._connection.commit()

    async def _init_default_settings(self):
        """Boshlang'ich sozlamalarni yaratish"""
        defaults = {
            'verification_enabled': '1',
            'ask_photo_enabled': '1',
            'ask_phone_enabled': '1',
            'antilink_enabled': '1',
            'antibot_enabled': '1',
            'antiswear_enabled': '1',
            'antiflood_enabled': '0',
            'antispam_enabled': '0',
            'antiporn_enabled': '0',
            'captcha_enabled': '0',
            'nightmode_enabled': '0',
            'wordfilter_enabled': '0',
            'media_restrict_enabled': '0',
            'invite_restrict_enabled': '0',
            'userinfo_enabled': '1',
            'namehistory_enabled': '1',
            'user_ranking_enabled': '0',
            'user_search_enabled': '0',
            'welcome_message': '1',
            'welcome_custom_enabled': '1',
            'auto_delete_warnings': '1',
            'rules_enabled': '0',
            'autoreply_enabled': '0',
            'scheduled_enabled': '0',
            'polls_enabled': '0',
            'backup_enabled': '0',
            'log_channel_enabled': '0',
            'blocklist_enabled': '0',
            'group_link': '',
            'group_name': 'Ayollar Guruhi',
            'bot_language': 'uz',
            'flood_limit': '3',
            'flood_interval': '3',
            'night_start': '23:00',
            'night_end': '08:00',
            'custom_words': '',
            'media_type': '0',
        }

        for key, value in defaults.items():
            await self._connection.execute("""
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            """, (key, value))

        await self._connection.commit()

    # ============================================================
    # USERS - Foydalanuvchilar bilan ishlash
    # ============================================================

    async def add_user(self, user_id: int, username: str = None, 
                       first_name: str = None, last_name: str = None,
                       phone: str = None, photo_id: str = None,
                       status: str = 'pending') -> bool:
        """Yangi foydalanuvchi qo'shish"""
        full_name = f"{first_name or ''} {last_name or ''}".strip()

        try:
            await self._connection.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, full_name, phone, photo_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, first_name, last_name, full_name, phone, photo_id, status))
            await self._connection.commit()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Foydalanuvchi ma'lumotlarini olish"""
        async with self._connection.execute(
            'SELECT * FROM users WHERE user_id = ?', (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_user_status(self, user_id: int, status: str, 
                                  verified_by: int = None) -> bool:
        """Foydalanuvchi statusini yangilash"""
        try:
            await self._connection.execute("""
                UPDATE users SET status = ?, verified_by = ?, verified_at = ?
                WHERE user_id = ?
            """, (status, verified_by, datetime.now(), user_id))
            await self._connection.commit()
            return True
        except Exception as e:
            print(f"Error updating user status: {e}")
            return False

    async def get_all_users(self, status: str = None) -> List[Dict[str, Any]]:
        """Barcha foydalanuvchilarni olish"""
        if status:
            async with self._connection.execute(
                'SELECT * FROM users WHERE status = ?', (status,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        else:
            async with self._connection.execute('SELECT * FROM users') as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_users_count(self) -> int:
        """Foydalanuvchilar sonini olish"""
        async with self._connection.execute(
            'SELECT COUNT(*) as count FROM users WHERE status = "active"'
        ) as cursor:
            row = await cursor.fetchone()
            return row['count'] if row else 0

    # ============================================================
    # ADMINS - Adminlar bilan ishlash
    # ============================================================

    async def add_admin(self, user_id: int, added_by: int, name: str = None, 
                        is_owner: bool = False) -> bool:
        """Yangi admin qo'shish"""
        try:
            await self._connection.execute("""
                INSERT OR REPLACE INTO admins (user_id, added_by, name, is_owner)
                VALUES (?, ?, ?, ?)
            """, (user_id, added_by, name, 1 if is_owner else 0))
            await self._connection.commit()
            return True
        except Exception as e:
            print(f"Error adding admin: {e}")
            return False

    async def remove_admin(self, user_id: int) -> bool:
        """Adminni o'chirish"""
        try:
            await self._connection.execute(
                'DELETE FROM admins WHERE user_id = ? AND is_owner = 0', (user_id,)
            )
            await self._connection.commit()
            return True
        except Exception as e:
            print(f"Error removing admin: {e}")
            return False

    async def get_admin(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Admin ma'lumotlarini olish"""
        async with self._connection.execute(
            'SELECT * FROM admins WHERE user_id = ?', (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_all_admins(self) -> List[Dict[str, Any]]:
        """Barcha adminlarni olish"""
        async with self._connection.execute('SELECT * FROM admins') as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def is_admin(self, user_id: int) -> bool:
        """Foydalanuvchi adminmi?"""
        async with self._connection.execute(
            'SELECT * FROM admins WHERE user_id = ?', (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None

    async def is_owner(self, user_id: int) -> bool:
        """Foydalanuvchi egami?"""
        async with self._connection.execute(
            'SELECT * FROM admins WHERE user_id = ? AND is_owner = 1', (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None

    # ============================================================
    # SETTINGS - Sozlamalar bilan ishlash
    # ============================================================

    async def get_setting(self, key: str, default: str = '') -> str:
        """Sozlama qiymatini olish"""
        async with self._connection.execute(
            'SELECT value FROM settings WHERE key = ?', (key,)
        ) as cursor:
            row = await cursor.fetchone()
            return row['value'] if row else default

    async def set_setting(self, key: str, value: str) -> bool:
        """Sozlama qiymatini o'zgartirish"""
        try:
            await self._connection.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value, datetime.now()))
            await self._connection.commit()
            return True
        except Exception as e:
            print(f"Error setting {key}: {e}")
            return False

    async def toggle_setting(self, key: str) -> bool:
        """Sozlamani yoqish/o'chirish (toggle)"""
        current = await self.get_setting(key, '0')
        new_value = '0' if current == '1' else '1'
        await self.set_setting(key, new_value)
        return new_value == '1'

    async def get_bool_setting(self, key: str) -> bool:
        """Boolean sozlama olish"""
        value = await self.get_setting(key, '0')
        return value == '1'

    # ============================================================
    # WARNS - Ogohlantirishlar bilan ishlash
    # ============================================================

    async def add_warn(self, user_id: int, group_id: int = None,
                       reason: str = None, warned_by: int = None) -> int:
        """Ogohlantirish qo'shish va joriy sonini qaytarish"""
        try:
            # Avvalgi ogohlantirishlarni hisoblash
            async with self._connection.execute(
                'SELECT COUNT(*) as count FROM warns WHERE user_id = ?', (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                current_count = row['count'] if row else 0

            # Yangi ogohlantirish qo'shish
            await self._connection.execute("""
                INSERT INTO warns (user_id, group_id, reason, warned_by, count)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, group_id, reason, warned_by, current_count + 1))
            await self._connection.commit()

            return current_count + 1
        except Exception as e:
            print(f"Error adding warn: {e}")
            return 0

    async def get_warns_count(self, user_id: int) -> int:
        """Foydalanuvchining ogohlantirishlar soni"""
        async with self._connection.execute(
            'SELECT COUNT(*) as count FROM warns WHERE user_id = ?', (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row['count'] if row else 0

    async def clear_warns(self, user_id: int) -> bool:
        """Foydalanuvchining ogohlantirishlarini tozalash"""
        try:
            await self._connection.execute(
                'DELETE FROM warns WHERE user_id = ?', (user_id,)
            )
            await self._connection.commit()
            return True
        except Exception as e:
            print(f"Error clearing warns: {e}")
            return False

    async def should_mute(self, user_id: int) -> bool:
        """Foydalanuvchini mut qilish kerakmi?"""
        count = await self.get_warns_count(user_id)
        return count >= WARN_LIMIT

    # ============================================================
    # VERIFICATION REQUESTS - Verifikatsiya so'rovlari
    # ============================================================

    async def add_verification_request(self, user_id: int, group_id: int,
                                        full_name: str, phone: str,
                                        photo_id: str) -> int:
        """Verifikatsiya so'rovini qo'shish"""
        try:
            cursor = await self._connection.execute("""
                INSERT INTO verification_requests 
                (user_id, group_id, full_name, phone, photo_id)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, group_id, full_name, phone, photo_id))
            await self._connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding verification request: {e}")
            return 0

    async def update_verification_status(self, request_id: int, status: str,
                                          processed_by: int) -> bool:
        """Verifikatsiya statusini yangilash"""
        try:
            await self._connection.execute("""
                UPDATE verification_requests 
                SET status = ?, processed_at = ?, processed_by = ?
                WHERE id = ?
            """, (status, datetime.now(), processed_by, request_id))
            await self._connection.commit()
            return True
        except Exception as e:
            print(f"Error updating verification: {e}")
            return False

    async def get_verification_request(self, request_id: int) -> Optional[Dict[str, Any]]:
        """Verifikatsiya so'rovini olish"""
        async with self._connection.execute(
            'SELECT * FROM verification_requests WHERE id = ?', (request_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    # ============================================================
    # GROUPS - Guruhlar bilan ishlash
    # ============================================================

    async def add_group(self, group_id: int, group_name: str = None,
                        group_link: str = None) -> bool:
        """Guruh qo'shish"""
        try:
            await self._connection.execute("""
                INSERT OR REPLACE INTO groups (group_id, group_name, group_link)
                VALUES (?, ?, ?)
            """, (group_id, group_name, group_link))
            await self._connection.commit()
            return True
        except Exception as e:
            print(f"Error adding group: {e}")
            return False

    async def get_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Guruh ma'lumotlarini olish"""
        async with self._connection.execute(
            'SELECT * FROM groups WHERE group_id = ?', (group_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    # ============================================================
    # LOGS - Loglar bilan ishlash
    # ============================================================

    async def add_log(self, action: str, user_id: int = None,
                      admin_id: int = None, details: str = None) -> bool:
        """Yangi log qo'shish"""
        try:
            await self._connection.execute("""
                INSERT INTO logs (action, user_id, admin_id, details)
                VALUES (?, ?, ?, ?)
            """, (action, user_id, admin_id, details))
            await self._connection.commit()
            return True
        except Exception as e:
            print(f"Error adding log: {e}")
            return False

    async def get_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """So'nggi loglarni olish"""
        async with self._connection.execute(
            'SELECT * FROM logs ORDER BY created_at DESC LIMIT ?', (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ============================================================
    # STATISTICS - Statistika
    # ============================================================

    # ============================================================
    # LANGUAGE - Til boshqaruvi
    # ============================================================

    async def get_user_language(self, user_id: int) -> str:
        """Foydalanuvchi tilini olish"""
        async with self._connection.execute(
            'SELECT language FROM users WHERE user_id = ?', (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row['language'] if row else 'uz'

    async def set_user_language(self, user_id: int, lang: str) -> bool:
        """Foydalanuvchi tilini o'zgartirish"""
        try:
            await self._connection.execute(
                'UPDATE users SET language = ? WHERE user_id = ?', (lang, user_id)
            )
            await self._connection.commit()
            return True
        except Exception as e:
            print(f"Error setting language: {e}")
            return False

    async def get_bot_language(self) -> str:
        """Bot tilini olish"""
        return await self.get_setting('bot_language', 'uz')

    async def set_bot_language(self, lang: str) -> bool:
        """Bot tilini o'zgartirish"""
        return await self.set_setting('bot_language', lang)

    async def get_statistics(self) -> Dict[str, Any]:
        """Umumiy statistika"""
        stats = {}

        # Jami foydalanuvchilar
        async with self._connection.execute(
            'SELECT COUNT(*) as count FROM users'
        ) as cursor:
            stats['total_users'] = (await cursor.fetchone())['count']

        # Faol foydalanuvchilar
        async with self._connection.execute(
            'SELECT COUNT(*) as count FROM users WHERE status = "active"'
        ) as cursor:
            stats['active_users'] = (await cursor.fetchone())['count']

        # Kutilayotganlar
        async with self._connection.execute(
            'SELECT COUNT(*) as count FROM users WHERE status = "pending"'
        ) as cursor:
            stats['pending_users'] = (await cursor.fetchone())['count']

        # Bloklanganlar
        async with self._connection.execute(
            'SELECT COUNT(*) as count FROM users WHERE status = "banned"'
        ) as cursor:
            stats['banned_users'] = (await cursor.fetchone())['count']

        # Adminlar soni
        async with self._connection.execute(
            'SELECT COUNT(*) as count FROM admins'
        ) as cursor:
            stats['total_admins'] = (await cursor.fetchone())['count']

        # Bugun qo'shilganlar
        today = datetime.now().strftime('%Y-%m-%d')
        async with self._connection.execute(
            'SELECT COUNT(*) as count FROM users WHERE DATE(join_date) = ?', (today,)
        ) as cursor:
            stats['today_joined'] = (await cursor.fetchone())['count']

        return stats


# Global database instance
db = DatabaseManager()
