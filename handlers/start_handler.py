from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command

from database import db
from config import OWNER_ID, PREMIUM_STICKER
from utils.keyboards import (
    get_grouphelp_keyboard, get_start_language_keyboard,
    get_start_keyboard, get_language_keyboard
)
from utils.language import get_text
from utils.helpers import Logger


async def _send_personal_welcome(bot, message, user, lang):
    if user.id == OWNER_ID:
        text = (
            f"👑 <b>Salom, {user.first_name}!</b>\n\n"
            f"Siz bot egasisiz.\n\n"
            f"Admin panelga kirish: /panel\n"
            f"Yordam: /help"
        )
        await message.answer(text, parse_mode='HTML', reply_markup=get_start_keyboard(lang))
    elif await db.is_admin(user.id):
        text = (
            f"👤 <b>Salom, {user.first_name}!</b>\n\n"
            f"Siz adminsiz.\n\n"
            f"Admin panel: /panel\n"
            f"Yordam: /help"
        )
        await message.answer(text, parse_mode='HTML')
    else:
        text = get_text('start_welcome', lang, name=user.first_name)
        await message.answer(text, parse_mode='HTML')

    if PREMIUM_STICKER:
        try:
            await bot.send_sticker(chat_id=user.id, sticker=PREMIUM_STICKER)
        except Exception:
            pass


def router(dp: Dispatcher):

    @dp.message_handler(Command("start"))
    async def cmd_start(message: types.Message):
        user = message.from_user
        bot = dp.bot

        await db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            status='active'
        )

        existing_lang = await db.get_user_language(user.id)

        if existing_lang != 'uz':
            await _send_personal_welcome(bot, message, user, existing_lang)
            return

        bot_me = await bot.get_me()
        bot_name = bot_me.first_name
        bot_username = bot_me.username
        await db.set_setting('bot_username', bot_username)

        links = await db.get_bot_links()
        group_link = links['group_link'] or f"https://t.me/{bot_username}?startgroup=admin"
        channel_link = links['channel_link']
        support_link = links['support_link']

        text = (
            f"<b>👋 {bot_name} ga xush kelibsiz!</b>\n\n"
            f"• Bu bot guruhlaringizni boshqarishga yordam beradi\n"
            f"• Anti-spam, verifikatsiya, anti-link va boshqalar\n"
            f"• Meni guruhingizga qo'shing va admin huquqini bering\n\n"

            f"<b>👋 Добро пожаловать в {bot_name}!</b>\n\n"
            f"• Этот бот помогает управлять группами\n"
            f"• Анти-спам, верификация, анти-ссылки и другое\n"
            f"• Добавьте меня в вашу группу и дайте права админа\n\n"

            f"👑 <b>1 357 413</b> monthly users"
        )

        await message.answer(
            text,
            parse_mode='HTML',
            reply_markup=get_grouphelp_keyboard(bot_username, group_link, channel_link, support_link)
        )

        if PREMIUM_STICKER:
            try:
                await bot.send_sticker(chat_id=user.id, sticker=PREMIUM_STICKER)
            except Exception:
                pass

    @dp.callback_query_handler(lambda c: c.data == "start_lang_menu")
    async def show_start_languages(callback: types.CallbackQuery):
        await callback.message.edit_text(
            "🌐 <b>Select language / Выберите язык / Tilni tanlang:</b>",
            parse_mode='HTML',
            reply_markup=get_start_language_keyboard()
        )
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data.startswith("start_lang:"))
    async def set_start_language(callback: types.CallbackQuery):
        user = callback.from_user
        lang = callback.data.split(":")[1]
        if lang not in ('uz', 'ru', 'en'):
            await callback.answer()
            return

        await db.set_user_language(user.id, lang)
        await _send_personal_welcome(dp.bot, callback.message, user, lang)
        await callback.answer()

    @dp.message_handler(Command("help"))
    async def cmd_help(message: types.Message):
        lang = await db.get_user_language(message.from_user.id)
        await message.answer(get_text('help_text', lang), parse_mode='HTML')

    @dp.callback_query_handler(lambda c: c.data == "help")
    async def callback_help(callback: types.CallbackQuery):
        bot_me = await dp.bot.get_me()
        bot_name = bot_me.first_name
        bot_username = bot_me.username
        links = await db.get_bot_links()
        group_link = links['group_link'] or f"https://t.me/{bot_username}?startgroup=admin"
        channel_link = links['channel_link']
        support_link = links['support_link']

        text = (
            f"<b>👋 {bot_name} ga xush kelibsiz!</b>\n\n"
            f"• Bu bot guruhlaringizni boshqarishga yordam beradi\n"
            f"• Anti-spam, verifikatsiya, anti-link va boshqalar\n"
            f"• Meni guruhingizga qo'shing va admin huquqini bering\n\n"

            f"<b>👋 Добро пожаловать в {bot_name}!</b>\n\n"
            f"• Этот бот помогает управлять группами\n"
            f"• Анти-спам, верификация, анти-ссылки и другое\n"
            f"• Добавьте меня в вашу группу и дайте права админа\n\n"

            f"👑 <b>1 357 413</b> monthly users"
        )

        await callback.message.edit_text(
            text,
            parse_mode='HTML',
            reply_markup=get_grouphelp_keyboard(bot_username, group_link, channel_link, support_link)
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
