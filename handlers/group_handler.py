"""
╔══════════════════════════════════════════════════════════════╗
║           GROUP HANDLER - aiogram 2.x                        ║
║           Yangi a'zo, chiqish, va boshqalar                  ║
╚══════════════════════════════════════════════════════════════╝
"""

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command

from database import db
from config import OWNER_ID
from utils.helpers import Logger


def router(dp: Dispatcher):
    """Handlerlarni ro'yxatdan o'tkazish"""

    # ============================================================
    # YANGI A'ZO (Anti-Bot)
    # ============================================================

    @dp.chat_member_handler()
    async def on_chat_member_update(update: types.ChatMemberUpdated):
        """Guruh a'zolari o'zgarishi"""

        # Yangi a'zo qo'shildi
        if update.new_chat_member and update.new_chat_member.status == 'member':
            new_member = update.new_chat_member.user

            # Bot qo'shilganmi?
            if new_member.is_bot and new_member.id != dp.bot.id:
                antibot_enabled = await db.get_bool_setting('antibot_enabled')

                if antibot_enabled:
                    try:
                        # Botni bloklash
                        await dp.bot.ban_chat_member(
                            chat_id=update.chat.id,
                            user_id=new_member.id
                        )

                        # Ogohlantirish xabari
                        await dp.bot.send_message(
                            chat_id=update.chat.id,
                            text=f"🤖 <b>Bot bloklandi!</b>\n\n"
                                 f"Guruhga bot qo'shish taqiqlangan.",
                            parse_mode='HTML'
                        )

                        Logger.warning(f"Bot {new_member.id} banned from group {update.chat.id}")

                    except Exception as e:
                        Logger.error(f"Cannot ban bot: {e}")

            # Oddiy foydalanuvchi
            else:
                # Bazaga qo'shish
                await db.add_user(
                    user_id=new_member.id,
                    username=new_member.username,
                    first_name=new_member.first_name,
                    last_name=new_member.last_name,
                    status='active'
                )

                # Log
                await db.add_log(
                    action='user_joined',
                    user_id=new_member.id,
                    details=f"Joined group {update.chat.id}"
                )

                # Welcome xabar (agar yoqilgan bo'lsa)
                welcome_enabled = await db.get_bool_setting('welcome_message')
                if welcome_enabled:
                    try:
                        await dp.bot.send_message(
                            chat_id=update.chat.id,
                            text=f"👋 <b>Xush kelibsiz, {new_member.first_name}!</b>\n\n"
                                 f"Guruh qoidalariga rioya qiling.",
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        Logger.error(f"Welcome message error: {e}")

        # A'zo chiqdi yoki bloklandi
        elif update.new_chat_member and update.new_chat_member.status in ['left', 'kicked']:
            user = update.new_chat_member.user

            status = 'banned' if update.new_chat_member.status == 'kicked' else 'left'
            await db.update_user_status(user.id, status)

            Logger.info(f"User {user.id} {update.new_chat_member.status} from group {update.chat.id}")

    # ============================================================
    # GURUH KOMANDALARI
    # ============================================================

    @dp.message_handler(Command("mute"))
    async def cmd_mute(message: types.Message):
        """Foydalanuvchini mut qilish"""
        user_id = message.from_user.id

        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return

        if not message.reply_to_message:
            await message.answer("❌ Foydalanuvchiga reply qilib /mute yuboring.")
            return

        target = message.reply_to_message.from_user

        try:
            await dp.bot.restrict_chat_member(
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

            # Vaqtini olish (ixtiyoriy)
            args = message.text.split()
            duration = "24 soat"
            if len(args) > 1:
                duration = args[1]

            await message.answer(
                f"🔇 <b>{target.first_name}</b> {duration}ga mutga qo'yildi!",
                parse_mode='HTML'
            )

        except Exception as e:
            Logger.error(f"Mute error: {e}")
            await message.answer("❌ Mut qilishda xatolik!")

    @dp.message_handler(Command("unmute"))
    async def cmd_unmute(message: types.Message):
        """Mutni olish"""
        user_id = message.from_user.id

        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return

        if not message.reply_to_message:
            await message.answer("❌ Foydalanuvchiga reply qilib /unmute yuboring.")
            return

        target = message.reply_to_message.from_user

        try:
            await dp.bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=target.id,
                permissions={
                    'can_send_messages': True,
                    'can_send_media_messages': True,
                    'can_send_polls': True,
                    'can_send_other_messages': True,
                    'can_add_web_page_previews': True,
                    'can_change_info': False,
                    'can_invite_users': True,
                    'can_pin_messages': False
                }
            )

            await message.answer(
                f"🔊 <b>{target.first_name}</b> endi yoza oladi!",
                parse_mode='HTML'
            )

        except Exception as e:
            Logger.error(f"Unmute error: {e}")
            await message.answer("❌ Xatolik!")
