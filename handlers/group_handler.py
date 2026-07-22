from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command

from database import db
from config import OWNER_ID
from utils.helpers import Logger


NEEDED_PERMS = [
    ('can_delete_messages', '🗑 Xabarlarni ochirish'),
    ('can_restrict_members', '🚫 Aʼzolarni bloklash'),
    ('can_invite_users', '👥 Taklif qilish'),
    ('can_pin_messages', '📌 Xabarlarni mahkamlash'),
    ('can_change_info', '✏️ Guruh malumotlarini ozgartirish'),
]


async def _check_bot_perms(bot, chat):
    """Botning admin ruxsatlarini tekshirish"""
    try:
        bot_member = await bot.get_chat_member(chat.id, bot.id)
        perms = bot_member.to_python() if hasattr(bot_member, 'to_python') else vars(bot_member)
        missing = []
        for perm_key, perm_name in NEEDED_PERMS:
            val = perms.get(perm_key) if isinstance(perms, dict) else getattr(bot_member, perm_key, None)
            if not val:
                missing.append(perm_name)

        if missing:
            await bot.send_message(
                chat_id=chat.id,
                text=f"⚠️ <b>Quyidagi ruxsatlar berilmagan:</b>\n\n"
                     f"{chr(10).join([f'❌ {m}' for m in missing])}\n\n"
                     f"Iltimos, guruh admini yuqoridagi ruxsatlarni bersin.",
                parse_mode='HTML'
            )
        else:
            await bot.send_message(
                chat_id=chat.id,
                text=f"✅ <b>Barcha ruxsatlar berilgan!</b>\n\nBot toliq ishlashga tayyor.",
                parse_mode='HTML'
            )
            try:
                await bot.send_message(
                    chat_id=OWNER_ID,
                    text=f"✅ <b>Bot toliq ruxsat bilan ishlamoqda:</b>\n"
                         f"👥 {chat.title} (<code>{chat.id}</code>)",
                    parse_mode='HTML'
                )
            except Exception:
                pass
    except Exception as e:
        Logger.error(f"Perm check error in {chat.id}: {e}")


