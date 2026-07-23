"""
╔══════════════════════════════════════════════════════════════╗
║           ADMIN HANDLER - aiogram 2.x                        ║
║           /panel, /broadcast, /stats, /warn, /unwarn         ║
║           /ban, /unban, multi-language support               ║
╚══════════════════════════════════════════════════════════════╝
"""

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import db
from config import OWNER_ID, WARN_LIMIT
from utils.keyboards import (
    get_main_menu_keyboard, get_security_keyboard,
    get_language_keyboard, get_broadcast_confirm_keyboard,
    get_stats_keyboard, get_back_keyboard,
    get_security_category_keyboard, get_users_category_keyboard,
    get_management_category_keyboard, get_extra_settings_keyboard,
    get_tools_keyboard,
)
from utils.language import get_text
from utils.helpers import Logger, is_valid_user_id, log_to_channel
from utils.security import rate_limiter, InputValidator, SecurityLogger


# FSM States
class Broadcast(StatesGroup):
    MESSAGE = State()
    CONFIRM = State()

class Admin(StatesGroup):
    ADD_ID = State()
    REMOVE_ID = State()

class BotLinks(StatesGroup):
    WAITING_GROUP_LINK = State()
    WAITING_CHANNEL_LINK = State()
    WAITING_SUPPORT_LINK = State()

class WordFilterState(StatesGroup):
    WAITING_WORD = State()

class BlocklistState(StatesGroup):
    WAITING_USER_ID = State()
    WAITING_REASON = State()

class RulesState(StatesGroup):
    WAITING_TEXT = State()

class LogChannelState(StatesGroup):
    WAITING_CHANNEL_ID = State()

class AutoReplyState(StatesGroup):
    WAITING_KEYWORD = State()
    WAITING_REPLY = State()


