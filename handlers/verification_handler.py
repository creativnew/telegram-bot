"""
╔══════════════════════════════════════════════════════════════╗
║         VERIFICATION HANDLER - aiogram 2.x                 ║
║         FSM: Ism → Telefon → Selfi → Admin Tasdiqi           ║
╚══════════════════════════════════════════════════════════════╝
"""

from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
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


# FSM Holatlari
class Verification(StatesGroup):
    NAME = State()
    PHONE = State()
    PHOTO = State()


async def _notify_admins(bot, request_id, user_id, full_name, phone, photo_id, admin_text):
    """Adminlarni xabardor qilish"""
    try:
        try:
            if photo_id:
                await bot.send_photo(
                    chat_id=OWNER_ID,
                    photo=photo_id,
                    caption=admin_text,
                    parse_mode='HTML',
                    reply_markup=get_admin_approve_keyboard(request_id, user_id)
                )
            else:
                await bot.send_message(
                    chat_id=OWNER_ID,
                    text=admin_text,
                    parse_mode='HTML',
                    reply_markup=get_admin_approve_keyboard(request_id, user_id)
                )
        except Exception as e:
            Logger.error(f"Cannot send to owner: {e}")

        if ADMIN_GROUP_ID:
            try:
                if photo_id:
                    await bot.send_photo(
                        chat_id=ADMIN_GROUP_ID,
                        photo=photo_id,
                        caption=admin_text,
                        parse_mode='HTML',
                        reply_markup=get_admin_approve_keyboard(request_id, user_id)
                    )
                else:
                    await bot.send_message(
                        chat_id=ADMIN_GROUP_ID,
                        text=admin_text,
                        parse_mode='HTML',
                        reply_markup=get_admin_approve_keyboard(request_id, user_id)
                    )
            except Exception as e:
                Logger.error(f"Cannot send to admin group: {e}")

        admins = await db.get_all_admins()
        for admin in admins:
            if admin['user_id'] != OWNER_ID:
                try:
                    if photo_id:
                        await bot.send_photo(
                            chat_id=admin['user_id'],
                            photo=photo_id,
                            caption=admin_text,
                            parse_mode='HTML',
                            reply_markup=get_admin_approve_keyboard(request_id, user_id)
                        )
                    else:
                        await bot.send_message(
                            chat_id=admin['user_id'],
                            text=admin_text,
                            parse_mode='HTML',
                            reply_markup=get_admin_approve_keyboard(request_id, user_id)
                        )
                except Exception as e:
                    Logger.error(f"Cannot send to admin {admin['user_id']}: {e}")

    except Exception as e:
        Logger.error(f"Error sending to admins: {e}")


