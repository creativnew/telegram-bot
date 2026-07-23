from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import db
from config import OWNER_ID, ADMIN_GROUP_ID, MAIN_GROUP_ID
from utils.keyboards import (
    get_contact_keyboard, get_cancel_keyboard,
    get_remove_keyboard, get_admin_approve_keyboard,
    get_approved_keyboard, get_rejected_keyboard
)
from utils.language import get_text
from utils.helpers import format_user_mention, Logger
from datetime import datetime


class Verification(StatesGroup):
    NAME = State()
    PHONE = State()
    PHOTO = State()


async def _notify_admins(bot, request_id, user_id, full_name, phone, photo_id, admin_text):
    try:
        targets = [OWNER_ID]
        if ADMIN_GROUP_ID:
            targets.append(ADMIN_GROUP_ID)
        admins = await db.get_all_admins()
        for a in admins:
            if a['user_id'] not in targets:
                targets.append(a['user_id'])

        for target_id in targets:
            try:
                kb = get_admin_approve_keyboard(request_id, user_id)
                if photo_id:
                    await bot.send_photo(
                        chat_id=target_id, photo=photo_id,
                        caption=admin_text, parse_mode='HTML', reply_markup=kb
                    )
                else:
                    await bot.send_message(
                        chat_id=target_id, text=admin_text,
                        parse_mode='HTML', reply_markup=kb
                    )
            except Exception:
                pass
    except Exception as e:
        Logger.error(f"Admin notify error: {e}")


