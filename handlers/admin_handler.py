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
    get_management_category_keyboard,
)
from utils.language import get_text
from utils.helpers import Logger, is_valid_user_id


# FSM States
class Broadcast(StatesGroup):
    MESSAGE = State()
    CONFIRM = State()

class Admin(StatesGroup):
    ADD_ID = State()
    REMOVE_ID = State()


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
            reply_markup=get_main_menu_keyboard(lang)
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
                    reply_markup=get_main_menu_keyboard(lang)
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
                reply_markup=get_main_menu_keyboard(lang)
            )
        except Exception:
            pass
        await callback.answer()

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

        if not is_valid_user_id(message.text):
            await message.answer(get_text('admin_not_found', lang))
            return

        new_admin_id = int(message.text)

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