def router(dp: Dispatcher):

    @dp.chat_member_handler()
    async def on_chat_member_update(update: types.ChatMemberUpdated):
        bot_id = dp.bot.id
        new = update.new_chat_member
        old = update.old_chat_member
        if not new or not old:
            return
        user = new.user
        chat = update.chat

        # === Botning ozi bilan bogliq hodisalar ===
        if user.id == bot_id:
            # Bot guruhga qoshildi (member yoki admin sifatida)
            if old.status in ['left', 'kicked'] and new.status in ['member', 'administrator']:
                await db.add_group(chat.id, chat.title)
                try:
                    await dp.bot.send_message(
                        chat_id=OWNER_ID,
                        text=f"➕ <b>Bot guruhga qoshildi!</b>\n\n"
                             f"👥 {chat.title}\n"
                             f"🆔 <code>{chat.id}</code>",
                        parse_mode='HTML'
                    )
                except Exception:
                    pass

                # Agar togridan-togri admin qilib qoshilgan bolsa
                if new.status == 'administrator':
                    await _check_bot_perms(dp.bot, chat)
                else:
                    msg = (
                        f"👋 <b>Salom! Botni qoshganingiz uchun rahmat!</b>\n\n"
                        f"Bot ishlashi uchun <b>admin huquqlari</b> kerak.\n\n"
                        f"👉 Meni guruh admini qiling va quyidagi ruxsatlarni bering:\n\n"
                        f"{chr(10).join([f'• {p[1]}' for p in NEEDED_PERMS])}\n\n"
                        f"✅ Admin qilgandan song <b>/start</b> ni bosing."
                    )
                    await dp.bot.send_message(chat_id=chat.id, text=msg, parse_mode='HTML')
                return

            # Bot admin qilindi (member edi, admin boldi)
            if old.status == 'member' and new.status == 'administrator':
                await _check_bot_perms(dp.bot, chat)
                return

            # Bot guruhdan chiqarildi
            if new.status in ['left', 'kicked']:
                try:
                    await dp.bot.send_message(
                        chat_id=OWNER_ID,
                        text=f"❌ <b>Bot guruhdan chiqarildi:</b>\n"
                             f"👥 {chat.title} (<code>{chat.id}</code>)",
                        parse_mode='HTML'
                    )
                except Exception:
                    pass
                return

        # === Bot guruhdan chiqarildi ===
        if user.id == bot_id and new.status in ['left', 'kicked']:
            try:
                await dp.bot.send_message(
                    chat_id=OWNER_ID,
                    text=f"❌ <b>Bot guruhdan chiqarildi:</b>\n"
                         f"👥 {chat.title} (<code>{chat.id}</code>)",
                    parse_mode='HTML'
                )
            except Exception:
                pass
            return

        # === Boshqa bot qoshildi (Anti-Bot) ===
        if user.is_bot and user.id != bot_id and old.status in ['left', 'kicked'] and new.status == 'member':
            antibot = await db.get_bool_setting('antibot_enabled')
            if antibot:
                try:
                    await dp.bot.ban_chat_member(chat.id, user.id)
                    await dp.bot.send_message(
                        chat_id=chat.id,
                        text=f"🤖 <b>Bot bloklandi!</b>\nGuruhga bot qoshish taqiqlangan.",
                        parse_mode='HTML'
                    )
                    Logger.warning(f"Bot {user.id} banned from {chat.id}")
                except Exception as e:
                    Logger.error(f"Cannot ban bot: {e}")
            return

        # === Oddiy foydalanuvchi qoshildi ===
        if not user.is_bot and old.status in ['left', 'kicked'] and new.status == 'member':
            await db.add_user(
                user_id=user.id, username=user.username,
                first_name=user.first_name, last_name=user.last_name,
                status='active'
            )
            welcome = await db.get_bool_setting('welcome_custom_enabled')
            if welcome:
                try:
                    await dp.bot.send_message(
                        chat_id=chat.id,
                        text=f"👋 <b>Xush kelibsiz, {user.first_name}!</b>\nGuruh qoidalariga rioya qiling.",
                        parse_mode='HTML'
                    )
                except Exception as e:
                    Logger.error(f"Welcome error: {e}")
            return

        # === Foydalanuvchi chiqdi / bloklandi ===
        if new.status in ['left', 'kicked'] and not user.is_bot:
            status = 'banned' if new.status == 'kicked' else 'left'
            await db.update_user_status(user.id, status)
            Logger.info(f"User {user.id} {new.status} from {chat.id}")

    # ============================================================
    # GURUH KOMANDALARI
    # ============================================================

    @dp.message_handler(Command("mute"))
    async def cmd_mute(message: types.Message):
        user_id = message.from_user.id
        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return
        if not message.reply_to_message:
            await message.answer("❌ Foydalanuvchiga reply qilib /mute yuboring.")
            return
        target = message.reply_to_message.from_user
        try:
            await dp.bot.restrict_chat_member(
                chat_id=message.chat.id, user_id=target.id,
                permissions={p: False for p in ['can_send_messages', 'can_send_media_messages',
                    'can_send_polls', 'can_send_other_messages', 'can_add_web_page_previews',
                    'can_change_info', 'can_invite_users', 'can_pin_messages']}
            )
            args = message.text.split()
            duration = args[1] if len(args) > 1 else "24 soat"
            await message.answer(f"🔇 <b>{target.first_name}</b> {duration}ga mutga qoyildi!", parse_mode='HTML')
        except Exception as e:
            Logger.error(f"Mute error: {e}")
            await message.answer("❌ Mut qilishda xatolik!")

    @dp.message_handler(Command("unmute"))
    async def cmd_unmute(message: types.Message):
        user_id = message.from_user.id
        if not (await db.is_admin(user_id) or user_id == OWNER_ID):
            return
        if not message.reply_to_message:
            await message.answer("❌ Foydalanuvchiga reply qilib /unmute yuboring.")
            return
        target = message.reply_to_message.from_user
        try:
            await dp.bot.restrict_chat_member(
                chat_id=message.chat.id, user_id=target.id,
                permissions={p: True for p in ['can_send_messages', 'can_send_media_messages',
                    'can_send_polls', 'can_send_other_messages', 'can_add_web_page_previews',
                    'can_change_info', 'can_invite_users', 'can_pin_messages']}
            )
            await message.answer(f"🔊 <b>{target.first_name}</b> endi yoza oladi!", parse_mode='HTML')
        except Exception as e:
            Logger.error(f"Unmute error: {e}")
            await message.answer("❌ Xatolik!")