def router(dp: Dispatcher):

    @dp.chat_join_request_handler()
    async def on_chat_join_request(join_request: types.ChatJoinRequest):
        user = join_request.from_user
        chat = join_request.chat
        bot = dp.bot

        verification_enabled = await db.get_bool_setting('verification_enabled')
        if not verification_enabled:
            try:
                await bot.approve_chat_join_request(chat.id, user.id)
                Logger.info(f"Auto-approved {user.id}")
            except Exception as e:
                Logger.error(f"Auto-approve error: {e}")
            return

        await db.add_user(
            user_id=user.id, username=user.username,
            first_name=user.first_name, last_name=user.last_name,
            status='pending'
        )
        await db.add_group(chat.id, chat.title)

        try:
            user_lang = await db.get_user_language(user.id)
        except Exception:
            user_lang = 'uz'

        ask_phone = await db.get_bool_setting('ask_phone_enabled')
        ask_photo = await db.get_bool_setting('ask_photo_enabled')

        try:
            await bot.send_message(
                chat_id=user.id,
                text=get_text('welcome', user_lang),
                parse_mode='HTML'
            )
            await bot.send_message(
                chat_id=user.id,
                text=get_text('enter_name', user_lang),
                parse_mode='HTML',
                reply_markup=get_cancel_keyboard()
            )
            await Verification.NAME.set()
        except Exception as e:
            Logger.error(f"Cannot send PM to {user.id}: {e}")
            try:
                await bot.decline_chat_join_request(chat.id, user.id)
            except Exception:
                pass

    @dp.message_handler(state=Verification.NAME)
    async def process_name(message: types.Message, state: FSMContext):
        if not message.text or len(message.text) < 3:
            try:
                lang = await db.get_user_language(message.from_user.id)
            except Exception:
                lang = 'uz'
            await message.answer(get_text('name_short', lang))
            return

        await state.update_data(full_name=message.text.strip())

        try:
            lang = await db.get_user_language(message.from_user.id)
        except Exception:
            lang = 'uz'

        ask_phone = await db.get_bool_setting('ask_phone_enabled')
        ask_photo = await db.get_bool_setting('ask_photo_enabled')

        if ask_phone:
            await Verification.PHONE.set()
            await message.answer(
                get_text('enter_phone', lang),
                parse_mode='HTML',
                reply_markup=get_contact_keyboard()
            )
        elif ask_photo:
            await Verification.PHOTO.set()
            await message.answer(
                get_text('enter_photo', lang),
                parse_mode='HTML',
                reply_markup=get_cancel_keyboard()
            )
        else:
            user = message.from_user
            full_name = message.text.strip()
            await db.add_user(
                user_id=user.id, username=user.username,
                first_name=user.first_name, last_name=user.last_name,
                status='pending'
            )
            request_id = await db.add_verification_request(
                user_id=user.id, group_id=MAIN_GROUP_ID or 0,
                full_name=full_name, phone=None, photo_id=None
            )
            mention = format_user_mention(user.id, user.first_name, user.last_name)
            admin_text = get_text('admin_request', 'uz',
                name=full_name, phone='-', user_id=user.id,
                mention=mention, date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            await _notify_admins(dp.bot, request_id, user.id, full_name, None, None, admin_text)
            await message.answer(
                get_text('verification_complete', lang),
                parse_mode='HTML', reply_markup=get_remove_keyboard())
            await state.finish()

    @dp.message_handler(content_types=types.ContentType.CONTACT, state=Verification.PHONE)
    async def process_phone_contact(message: types.Message, state: FSMContext):
        if not message.contact:
            try:
                lang = await db.get_user_language(message.from_user.id)
            except Exception:
                lang = 'uz'
            await message.answer(get_text('phone_invalid', lang))
            return

        if message.contact.user_id != message.from_user.id:
            try:
                lang = await db.get_user_language(message.from_user.id)
            except Exception:
                lang = 'uz'
            await message.answer(get_text('phone_not_yours', lang))
            return

        phone = message.contact.phone_number
        await state.update_data(phone=phone)

        try:
            lang = await db.get_user_language(message.from_user.id)
        except Exception:
            lang = 'uz'

        ask_photo = await db.get_bool_setting('ask_photo_enabled')
        if ask_photo:
            await Verification.PHOTO.set()
            await message.answer(
                get_text('enter_photo', lang),
                parse_mode='HTML', reply_markup=get_cancel_keyboard())
        else:
            user = message.from_user
            data = await state.get_data()
            full_name = data.get('full_name', "Noma'lum")
            await db.add_user(
                user_id=user.id, username=user.username,
                first_name=user.first_name, last_name=user.last_name,
                phone=phone, status='pending')
            request_id = await db.add_verification_request(
                user_id=user.id, group_id=MAIN_GROUP_ID or 0,
                full_name=full_name, phone=phone, photo_id=None)
            mention = format_user_mention(user.id, user.first_name, user.last_name)
            admin_text = get_text('admin_request', 'uz',
                name=full_name, phone=phone, user_id=user.id,
                mention=mention, date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            await _notify_admins(dp.bot, request_id, user.id, full_name, phone, None, admin_text)
            await message.answer(
                get_text('verification_complete', lang),
                parse_mode='HTML', reply_markup=get_remove_keyboard())
            await state.finish()

    @dp.message_handler(state=Verification.PHONE)
    async def process_phone_text(message: types.Message, state: FSMContext):
        try:
            lang = await db.get_user_language(message.from_user.id)
        except Exception:
            lang = 'uz'
        await message.answer(get_text('phone_invalid', lang))

    @dp.message_handler(content_types=types.ContentType.PHOTO, state=Verification.PHOTO)
    async def process_photo(message: types.Message, state: FSMContext):
        bot = dp.bot
        photo_id = message.photo[-1].file_id
        data = await state.get_data()
        full_name = data.get('full_name', "Noma'lum")
        phone = data.get('phone', "Noma'lum")
        user = message.from_user

        try:
            lang = await db.get_user_language(user.id)
        except Exception:
            lang = 'uz'

        await db.add_user(
            user_id=user.id, username=user.username,
            first_name=user.first_name, last_name=user.last_name,
            phone=phone, photo_id=photo_id, status='pending')

        request_id = await db.add_verification_request(
            user_id=user.id, group_id=MAIN_GROUP_ID or 0,
            full_name=full_name, phone=phone, photo_id=photo_id)

        mention = format_user_mention(user.id, user.first_name, user.last_name)
        admin_text = get_text('admin_request', 'uz',
            name=full_name, phone=phone, user_id=user.id,
            mention=mention, date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        await _notify_admins(bot, request_id, user.id, full_name, phone, photo_id, admin_text)

        await message.answer(
            get_text('waiting_approval', lang),
            parse_mode='HTML', reply_markup=get_remove_keyboard())

        await state.finish()
        Logger.info(f"Verification request #{request_id} from {user.id}")

    @dp.message_handler(state=Verification.PHOTO)
    async def process_photo_invalid(message: types.Message, state: FSMContext):
        try:
            lang = await db.get_user_language(message.from_user.id)
        except Exception:
            lang = 'uz'
        await message.answer(get_text('photo_invalid', lang))

    @dp.callback_query_handler(lambda c: c.data.startswith("approve:"))
    async def approve_user(callback: types.CallbackQuery):
        bot = dp.bot
        admin = callback.from_user
        if not (await db.is_admin(admin.id) or admin.id == OWNER_ID):
            await callback.answer("❌ Ruxsat yoq!", show_alert=True)
            return

        try:
            _, request_id, user_id = callback.data.split(":")
            request_id = int(request_id)
            user_id = int(user_id)
        except ValueError:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return

        try:
            lang = await db.get_user_language(user_id)
        except Exception:
            lang = 'uz'

        await db.update_verification_status(request_id, 'approved', admin.id)
        await db.update_user_status(user_id, 'active', admin.id)

        group_id = MAIN_GROUP_ID
        invite_link = ""
        if group_id:
            try:
                await bot.approve_chat_join_request(group_id, user_id)
                Logger.info(f"Approved join request {user_id}")
            except Exception:
                pass
            try:
                link = await bot.create_chat_invite_link(
                    chat_id=group_id, member_limit=1, creates_join_request=False)
                invite_link = link.invite_link
            except Exception as e:
                Logger.error(f"Cannot create invite link: {e}")

        if not invite_link:
            try:
                invite_link = await db.get_setting('group_link', '')
            except Exception:
                invite_link = ""

        try:
            text = get_text('approved_with_link', lang, link=invite_link) if invite_link else get_text('approved', lang)
            await bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode='HTML')
        except Exception as e:
            Logger.error(f"Cannot notify {user_id}: {e}")

        try:
            await callback.message.edit_reply_markup(
                reply_markup=get_approved_keyboard(admin.first_name))
        except Exception:
            pass

        await callback.answer("✅ Qabul qilindi!")
        Logger.success(f"User {user_id} approved by {admin.id}")

    @dp.callback_query_handler(lambda c: c.data.startswith("reject:"))
    async def reject_user(callback: types.CallbackQuery):
        bot = dp.bot
        admin = callback.from_user
        if not (await db.is_admin(admin.id) or admin.id == OWNER_ID):
            await callback.answer("❌ Ruxsat yoq!", show_alert=True)
            return

        try:
            _, request_id, user_id = callback.data.split(":")
            request_id = int(request_id)
            user_id = int(user_id)
        except ValueError:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return

        try:
            lang = await db.get_user_language(user_id)
        except Exception:
            lang = 'uz'

        await db.update_verification_status(request_id, 'rejected', admin.id)
        await db.update_user_status(user_id, 'rejected', admin.id)

        group_id = MAIN_GROUP_ID
        if group_id:
            try:
                await bot.decline_chat_join_request(group_id, user_id)
            except Exception:
                pass

        try:
            await bot.send_message(
                chat_id=user_id,
                text=get_text('rejected', lang),
                parse_mode='HTML')
        except Exception as e:
            Logger.error(f"Cannot notify {user_id}: {e}")

        try:
            await callback.message.edit_reply_markup(
                reply_markup=get_rejected_keyboard(admin.first_name))
        except Exception:
            pass

        await callback.answer("❌ Rad etildi!")
        Logger.warning(f"User {user_id} rejected by {admin.id}")

    @dp.callback_query_handler(lambda c: c.data == "done")
    async def done_callback(callback: types.CallbackQuery):
        await callback.answer()