def router(dp: Dispatcher):
    """Handlerlarni ro'yxatdan o'tkazish"""

    # ============================================================
    # CHAT JOIN REQUEST - Guruhga kirish so'rovi
    # ============================================================

    @dp.chat_join_request_handler()
    async def on_chat_join_request(join_request: types.ChatJoinRequest):
        """Foydalanuvchi guruhga kirishni xohlaganda"""

        user = join_request.from_user
        chat = join_request.chat
        bot = dp.bot

        # Verifikatsiya yoqilganmi?
        verification_enabled = await db.get_bool_setting('verification_enabled')

        if not verification_enabled:
            # Avtomatik qabul qilish
            try:
                await bot.approve_chat_join_request(chat.id, user.id)
                Logger.info(f"Auto-approved user {user.id} (verification disabled)")
            except Exception as e:
                Logger.error(f"Auto-approve error: {e}")
            return

        # Foydalanuvchini bazaga qo'shish
        await db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            status='pending'
        )

        # Guruhni bazaga qo'shish
        await db.add_group(chat.id, chat.title)

        # Tilni aniqlash
        try:
            user_lang = await db.get_user_language(user.id)
        except:
            user_lang = 'uz'

        # Sozlamalarni tekshirish
        ask_phone = await db.get_bool_setting('ask_phone_enabled')
        ask_photo = await db.get_bool_setting('ask_photo_enabled')

        # Shaxsiy xabarda verifikatsiya boshlash
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

            # FSM holatini o'rnatish
            await Verification.NAME.set()

        except Exception as e:
            Logger.error(f"Cannot send PM to user {user.id}: {e}")
            # Foydalanuvchi botga start bosmagan - avtomatik rad etish
            try:
                await bot.decline_chat_join_request(chat.id, user.id)
            except:
                pass

    # ============================================================
    # VERIFIKATSIYA ZANJIRI (FSM)
    # ============================================================

    @dp.message_handler(state=Verification.NAME)
    async def process_name(message: types.Message, state: FSMContext):
        """Ism va familyani qabul qilish"""
        if not message.text or len(message.text) < 3:
            await message.answer(
                "❌ Ism juda qisqa. Iltimos, to'liq ism va familiyangizni kiriting:"
            )
            return

        await state.update_data(full_name=message.text.strip())

        try:
            lang = await db.get_user_language(message.from_user.id)
        except:
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
            # Ikkalasi ham o'chirilgan - darhol yakunlash
            user = message.from_user
            full_name = message.text.strip()

            await db.add_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=None,
                photo_id=None,
                status='pending'
            )

            request_id = await db.add_verification_request(
                user_id=user.id,
                group_id=MAIN_GROUP_ID or 0,
                full_name=full_name,
                phone=None,
                photo_id=None
            )

            mention = format_user_mention(user.id, user.first_name, user.last_name)

            admin_text = get_text('admin_request', 'uz',
                name=full_name,
                phone='-',
                user_id=user.id,
                mention=mention,
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            bot = dp.bot
            await _notify_admins(bot, request_id, user.id, full_name, None, None, admin_text)

            await message.answer(
                get_text('verification_complete', lang),
                parse_mode='HTML',
                reply_markup=get_remove_keyboard()
            )

            await state.finish()
            Logger.info(f"Verification request #{request_id} from user {user.id}")

    @dp.message_handler(content_types=types.ContentType.CONTACT, state=Verification.PHONE)
    async def process_phone_contact(message: types.Message, state: FSMContext):
        """Telefon raqamni qabul qilish (contact orqali)"""
        if not message.contact:
            await message.answer(
                "❌ Iltimos, pastdagi tugma orqali telefon raqamingizni ulashing."
            )
            return

        # O'z raqamini yuborganmi?
        if message.contact.user_id != message.from_user.id:
            await message.answer(
                "❌ O'zingizning telefon raqamingizni ulashing!"
            )
            return

        phone = message.contact.phone_number
        await state.update_data(phone=phone)

        try:
            lang = await db.get_user_language(message.from_user.id)
        except:
            lang = 'uz'

        ask_photo = await db.get_bool_setting('ask_photo_enabled')

        if ask_photo:
            await Verification.PHOTO.set()
            await message.answer(
                get_text('enter_photo', lang),
                parse_mode='HTML',
                reply_markup=get_cancel_keyboard()
            )
        else:
            # Rasm so'ralmagan - yakunlash
            user = message.from_user
            data = await state.get_data()
            full_name = data.get('full_name', "Noma'lum")

            await db.add_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=phone,
                photo_id=None,
                status='pending'
            )

            request_id = await db.add_verification_request(
                user_id=user.id,
                group_id=MAIN_GROUP_ID or 0,
                full_name=full_name,
                phone=phone,
                photo_id=None
            )

            mention = format_user_mention(user.id, user.first_name, user.last_name)

            admin_text = get_text('admin_request', 'uz',
                name=full_name,
                phone=phone,
                user_id=user.id,
                mention=mention,
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            bot = dp.bot
            await _notify_admins(bot, request_id, user.id, full_name, phone, None, admin_text)

            await message.answer(
                get_text('verification_complete', lang),
                parse_mode='HTML',
                reply_markup=get_remove_keyboard()
            )

            await state.finish()
            Logger.info(f"Verification request #{request_id} from user {user.id}")

    @dp.message_handler(state=Verification.PHONE)
    async def process_phone_text(message: types.Message, state: FSMContext):
        """Qo'lda telefon raqam yuborilgan"""
        await message.answer(
            "❌ Iltimos, faqat pastdagi tugma orqali telefon raqamingizni ulashing."
        )

    @dp.message_handler(content_types=types.ContentType.PHOTO, state=Verification.PHOTO)
    async def process_photo(message: types.Message, state: FSMContext):
        """Selfi rasmni qabul qilish"""
        bot = dp.bot

        # Eng katta rasmni olish
        photo = message.photo[-1]
        photo_id = photo.file_id

        # Ma'lumotlarni olish
        data = await state.get_data()
        full_name = data.get('full_name', "Noma'lum")
        phone = data.get('phone', "Noma'lum")

        user = message.from_user

        try:
            lang = await db.get_user_language(user.id)
        except:
            lang = 'uz'

        # Bazaga saqlash
        await db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=phone,
            photo_id=photo_id,
            status='pending'
        )

        # Verifikatsiya so'rovini yaratish
        request_id = await db.add_verification_request(
            user_id=user.id,
            group_id=MAIN_GROUP_ID or 0,
            full_name=full_name,
            phone=phone,
            photo_id=photo_id
        )

        # Adminlarga yuborish
        mention = format_user_mention(user.id, user.first_name, user.last_name)

        admin_text = get_text('admin_request', 'uz',
            name=full_name,
            phone=phone,
            user_id=user.id,
            mention=mention,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        await _notify_admins(bot, request_id, user.id, full_name, phone, photo_id, admin_text)

        # Foydalanuvchiga xabar
        await message.answer(
            get_text('verification_complete', lang),
            parse_mode='HTML',
            reply_markup=get_remove_keyboard()
        )

        await state.finish()
        Logger.info(f"Verification request #{request_id} from user {user.id}")

    @dp.message_handler(state=Verification.PHOTO)
    async def process_photo_invalid(message: types.Message, state: FSMContext):
        """Noto'g'ri rasm formati"""
        await message.answer(
            "❌ Iltimos, faqat rasm yuboring (selfie).\n\n"
            "Fayl, video yoki boshqa format qabul qilinmaydi."
        )

    # ============================================================
    # ADMIN TASDIQLASH CALLBACK
    # ============================================================

    @dp.callback_query_handler(lambda c: c.data.startswith("approve:"))
    async def approve_user(callback: types.CallbackQuery):
        """Foydalanuvchini qabul qilish"""
        bot = dp.bot

        try:
            _, request_id, user_id = callback.data.split(":")
            request_id = int(request_id)
            user_id = int(user_id)
        except ValueError:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return

        admin = callback.from_user

        try:
            lang = await db.get_user_language(user_id)
        except:
            lang = 'uz'

        # So'rovni yangilash
        await db.update_verification_status(request_id, 'approved', admin.id)
        await db.update_user_status(user_id, 'active', admin.id)

        # Guruhga qo'shish
        group_id = MAIN_GROUP_ID
        if group_id:
            try:
                await bot.approve_chat_join_request(group_id, user_id)
                Logger.info(f"Approved join request for user {user_id}")
            except Exception as e:
                Logger.error(f"Cannot approve join request: {e}")

        # Guruh linkini olish
        group_link = await db.get_setting('group_link', '')

        # Foydalanuvchiga xabar
        try:
            await bot.send_message(
                chat_id=user_id,
                text=get_text('approved', lang, link=group_link or "Guruhga qo'shildingiz! 🎉"),
                parse_mode='HTML'
            )
        except Exception as e:
            Logger.error(f"Cannot notify user {user_id}: {e}")

        # Xabarni yangilash
        admin_name = admin.first_name

        try:
            await callback.message.edit_reply_markup(
                reply_markup=get_approved_keyboard(admin_name)
            )
        except Exception as e:
            Logger.error(f"Cannot edit message: {e}")

        await callback.answer("✅ Qabul qilindi!")
        Logger.success(f"User {user_id} approved by admin {admin.id}")

    @dp.callback_query_handler(lambda c: c.data.startswith("reject:"))
    async def reject_user(callback: types.CallbackQuery):
        """Foydalanuvchini rad etish"""
        bot = dp.bot

        try:
            _, request_id, user_id = callback.data.split(":")
            request_id = int(request_id)
            user_id = int(user_id)
        except ValueError:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return

        admin = callback.from_user

        try:
            lang = await db.get_user_language(user_id)
        except:
            lang = 'uz'

        # So'rovni yangilash
        await db.update_verification_status(request_id, 'rejected', admin.id)
        await db.update_user_status(user_id, 'rejected', admin.id)

        # Guruhga qo'shilmaydi
        group_id = MAIN_GROUP_ID
        if group_id:
            try:
                await bot.decline_chat_join_request(group_id, user_id)
            except Exception as e:
                Logger.error(f"Cannot decline join request: {e}")

        # Foydalanuvchiga xabar
        try:
            await bot.send_message(
                chat_id=user_id,
                text=get_text('rejected', lang),
                parse_mode='HTML'
            )
        except Exception as e:
            Logger.error(f"Cannot notify user {user_id}: {e}")

        # Xabarni yangilash
        admin_name = admin.first_name

        try:
            await callback.message.edit_reply_markup(
                reply_markup=get_rejected_keyboard(admin_name)
            )
        except Exception as e:
            Logger.error(f"Cannot edit message: {e}")

        await callback.answer("❌ Rad etildi!")
        Logger.warning(f"User {user_id} rejected by admin {admin.id}")

    @dp.callback_query_handler(lambda c: c.data == "done")
    async def done_callback(callback: types.CallbackQuery):
        """Tugallangan callback - hech narsa qilmaydi"""
        await callback.answer()