def router(dp: Dispatcher):

    # ============================================================
    # ADMIN PANEL (/panel)
    # ============================================================

    @dp.message_handler(Command("panel"))
    async def cmd_panel(message: types.Message):
        user_id = message.from_user.id

        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            lang = await db.get_user_language(user_id) or 'uz'
            await message.answer(get_text('no_permission', lang))
            return

        lang = await db.get_user_language(user_id) or 'uz'
        stats = await db.get_statistics()

        text = get_text('panel_info', lang,
                        total=stats['total_users'],
                        active=stats['active_users'],
                        pending=stats['pending_users'],
                        banned=stats['banned_users'],
                        admins=stats['total_admins'],
                        today=stats['today_joined'])

        await message.answer(
            text,
            parse_mode='HTML',
            reply_markup=get_main_menu_keyboard(lang, show_bot_settings=(user_id == OWNER_ID))
        )

    # ============================================================
    # SECURITY SUBMENU
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "security")
    async def show_security(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'

            verification = await db.get_bool_setting('verification_enabled')
            photo = await db.get_bool_setting('ask_photo_enabled')
            phone = await db.get_bool_setting('ask_phone_enabled')
            antilink = await db.get_bool_setting('antilink_enabled')
            antibot = await db.get_bool_setting('antibot_enabled')
            antiswear = await db.get_bool_setting('antiswear_enabled')

            await callback.message.edit_text(
                get_text('security', lang),
                parse_mode='HTML',
                reply_markup=get_security_keyboard(verification, photo, phone, antilink, antibot, antiswear, lang)
            )
            await callback.answer()
        except Exception as e:
            Logger.error(f"Security menu error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    # ============================================================
    # SETTINGS
    # ============================================================

    # ============================================================
    # SECURITY CATEGORY (sec_main)
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "sec_main")
    async def show_security_category(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'

            settings = {}
            for key in ['antiflood','antispam','antiporn','captcha','nightmode','wordfilter','media_restrict','invite_restrict']:
                settings[key] = await db.get_bool_setting(f'{key}_enabled')

            await callback.message.edit_text(
                get_text('security_category_title', lang),
                parse_mode='HTML',
                reply_markup=get_security_category_keyboard(settings, lang)
            )
            await callback.answer()
        except Exception as e:
            Logger.error(f"Security category error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    # ============================================================
    # USERS CATEGORY (users_main)
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "users_main")
    async def show_users_category(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'

            settings = {
                'userinfo': await db.get_bool_setting('userinfo_enabled'),
                'namehistory': await db.get_bool_setting('namehistory_enabled'),
                'user_ranking': await db.get_bool_setting('user_ranking_enabled'),
                'user_search': await db.get_bool_setting('user_search_enabled'),
            }

            await callback.message.edit_text(
                get_text('users_category_title', lang),
                parse_mode='HTML',
                reply_markup=get_users_category_keyboard(settings, lang)
            )
            await callback.answer()
        except Exception as e:
            Logger.error(f"Users category error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    # ============================================================
    # MANAGEMENT CATEGORY (mgmt_main)
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "mgmt_main")
    async def show_management_category(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'

            settings = {}
            for key in ['welcome_custom','rules','autoreply','scheduled','polls','backup','log_channel','blocklist']:
                settings[key] = await db.get_bool_setting(f'{key}_enabled')

            await callback.message.edit_text(
                get_text('management_category_title', lang),
                parse_mode='HTML',
                reply_markup=get_management_category_keyboard(settings, lang)
            )
            await callback.answer()
        except Exception as e:
            Logger.error(f"Management category error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    # ============================================================
    # SETTINGS
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "settings")
    async def show_settings(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'

            await callback.message.edit_text(
                get_text('settings', lang),
                parse_mode='HTML',
                reply_markup=get_back_keyboard()
            )
            await callback.answer()
        except Exception as e:
            Logger.error(f"Settings error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    # ============================================================
    # STATISTICS (callback)
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "statistics")
    async def show_statistics(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'
            stats = await db.get_statistics()

            text = get_text('stats_text', lang,
                            total=stats['total_users'],
                            active=stats['active_users'],
                            pending=stats['pending_users'],
                            banned=stats['banned_users'],
                            admins=stats['total_admins'],
                            today=stats['today_joined'])

            await callback.message.edit_text(
                text,
                parse_mode='HTML',
                reply_markup=get_stats_keyboard()
            )
            await callback.answer()
        except Exception as e:
            Logger.error(f"Statistics error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    @dp.callback_query_handler(lambda c: c.data == "stats_refresh")
    async def refresh_stats(callback: types.CallbackQuery):
        await show_statistics(callback)

    # ============================================================
    # ADMINS SUBMENU
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "admins_main")
    async def show_admins_menu(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text('btn_admin_list', lang), callback_data="admin_list")],
                [InlineKeyboardButton(text=get_text('btn_add_admin', lang), callback_data="admin_add")],
                [InlineKeyboardButton(text=get_text('btn_remove_admin', lang), callback_data="admin_remove")],
                [InlineKeyboardButton(text=get_text('btn_back', lang), callback_data="panel_back")],
            ])

            await callback.message.edit_text(
                get_text('admins', lang),
                parse_mode='HTML',
                reply_markup=keyboard
            )
            await callback.answer()
        except Exception as e:
            Logger.error(f"Admins menu error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    # ============================================================
    # STATS MAIN
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "stats_main")
    async def show_stats_main(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'
            stats = await db.get_statistics()

            text = get_text('stats_text', lang,
                            total=stats['total_users'],
                            active=stats['active_users'],
                            pending=stats['pending_users'],
                            banned=stats['banned_users'],
                            admins=stats['total_admins'],
                            today=stats['today_joined'])

            await callback.message.edit_text(
                text,
                parse_mode='HTML',
                reply_markup=get_stats_keyboard()
            )
            await callback.answer()
        except Exception as e:
            Logger.error(f"Stats main error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    # ============================================================
    # LANGUAGE SELECTION
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "lang")
    async def show_language(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'

            await callback.message.edit_text(
                get_text('choose_language', lang),
                parse_mode='HTML',
                reply_markup=get_language_keyboard(lang)
            )
            await callback.answer()
        except Exception as e:
            Logger.error(f"Language menu error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    @dp.callback_query_handler(lambda c: c.data.startswith("lang:"))
    async def set_language(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            new_lang = callback.data.split(":")[1]

            if new_lang not in ('uz', 'ru', 'en'):
                await callback.answer("❌ Noto'g'ri til!", show_alert=True)
                return

            await db.set_user_language(user_id, new_lang)

            lang_names = {'uz': "O'zbekcha", 'ru': 'Русский', 'en': 'English'}
            lang_name = lang_names.get(new_lang, new_lang)

            await callback.message.edit_text(
                get_text('language_changed', new_lang, lang=lang_name),
                parse_mode='HTML',
                reply_markup=get_language_keyboard(new_lang)
            )
            await callback.answer()
        except Exception as e:
            Logger.error(f"Language set error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    # ============================================================
    # TOGGLE SETTINGS
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data.startswith("toggle:"))
    async def toggle_setting(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            if not (await db.is_admin(user_id) or user_id == OWNER_ID):
                await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
                return
            lang = await db.get_user_language(user_id) or 'uz'
            setting = callback.data.split(":")[1]
            setting_key = f"{setting}_enabled"

            new_status = await db.toggle_setting(setting_key)

            # Show main menu after toggle
            try:
                stats = await db.get_statistics()
                text = get_text('panel_info', lang,
                                total=stats['total_users'],
                                active=stats['active_users'],
                                pending=stats['pending_users'],
                                banned=stats['banned_users'],
                                admins=stats['total_admins'],
                                today=stats['today_joined'])
                await callback.message.edit_text(
                    text,
                    parse_mode='HTML',
                    reply_markup=get_main_menu_keyboard(lang, show_bot_settings=(user_id == OWNER_ID))
                )
            except Exception:
                pass

            status_text = get_text('toggle_on', lang) if new_status else get_text('toggle_off', lang)
            await callback.answer(f"{setting.title()} {status_text}")

        except Exception as e:
            Logger.error(f"Toggle error: {e}")
            await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)

    # ============================================================
    # BACK TO PANEL
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "panel_back")
    async def back_to_panel(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'
            stats = await db.get_statistics()

            text = get_text('panel_info', lang,
                            total=stats['total_users'],
                            active=stats['active_users'],
                            pending=stats['pending_users'],
                            banned=stats['banned_users'],
                            admins=stats['total_admins'],
                            today=stats['today_joined'])

            await callback.message.edit_text(
                text,
                parse_mode='HTML',
                reply_markup=get_main_menu_keyboard(lang, show_bot_settings=(user_id == OWNER_ID))
            )
        except Exception:
            pass
        await callback.answer()

    # ============================================================
    # BOT SETTINGS (owner only)
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "bot_settings")
    async def show_bot_settings(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        if user_id != OWNER_ID:
            await callback.answer("❌ Faqat egasi!", show_alert=True)
            return
        lang = await db.get_user_language(user_id) or 'uz'
        links = await db.get_bot_links()

        text = (
            f"⚙️ <b>Bot sozlamalari</b>\n\n"
            f"👥 Guruh: {links['group_link'] or '❌ Sozlanmagan'}\n"
            f"📢 Kanal: {links['channel_link'] or '❌ Sozlanmagan'}\n"
            f"🆘 Support: {links['support_link'] or '❌ Sozlanmagan'}\n\n"
            f"Quyidagi tugmalar orqali linklarni o'zgartiring:"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 Guruh linki", callback_data="bot_set:group")],
            [InlineKeyboardButton(text="📢 Kanal linki", callback_data="bot_set:channel")],
            [InlineKeyboardButton(text="🆘 Support linki", callback_data="bot_set:support")],
            [InlineKeyboardButton(text=get_text('btn_back', lang), callback_data="panel_back")],
        ])
        await callback.message.edit_text(text, parse_mode='HTML', reply_markup=keyboard)
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data.startswith("bot_set:"))
    async def start_set_link(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        if user_id != OWNER_ID:
            await callback.answer("❌", show_alert=True)
            return
        link_type = callback.data.split(":")[1]
        lang = await db.get_user_language(user_id) or 'uz'

        names = {'group': '👥 Guruh', 'channel': '📢 Kanal', 'support': '🆘 Support'}
        name = names.get(link_type, link_type)
        target_states = {'group': BotLinks.WAITING_GROUP_LINK, 'channel': BotLinks.WAITING_CHANNEL_LINK, 'support': BotLinks.WAITING_SUPPORT_LINK}
        target_state = target_states.get(link_type)
        if not target_state:
            await callback.answer()
            return

        storage = dp.storage
        fsm = FSMContext(storage=storage, chat=user_id, user=user_id)
        await fsm.set_state(target_state)
        await fsm.update_data(link_type=link_type)

        await callback.message.edit_text(
            f"{name} linkini yuboring.\nMisol: <code>https://t.me/your_group</code>\n\n/cancel - Bekor qilish",
            parse_mode='HTML'
        )
        await callback.answer()

    @dp.message_handler(state=BotLinks.WAITING_GROUP_LINK)
    async def set_group_link(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        if user_id != OWNER_ID:
            await state.finish()
            return
        text = message.text.strip()
        if text.lower() == '/cancel':
            await state.finish()
            await message.answer("❌ Bekor qilindi.")
            return
        await db.set_setting('group_link', text)
        await state.finish()
        await message.answer("✅ Guruh linki saqlandi!\n\n/panel orqali tekshiring.")

    @dp.message_handler(state=BotLinks.WAITING_CHANNEL_LINK)
    async def set_channel_link(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        if user_id != OWNER_ID:
            await state.finish()
            return
        text = message.text.strip()
        if text.lower() == '/cancel':
            await state.finish()
            await message.answer("❌ Bekor qilindi.")
            return
        await db.set_setting('channel_link', text)
        await state.finish()
        await message.answer("✅ Kanal linki saqlandi!\n\n/panel orqali tekshiring.")

    @dp.message_handler(state=BotLinks.WAITING_SUPPORT_LINK)
    async def set_support_link(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        if user_id != OWNER_ID:
            await state.finish()
            return
        text = message.text.strip()
        if text.lower() == '/cancel':
            await state.finish()
            await message.answer("❌ Bekor qilindi.")
            return
        await db.set_setting('support_link', text)
        await state.finish()
        await message.answer("✅ Support linki saqlandi!\n\n/panel orqali tekshiring.")

    # ============================================================
    # /stats COMMAND
    # ============================================================

    @dp.message_handler(Command("stats"))
    async def cmd_stats(message: types.Message):
        user_id = message.from_user.id

        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return

        lang = await db.get_user_language(user_id) or 'uz'

        try:
            stats = await db.get_statistics()

            text = get_text('stats_text', lang,
                            total=stats['total_users'],
                            active=stats['active_users'],
                            pending=stats['pending_users'],
                            banned=stats['banned_users'],
                            admins=stats['total_admins'],
                            today=stats['today_joined'])

            await message.answer(text, parse_mode='HTML')
        except Exception as e:
            Logger.error(f"Stats command error: {e}")

    # ============================================================
    # BROADCAST
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "broadcast")
    async def start_broadcast(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        lang = await db.get_user_language(user_id) or 'uz'

        await Broadcast.MESSAGE.set()

        await callback.message.edit_text(
            get_text('broadcast_text', lang),
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
        await callback.answer()

    @dp.message_handler(state=Broadcast.MESSAGE)
    async def process_broadcast_message(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        lang = await db.get_user_language(user_id) or 'uz'

        if message.text == "/cancel":
            await state.finish()
            await message.answer(get_text('broadcast_cancelled', lang))
            return

        await state.update_data(
            text=message.text or "",
            photo=message.photo[-1].file_id if message.photo else None,
            caption=message.caption
        )

        await Broadcast.CONFIRM.set()

        preview = "📢 <b>Broadcast (preview):</b>\n\n"

        if message.photo:
            preview += message.caption or "[Image]"
        else:
            preview += message.text

        preview += "\n\n✅ Send?"

        await message.answer(
            preview,
            parse_mode='HTML',
            reply_markup=get_broadcast_confirm_keyboard()
        )

    @dp.callback_query_handler(lambda c: c.data == "broadcast_send", state=Broadcast.CONFIRM)
    async def send_broadcast(callback: types.CallbackQuery, state: FSMContext):
        bot = dp.bot
        user_id = callback.from_user.id
        lang = await db.get_user_language(user_id) or 'uz'

        try:
            data = await state.get_data()
            text = data.get('text', '')
            photo = data.get('photo')
            caption = data.get('caption')

            users = await db.get_all_users(status='active')

            sent_count = 0
            failed_count = 0

            await callback.answer("📤 Yuborilmoqda...", show_alert=False)

            for user in users:
                try:
                    if photo:
                        await bot.send_photo(
                            chat_id=user['user_id'],
                            photo=photo,
                            caption=caption,
                            parse_mode='HTML'
                        )
                    else:
                        await bot.send_message(
                            chat_id=user['user_id'],
                            text=text,
                            parse_mode='HTML'
                        )
                    sent_count += 1
                except Exception as e:
                    failed_count += 1
                    Logger.error(f"Broadcast failed to {user['user_id']}: {e}")

            await callback.message.edit_text(
                get_text('broadcast_sent', lang, count=sent_count, failed=failed_count),
                parse_mode='HTML'
            )

            await state.finish()
            Logger.success(f"Broadcast sent to {sent_count} users")

        except Exception as e:
            Logger.error(f"Broadcast error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    @dp.callback_query_handler(lambda c: c.data == "broadcast_cancel", state=Broadcast.CONFIRM)
    async def cancel_broadcast(callback: types.CallbackQuery, state: FSMContext):
        user_id = callback.from_user.id
        lang = await db.get_user_language(user_id) or 'uz'

        await state.finish()
        await callback.message.edit_text(get_text('broadcast_cancelled', lang))
        await callback.answer()

    # ============================================================
    # ADMIN LIST
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "admin_list")
    async def show_admins(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'
            admins = await db.get_all_admins()

            if not admins:
                list_text = get_text('admin_list', lang, list=get_text('user_not_found', lang))
            else:
                lines = []
                for i, admin in enumerate(admins, 1):
                    owner_mark = "👑 " if admin['is_owner'] else ""
                    name = admin['name'] or f"ID: {admin['user_id']}"
                    lines.append(f"{i}. {owner_mark}{name} (ID: <code>{admin['user_id']}</code>)")
                list_text = get_text('admin_list', lang, list='\n'.join(lines))

            await callback.message.edit_text(
                list_text,
                parse_mode='HTML',
                reply_markup=get_back_keyboard()
            )
            await callback.answer()
        except Exception as e:
            Logger.error(f"Admin list error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    # ============================================================
    # ADMIN ADD
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "admin_add")
    async def start_add_admin(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        lang = await db.get_user_language(user_id) or 'uz'

        if user_id != OWNER_ID:
            await callback.answer(get_text('only_owner', lang), show_alert=True)
            return

        await Admin.ADD_ID.set()

        await callback.message.edit_text(
            get_text('add_admin', lang),
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
        await callback.answer()

    @dp.message_handler(state=Admin.ADD_ID)
    async def process_add_admin(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        lang = await db.get_user_language(user_id) or 'uz'

        if message.text == "/cancel":
            await state.finish()
            await message.answer(get_text('broadcast_cancelled', lang))
            return

        # Security: Validate input
        if not is_valid_user_id(message.text):
            await message.answer(get_text('admin_not_found', lang))
            SecurityLogger.log_security_event('INVALID_ADMIN_ID', user_id, message.text)
            return

        new_admin_id = int(message.text)

        # Security: Additional validation
        if not InputValidator.validate_user_id(new_admin_id):
            await message.answer(get_text('admin_not_found', lang))
            SecurityLogger.log_security_event('INVALID_ADMIN_ID_VALIDATION', user_id, str(new_admin_id))
            return

        if new_admin_id == message.from_user.id:
            await message.answer(get_text('admin_not_found', lang))
            return

        success = await db.add_admin(
            user_id=new_admin_id,
            added_by=message.from_user.id
        )

        if success:
            await message.answer(
                get_text('admin_added', lang, id=new_admin_id),
                parse_mode='HTML'
            )
            Logger.success(f"Admin {new_admin_id} added by {message.from_user.id}")
            SecurityLogger.log_security_event('ADMIN_ADDED', message.from_user.id, f'New admin: {new_admin_id}')
        else:
            await message.answer(get_text('admin_not_found', lang))

        await state.finish()

    # ============================================================
    # ADMIN REMOVE
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "admin_remove")
    async def start_remove_admin(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        lang = await db.get_user_language(user_id) or 'uz'

        if user_id != OWNER_ID:
            await callback.answer(get_text('only_owner', lang), show_alert=True)
            return

        await Admin.REMOVE_ID.set()

        admins = await db.get_all_admins()
        lines = []
        for admin in admins:
            if not admin['is_owner']:
                name = admin['name'] or "Noma'lum"
                lines.append(f"• {name} - <code>{admin['user_id']}</code>")

        await callback.message.edit_text(
            get_text('remove_admin', lang, list='\n'.join(lines)),
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
        await callback.answer()

    @dp.message_handler(state=Admin.REMOVE_ID)
    async def process_remove_admin(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        lang = await db.get_user_language(user_id) or 'uz'

        if message.text == "/cancel":
            await state.finish()
            await message.answer(get_text('broadcast_cancelled', lang))
            return

        if not is_valid_user_id(message.text):
            await message.answer(get_text('admin_not_found', lang))
            return

        remove_id = int(message.text)

        if remove_id == OWNER_ID:
            await message.answer(get_text('admin_not_found', lang))
            return

        if remove_id == message.from_user.id:
            await message.answer(get_text('admin_not_found', lang))
            return

        success = await db.remove_admin(remove_id)

        if success:
            await message.answer(
                get_text('admin_removed', lang, id=remove_id),
                parse_mode='HTML'
            )
            Logger.success(f"Admin {remove_id} removed by {message.from_user.id}")
        else:
            await message.answer(get_text('admin_not_found', lang))

        await state.finish()

    # ============================================================
    # /warn COMMAND
    # ============================================================

    @dp.message_handler(Command("warn"))
    async def cmd_warn(message: types.Message):
        bot = dp.bot
        user_id = message.from_user.id

        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return

        lang = await db.get_user_language(user_id) or 'uz'

        if not message.reply_to_message:
            await message.answer(get_text('reply_required', lang))
            return

        target = message.reply_to_message.from_user

        if await db.is_admin(target.id):
            await message.answer(get_text('no_permission', lang))
            return

        warn_count = await db.add_warn(
            user_id=target.id,
            group_id=message.chat.id,
            reason="Admin tomonidan ogohlantirish",
            warned_by=user_id
        )

        await message.answer(
            f"⚠️ <b>{target.first_name}</b> ogohlantirildi!\n"
            f"Jami: {warn_count}/{WARN_LIMIT}",
            parse_mode='HTML'
        )

        await log_to_channel(dp.bot, "⚠️ Ogohlantirish",
                             user_id=target.id, admin_id=user_id,
                             details=f"{warn_count}/{WARN_LIMIT}")

        if warn_count >= WARN_LIMIT:
            try:
                await bot.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=target.id,
                    permissions={
                        'can_send_messages': False,
                        'can_send_media_messages': False,
                        'can_send_polls': False,
                        'can_send_other_messages': False,
                        'can_add_web_page_previews': False,
                        'can_change_info': False,
                        'can_invite_users': False,
                        'can_pin_messages': False
                    }
                )
                await message.answer(
                    f"🔇 <b>{target.first_name}</b> 24 soatga mutga qo'yildi!",
                    parse_mode='HTML'
                )
            except Exception as e:
                Logger.error(f"Mute error: {e}")

    # ============================================================
    # /unwarn COMMAND
    # ============================================================

    @dp.message_handler(Command("unwarn"))
    async def cmd_unwarn(message: types.Message):
        user_id = message.from_user.id

        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return

        lang = await db.get_user_language(user_id) or 'uz'

        if not message.reply_to_message:
            await message.answer(get_text('reply_required', lang))
            return

        target = message.reply_to_message.from_user

        await db.clear_warns(target.id)

        await message.answer(
            f"✅ <b>{target.first_name}</b> ning ogohlantirishlari tozalandi!",
            parse_mode='HTML'
        )

    # ============================================================
    # /ban COMMAND
    # ============================================================

    @dp.message_handler(Command("ban"))
    async def cmd_ban(message: types.Message):
        bot = dp.bot
        user_id = message.from_user.id

        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return

        lang = await db.get_user_language(user_id) or 'uz'

        if not message.reply_to_message:
            await message.answer(get_text('reply_required', lang))
            return

        target = message.reply_to_message.from_user

        try:
            await bot.ban_chat_member(message.chat.id, target.id)
            await db.update_user_status(target.id, 'banned')
            await message.answer(
                f"🚫 <b>{target.first_name}</b> guruhdan bloklandi!",
                parse_mode='HTML'
            )
            await log_to_channel(dp.bot, "🚫 Ban", user_id=target.id, admin_id=user_id)
            Logger.success(f"User {target.id} banned by {user_id}")
        except Exception as e:
            Logger.error(f"Ban error: {e}")
            await message.answer("❌ Bloklashda xatolik!")

    # ============================================================
    # /unban COMMAND
    # ============================================================

    @dp.message_handler(Command("unban"))
    async def cmd_unban(message: types.Message):
        bot = dp.bot
        user_id = message.from_user.id

        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return

        lang = await db.get_user_language(user_id) or 'uz'

        if message.reply_to_message:
            target_id = message.reply_to_message.from_user.id
        else:
            args = message.text.split()
            if len(args) < 2:
                await message.answer("❌ ID raqam kiriting: /unban 123456789")
                return
            target_id = int(args[1])

        try:
            await bot.unban_chat_member(message.chat.id, target_id)
            await db.update_user_status(target_id, 'active')
            await message.answer(
                f"✅ Foydalanuvchi (<code>{target_id}</code>) blokdan chiqarildi!",
                parse_mode='HTML'
            )
            Logger.success(f"User {target_id} unbanned by {user_id}")
        except Exception as e:
            Logger.error(f"Unban error: {e}")
            await message.answer("❌ Xatolik!")

    # ============================================================
    # EXTRA SETTINGS SUBMENU
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "extra_main")
    async def show_extra_settings(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'
            settings = {}
            for key in ['anti_raid','new_member_restrict','service_msg_delete','bio_filter']:
                settings[key] = await db.get_bool_setting(f'{key}_enabled')
            await callback.message.edit_text(
                "⚙️ <b>Qo'shimcha sozlamalar</b>\n\nYoqish/o'chirish:",
                parse_mode='HTML',
                reply_markup=get_extra_settings_keyboard(settings, lang))
            await callback.answer()
        except Exception as e:
            Logger.error(f"Extra settings error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    # ============================================================
    # TOOLS SUBMENU
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "tools_main")
    async def show_tools(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            lang = await db.get_user_language(user_id) or 'uz'
            await callback.message.edit_text(
                "🔧 <b>Asboblar</b>\n\nKerakli bo'limni tanlang:",
                parse_mode='HTML',
                reply_markup=get_tools_keyboard(lang))
            await callback.answer()
        except Exception as e:
            Logger.error(f"Tools error: {e}")
            await callback.answer("❌ Xatolik!", show_alert=True)

    # ============================================================
    # TOOL HANDLERS
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "tool:wordfilter")
    async def tool_wordfilter(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        lang = await db.get_user_language(user_id) or 'uz'
        words = await db.get_filtered_words()
        word_list = "\n".join([f"• {w}" for w in words]) if words else "Hozircha yo'q"
        text = f"🔤 <b>So'z filtri</b>\n\nTaqlangan so'zlar:\n{word_list}\n\n/addword <b>so'z</b> — qo'shish\n/delword <b>so'z</b> — o'chirish"
        await callback.message.edit_text(text, parse_mode='HTML', reply_markup=get_back_keyboard())
        await callback.answer()

    @dp.message_handler(Command("addword"))
    async def cmd_addword(message: types.Message):
        user_id = message.from_user.id
        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return
        lang = await db.get_user_language(user_id) or 'uz'
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("❌ So'z kiriting: /addword so'z")
            return
        word = args[1].strip().lower()
        await db.add_filtered_word(word, user_id)
        await message.answer(f"✅ <b>{word}</b> filtrga qo'shildi!", parse_mode='HTML')

    @dp.message_handler(Command("delword"))
    async def cmd_delword(message: types.Message):
        user_id = message.from_user.id
        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("❌ So'z kiriting: /delword so'z")
            return
        word = args[1].strip().lower()
        await db.remove_filtered_word(word)
        await message.answer(f"✅ <b>{word}</b> filtrdan o'chirildi!", parse_mode='HTML')

    # ============================================================
    # BLOCKLIST HANDLERS
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "tool:blocklist")
    async def tool_blocklist(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        lang = await db.get_user_language(user_id) or 'uz'
        blocked = await db.get_blocklist()
        if blocked:
            lines = [f"• {b['user_id']} — {b['reason'] or 'Sababsiz'}" for b in blocked[:20]]
            text = f"🚫 <b>Qora ro'yxat</b>\n\n" + "\n".join(lines)
        else:
            text = "🚫 <b>Qora ro'yxat</b>\n\nBo'sh"
        text += "\n\n/block ID — qo'shish\n/unblock ID — o'chirish"
        await callback.message.edit_text(text, parse_mode='HTML', reply_markup=get_back_keyboard())
        await callback.answer()

    @dp.message_handler(Command("block"))
    async def cmd_block(message: types.Message):
        user_id = message.from_user.id
        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return
        args = message.text.split()
        if len(args) < 2:
            await message.answer("❌ ID kiriting: /block 123456789")
            return
        try:
            target_id = int(args[1])
            reason = ' '.join(args[2:]) if len(args) > 2 else None
            await db.add_to_blocklist(target_id, reason, user_id)
            await message.answer(f"✅ <code>{target_id}</code> qora ro'yxatga qo'shildi!", parse_mode='HTML')
        except ValueError:
            await message.answer("❌ Noto'g'ri ID!")

    @dp.message_handler(Command("unblock"))
    async def cmd_unblock(message: types.Message):
        user_id = message.from_user.id
        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return
        args = message.text.split()
        if len(args) < 2:
            await message.answer("❌ ID kiriting: /unblock 123456789")
            return
        try:
            target_id = int(args[1])
            await db.remove_from_blocklist(target_id)
            await message.answer(f"✅ <code>{target_id}</code> qora ro'yxatdan o'chirildi!", parse_mode='HTML')
        except ValueError:
            await message.answer("❌ Noto'g'ri ID!")

    # ============================================================
    # RULES HANDLERS
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "tool:rules")
    async def tool_rules(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        lang = await db.get_user_language(user_id) or 'uz'
        current = await db.get_rules(callback.message.chat.id) if callback.message.chat.type in ['group', 'supergroup'] else ''
        txt = current if current else "Hali o'rnatilmagan"
        text = f"📋 <b>Qoidalar</b>\n\n{txt}\n\n/setrules — yangi qoidalar kiritish"
        await callback.message.edit_text(text, parse_mode='HTML', reply_markup=get_back_keyboard())
        await callback.answer()

    @dp.message_handler(Command("setrules"))
    async def cmd_setrules(message: types.Message):
        user_id = message.from_user.id
        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return
        if message.chat.type not in ['group', 'supergroup']:
            await message.answer("❌ Bu buyruq guruhda ishlaydi!")
            return
        storage = dp.storage
        fsm = FSMContext(storage=storage, chat=user_id, user=user_id)
        await fsm.set_state(RulesState.WAITING_TEXT)
        await message.answer("📋 Guruh qoidalarini yuboring (HTML formatda bo'lishi mumkin):\n\n/cancel — bekor qilish")

    @dp.message_handler(state=RulesState.WAITING_TEXT)
    async def process_rules(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            await state.finish()
            return
        if message.text == '/cancel':
            await state.finish()
            await message.answer("❌ Bekor qilindi.")
            return
        await db.set_rules(message.chat.id, message.text)
        await state.finish()
        await message.answer("✅ Qoidalar saqlandi!\n/panel")

    # ============================================================
    # LOG CHANNEL HANDLERS
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "tool:log_channel")
    async def tool_log_channel(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        if user_id != OWNER_ID:
            await callback.answer("❌ Faqat egasi!", show_alert=True)
            return
        lang = await db.get_user_language(user_id) or 'uz'
        current = await db.get_setting('log_channel_id', '')
        text = f"📝 <b>Log kanal</b>\n\nJoriy: {current or '❌ Sozlanmagan'}\n\n/setlog <b>ID</b> — o'rnatish\n/dellog — o'chirish"
        await callback.message.edit_text(text, parse_mode='HTML', reply_markup=get_back_keyboard())
        await callback.answer()

    @dp.message_handler(Command("setlog"))
    async def cmd_setlog(message: types.Message):
        user_id = message.from_user.id
        if user_id != OWNER_ID:
            return
        args = message.text.split()
        if len(args) < 2:
            await message.answer("❌ Kanal ID kiriting: /setlog -1001234567890")
            return
        try:
            channel_id = int(args[1])
            await db.set_setting('log_channel_id', str(channel_id))
            await message.answer(f"✅ Log kanali o'rnatildi: <code>{channel_id}</code>", parse_mode='HTML')
        except ValueError:
            await message.answer("❌ Noto'g'ri ID!")

    @dp.message_handler(Command("dellog"))
    async def cmd_dellog(message: types.Message):
        user_id = message.from_user.id
        if user_id != OWNER_ID:
            return
        await db.set_setting('log_channel_id', '')
        await message.answer("✅ Log kanali o'chirildi!")

    # ============================================================
    # EXPORT / IMPORT SETTINGS
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "tool:export")
    async def tool_export(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        if user_id != OWNER_ID:
            await callback.answer("❌ Faqat egasi!", show_alert=True)
            return
        settings = await db.export_settings()
        import json
        data = json.dumps(settings, indent=2, ensure_ascii=False)
        if len(data) > 4000:
            with open('settings_export.json', 'w', encoding='utf-8') as f:
                f.write(data)
            with open('settings_export.json', 'rb') as f:
                await callback.message.answer_document(
                    types.InputFile(f, filename='settings_export.json'),
                    caption="💾 Sozlamalar eksport qilindi")
        else:
            await callback.message.answer(f"💾 <b>Sozlamalar</b>:\n\n<code>{data}</code>", parse_mode='HTML')
        await callback.answer()

    @dp.message_handler(Command("import"))
    async def cmd_import(message: types.Message):
        user_id = message.from_user.id
        if user_id != OWNER_ID:
            return
        import json
        if not message.reply_to_message or not message.reply_to_message.document:
            await message.answer("❌ JSON faylni reply qilib /import yuboring!")
            return
        try:
            file = await dp.bot.download_file(
                (await dp.bot.get_file(message.reply_to_message.document.file_id)).file_path)
            content = file.read().decode('utf-8')
            settings = json.loads(content)
            count = await db.import_settings(settings)
            await message.answer(f"✅ {count} ta sozlama import qilindi!")
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")

    # ============================================================
    # AUTO-REPLY HANDLERS
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data == "tool:autoreply")
    async def tool_autoreply(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        lang = await db.get_user_language(user_id) or 'uz'
        replies = await db.get_all_autoreplies()
        if replies:
            lines = [f"• {r['keyword']} → {r['reply'][:30]}..." for r in replies[:20]]
            text = "🤖 <b>Avto-javoblar</b>\n\n" + "\n".join(lines)
        else:
            text = "🤖 <b>Avto-javoblar</b>\n\nHozircha yo'q"
        text += "\n\n/autoreply <b>kalit</b> | <b>javob</b> — qo'shish\n/delauto <b>kalit</b> — o'chirish"
        await callback.message.edit_text(text, parse_mode='HTML', reply_markup=get_back_keyboard())
        await callback.answer()

    @dp.message_handler(Command("autoreply"))
    async def cmd_autoreply(message: types.Message):
        user_id = message.from_user.id
        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return
        args = message.text.split(maxsplit=1)
        if len(args) < 2 or '|' not in args[1]:
            await message.answer("❌ Format: /autoreply kalit_so'z | javob matni")
            return
        keyword, reply = args[1].split('|', 1)
        keyword = keyword.strip().lower()
        reply = reply.strip()
        chat_id = message.chat.id if message.chat.type in ['group', 'supergroup'] else None
        await db.add_autoreply(keyword, reply, chat_id)
        await message.answer(f"✅ Avto-javob qo'shildi: <b>{keyword}</b>", parse_mode='HTML')

    @dp.message_handler(Command("delauto"))
    async def cmd_delauto(message: types.Message):
        user_id = message.from_user.id
        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("❌ Kalit so'z kiriting: /delauto kalit")
            return
        keyword = args[1].strip().lower()
        chat_id = message.chat.id if message.chat.type in ['group', 'supergroup'] else None
        await db.remove_autoreply(keyword, chat_id)
        await message.answer(f"✅ Avto-javob o'chirildi: <b>{keyword}</b>", parse_mode='HTML')
