from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from database import db
from config import OWNER_ID, PREMIUM_STICKER
from utils.keyboards import get_start_language_keyboard, get_start_keyboard, get_language_keyboard
from utils.language import get_text
from utils.helpers import Logger


async def _send_welcome(bot, msg_or_callback, user, lang):
    if user.id == OWNER_ID:
        text = (
            f"👑 <b>Salom, {user.first_name}!</b>\n\n"
            f"Siz bot egasisiz.\n\n"
            f"Admin panelga kirish: /panel\n"
            f"Yordam: /help"
        )
        await msg_or_callback.answer(text, parse_mode='HTML', reply_markup=get_start_keyboard(lang))
    elif await db.is_admin(user.id):
        text = (
            f"👤 <b>Salom, {user.first_name}!</b>\n\n"
            f"Siz adminsiz.\n\n"
            f"Admin panel: /panel\n"
            f"Yordam: /help"
        )
        await msg_or_callback.answer(text, parse_mode='HTML')
    else:
        text = get_text('start_welcome', lang, name=user.first_name)
        await msg_or_callback.answer(text, parse_mode='HTML')

    if PREMIUM_STICKER:
        try:
            await bot.send_sticker(chat_id=user.id, sticker=PREMIUM_STICKER)
        except Exception:
            pass


def router(dp: Dispatcher):

    @dp.message_handler(Command("start"))
    async def cmd_start(message: types.Message):
        user = message.from_user

        await db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            status='active'
        )

        existing_lang = await db.get_user_language(user.id)

        if existing_lang and existing_lang != 'uz':
            await _send_welcome(dp.bot, message, user, existing_lang)
            return

        text = (
            f"👋 <b>Salom, {user.first_name}!</b>\n\n"
            f"🌍 <b>Iltimos, tilni tanlang:</b>\n"
            f"Пожалуйста, выберите язык:\n"
            f"Please select a language:"
        )
        await message.answer(text, parse_mode='HTML', reply_markup=get_start_language_keyboard())

    @dp.callback_query_handler(lambda c: c.data.startswith("start_lang:"))
    async def set_start_language(callback: types.CallbackQuery):
        user = callback.from_user
        lang = callback.data.split(":")[1]
        if lang not in ('uz', 'ru', 'en'):
            await callback.answer()
            return

        await db.set_user_language(user.id, lang)
        await _send_welcome(dp.bot, callback.message, user, lang)
        await callback.answer()

    @dp.message_handler(Command("help"))
    async def cmd_help(message: types.Message):
        lang = await db.get_user_language(message.from_user.id)
        help_text = get_text('help_text', lang)
        await message.answer(help_text, parse_mode='HTML')

    @dp.callback_query_handler(lambda c: c.data == "help")
    async def callback_help(callback: types.CallbackQuery):
        lang = await db.get_user_language(callback.from_user.id)
        await callback.message.edit_text(
            get_text('help_text', lang),
            parse_mode='HTML'
        )
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data == "lang")
    async def callback_language(callback: types.CallbackQuery):
        lang = await db.get_user_language(callback.from_user.id)
        await callback.message.edit_text(
            get_text('choose_language', lang),
            parse_mode='HTML',
            reply_markup=get_language_keyboard(lang)
        )
        await callback.answer()
