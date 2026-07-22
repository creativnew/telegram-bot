"""
╔══════════════════════════════════════════════════════════════╗
║              START HANDLER - aiogram 2.x                     ║
╚══════════════════════════════════════════════════════════════╝
"""

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from database import db
from config import OWNER_ID
from utils.keyboards import get_start_keyboard, get_language_keyboard
from utils.language import get_text
from utils.helpers import Logger


def router(dp: Dispatcher):
    """Handlerlarni ro'yxatdan o'tkazish"""

    @dp.message_handler(Command("start"))
    async def cmd_start(message: types.Message):
        """Start komandasi"""
        user = message.from_user

        # Foydalanuvchini bazaga qo'shish
        await db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            status='active'
        )
        lang = await db.get_user_language(user.id)

        # Owner uchun maxsus xabar
        if user.id == OWNER_ID:
            await message.answer(
                f"👑 <b>Salom, {user.first_name}!</b>\n\n"
                f"Siz bot egasisiz.\n\n"
                f"Admin panelga kirish: /panel\n"
                f"Yordam: /help",
                parse_mode='HTML',
                reply_markup=get_start_keyboard(lang)
            )
            return

        # Admin uchun xabar
        if await db.is_admin(user.id):
            await message.answer(
                f"👤 <b>Salom, {user.first_name}!</b>\n\n"
                f"Siz adminsiz.\n\n"
                f"Admin panel: /panel\n"
                f"Yordam: /help",
                parse_mode='HTML'
            )
            return

        # Oddiy foydalanuvchi
        await message.answer(
            get_text('welcome', lang, name=user.first_name),
            parse_mode='HTML'
        )

    @dp.message_handler(Command("help"))
    async def cmd_help(message: types.Message):
        """Yordam komandasi"""
        lang = await db.get_user_language(message.from_user.id)
        help_text = get_text('help_text', lang)
        await message.answer(help_text, parse_mode='HTML')

    @dp.callback_query_handler(lambda c: c.data == "help")
    async def callback_help(callback: types.CallbackQuery):
        """Help callback"""
        await callback.message.edit_text(
            "📋 <b>Yordam</b>\n\n"
            "Bot guruhni avtomatik nazorat qiladi:\n"
            "• Verifikatsiya\n"
            "• Anti-reklama\n"
            "• Anti-bot\n"
            "• Anti-so'kinish\n\n"
            "Admin panel: /panel",
            parse_mode='HTML'
        )
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data == "lang")
    async def callback_language(callback: types.CallbackQuery):
        """Language selection callback"""
        lang = await db.get_user_language(callback.from_user.id)
        await callback.message.edit_text(
            get_text('choose_language', lang),
            parse_mode='HTML',
            reply_markup=get_language_keyboard(lang)
        )
        await callback.answer()
