"""
╔══════════════════════════════════════════════════════════════╗
║           ADMIN MIDDLEWARE - aiogram 2.x                     ║
║     Faqat adminlar va ownerlar uchun komandalar              ║
╚══════════════════════════════════════════════════════════════╝
"""

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery

from database import db
from config import OWNER_ID


def setup_middleware(dp: Dispatcher):
    """Admin middleware'larini sozlash"""

    @dp.message_handler(commands=['panel', 'broadcast', 'stats', 'admin'])
    async def admin_command_filter(message: Message):
        """Admin komandalarini tekshirish"""
        user_id = message.from_user.id

        is_admin = await db.is_admin(user_id) or user_id == OWNER_ID

        if not is_admin:
            await message.answer(
                "❌ <b>Ruxsat yo'q!</b>\n\n"
                "Bu komanda faqat adminlar uchun.",
                parse_mode='HTML'
            )
            return False

        return True

    @dp.callback_query_handler(lambda c: c.data.startswith(('toggle:', 'broadcast', 'admin_', 'approve:', 'reject:')))
    async def admin_callback_filter(callback: CallbackQuery):
        """Admin callback'larini tekshirish"""
        user_id = callback.from_user.id

        is_admin = await db.is_admin(user_id) or user_id == OWNER_ID

        if not is_admin:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return False

        return True
