import asyncio
import random
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command

from database import db
from config import OWNER_ID, WARN_LIMIT
from utils.helpers import Logger, format_user_mention, delete_after, generate_captcha


NEEDED_PERMS = [
    ('can_delete_messages', '🗑 Xabarlarni ochirish'),
    ('can_restrict_members', '🚫 Aʼzolarni bloklash'),
    ('can_invite_users', '👥 Taklif qilish'),
    ('can_pin_messages', '📌 Xabarlarni mahkamlash'),
    ('can_change_info', '✏️ Guruh malumotlarini ozgartirish'),
]


async def _check_bot_perms(bot, chat):
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
                parse_mode='HTML')
        else:
            await bot.send_message(
                chat_id=chat.id,
                text=f"✅ <b>Barcha ruxsatlar berilgan!</b>\n\nBot toliq ishlashga tayyor.",
                parse_mode='HTML')
            try:
                await bot.send_message(
                    chat_id=OWNER_ID,
                    text=f"✅ <b>Bot toliq ruxsat bilan ishlamoqda:</b>\n"
                         f"👥 {chat.title} (<code>{chat.id}</code>)",
                    parse_mode='HTML')
            except Exception:
                pass
    except Exception as e:
        Logger.error(f"Perm check error in {chat.id}: {e}")


async def _send_captcha(bot, chat_id, user_id, user_name):
    question, answer = generate_captcha('easy')
    await db.save_captcha(user_id, chat_id, answer)
    msg = await bot.send_message(
        chat_id=user_id,
        text=f"🧩 <b>Captcha tekshiruvi!</b>\n\n"
             f"Assalomu alaykum, {user_name}!\n"
             f"Bot ekanligingizni isbotlash uchun quyidagi misolni yeching:\n\n"
             f"<code>{question}</code>\n\n"
             f"Javobni raqamda yuboring. 3 urinish beriladi.",
        parse_mode='HTML')
    await db.save_captcha(user_id, chat_id, answer, msg.message_id)
    return msg


async def _check_and_handle_raid(bot, chat_id, user_id) -> bool:
    anti_raid = await db.get_bool_setting('anti_raid_enabled')
    if not anti_raid:
        return False
    try:
        limit = int(await db.get_setting('raid_limit', '10'))
        interval = int(await db.get_setting('raid_interval', '60'))
    except ValueError:
        limit, interval = 10, 60
    recent = await db.get_recent_joins(chat_id, interval)
    if recent >= limit:
        try:
            await bot.restrict_chat_member(
                chat_id=chat_id, user_id=user_id,
                permissions={p: False for p in [
                    'can_send_messages', 'can_send_media_messages',
                    'can_send_polls', 'can_send_other_messages',
                    'can_add_web_page_previews', 'can_change_info',
                    'can_invite_users', 'can_pin_messages']})
            await bot.send_message(
                chat_id=chat_id,
                text=f"🚨 <b>Reyd aniqlandi!</b>\n\n"
                     f"{recent} ta odam {interval} soniyada qo'shilmoqchi.\n"
                     f"Guruh vaqtincha himoyaga olindi!",
                parse_mode='HTML')
            Logger.warning(f"Raid detected in {chat_id}: {recent} joins in {interval}s")
        except Exception as e:
            Logger.error(f"Raid restrict error: {e}")
        return True
    return False


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

        # Bot events
        if user.id == bot_id:
            if old.status in ['left', 'kicked'] and new.status in ['member', 'administrator']:
                await db.add_group(chat.id, chat.title)
                try:
                    await dp.bot.send_message(
                        chat_id=OWNER_ID,
                        text=f"➕ <b>Bot guruhga qoshildi!</b>\n\n"
                             f"👥 {chat.title}\n🆔 <code>{chat.id}</code>",
                        parse_mode='HTML')
                except Exception:
                    pass
                if new.status == 'administrator':
                    await _check_bot_perms(dp.bot, chat)
                else:
                    msg = (f"👋 <b>Salom! Botni qoshganingiz uchun rahmat!</b>\n\n"
                           f"Bot ishlashi uchun <b>admin huquqlari</b> kerak.\n\n"
                           f"👉 Meni guruh admini qiling va quyidagi ruxsatlarni bering:\n\n"
                           f"{chr(10).join([f'• {p[1]}' for p in NEEDED_PERMS])}\n\n"
                           f"✅ Admin qilgandan song <b>/start</b> ni bosing.")
                    await dp.bot.send_message(chat_id=chat.id, text=msg, parse_mode='HTML')
                return
            if old.status == 'member' and new.status == 'administrator':
                await _check_bot_perms(dp.bot, chat)
                return
            if new.status in ['left', 'kicked']:
                try:
                    await dp.bot.send_message(
                        chat_id=OWNER_ID,
                        text=f"❌ <b>Bot guruhdan chiqarildi:</b>\n"
                             f"👥 {chat.title} (<code>{chat.id}</code>)",
                        parse_mode='HTML')
                except Exception:
                    pass
                return

        # Bot removed duplicate check
        if user.id == bot_id and new.status in ['left', 'kicked']:
            try:
                await dp.bot.send_message(
                    chat_id=OWNER_ID,
                    text=f"❌ <b>Bot guruhdan chiqarildi:</b>\n"
                         f"👥 {chat.title} (<code>{chat.id}</code>)",
                    parse_mode='HTML')
            except Exception:
                pass
            return

        # Anti-Bot: another bot joined
        if user.is_bot and user.id != bot_id and old.status in ['left', 'kicked'] and new.status == 'member':
            antibot = await db.get_bool_setting('antibot_enabled')
            if antibot:
                try:
                    await dp.bot.ban_chat_member(chat.id, user.id)
                    await dp.bot.send_message(
                        chat_id=chat.id,
                        text=f"🤖 <b>Bot bloklandi!</b>\nGuruhga bot qoshish taqiqlangan.",
                        parse_mode='HTML')
                    Logger.warning(f"Bot {user.id} banned from {chat.id}")
                except Exception as e:
                    Logger.error(f"Cannot ban bot: {e}")
            return

        # New user joined
        if not user.is_bot and old.status in ['left', 'kicked'] and new.status == 'member':
            await db.add_user(
                user_id=user.id, username=user.username,
                first_name=user.first_name, last_name=user.last_name,
                status='active')

            # Anti-raid check
            await db.log_join(chat.id, user.id)
            raid = await _check_and_handle_raid(dp.bot, chat.id, user.id)
            if raid:
                return

            # Track new member
            await db.track_new_member(user.id, chat.id)

            # Captcha check
            captcha_enabled = await db.get_bool_setting('captcha_enabled')
            if captcha_enabled:
                try:
                    await dp.bot.restrict_chat_member(
                        chat_id=chat.id, user_id=user.id,
                        permissions={'can_send_messages': False, 'can_send_media_messages': False,
                                     'can_send_polls': False, 'can_send_other_messages': False,
                                     'can_add_web_page_previews': False, 'can_change_info': False,
                                     'can_invite_users': False, 'can_pin_messages': False})
                    await _send_captcha(dp.bot, chat.id, user.id, user.first_name)
                except Exception as e:
                    Logger.error(f"Captcha error for {user.id}: {e}")

            # Welcome message
            welcome = await db.get_bool_setting('welcome_custom_enabled')
            if welcome:
                try:
                    await dp.bot.send_message(
                        chat_id=chat.id,
                        text=f"👋 <b>Xush kelibsiz, {user.first_name}!</b>\nGuruh qoidalariga rioya qiling.",
                        parse_mode='HTML')
                except Exception as e:
                    Logger.error(f"Welcome error: {e}")
            return

        # User left/banned
        if new.status in ['left', 'kicked'] and not user.is_bot:
            status = 'banned' if new.status == 'kicked' else 'left'
            await db.update_user_status(user.id, status)
            await db.remove_new_member_track(user.id, chat.id)
            Logger.info(f"User {user.id} {new.status} from {chat.id}")

    # ========== SERVICE MESSAGE AUTO-DELETE ==========
    @dp.message_handler(content_types=[
        types.ContentType.NEW_CHAT_MEMBERS,
        types.ContentType.LEFT_CHAT_MEMBER,
        types.ContentType.PINNED_MESSAGE,
        types.ContentType.NEW_CHAT_TITLE,
        types.ContentType.NEW_CHAT_PHOTO,
        types.ContentType.DELETE_CHAT_PHOTO,
        types.ContentType.GROUP_CHAT_CREATED,
        types.ContentType.SUPERGROUP_CHAT_CREATED,
    ])
    async def auto_delete_service(message: types.Message):
        svc_delete = await db.get_bool_setting('service_msg_delete_enabled')
        if svc_delete and message.chat.type in ['group', 'supergroup']:
            try:
                await asyncio.sleep(1)
                await message.delete()
            except Exception:
                pass

    # ========== GROUP COMMANDS ==========

    @dp.message_handler(Command("rules"))
    async def cmd_rules(message: types.Message):
        rules_text = await db.get_rules(message.chat.id)
        if rules_text:
            await message.answer(f"📋 <b>Guruh qoidalari:</b>\n\n{rules_text}", parse_mode='HTML')
        else:
            await message.answer("📋 Qoidalar hali o'rnatilmagan. Admin bilan bog'laning.")

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
                    'can_change_info', 'can_invite_users', 'can_pin_messages']})
            args = message.text.split()
            duration = args[1] if len(args) > 1 else "24 soat"
            await message.answer(f"🔇 <b>{target.first_name}</b> {duration}ga mutga qoyildi!",
                                 parse_mode='HTML')
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
                    'can_change_info', 'can_invite_users', 'can_pin_messages']})
            await message.answer(f"🔊 <b>{target.first_name}</b> endi yoza oladi!", parse_mode='HTML')
        except Exception as e:
            Logger.error(f"Unmute error: {e}")
            await message.answer("❌ Xatolik!")

    @dp.message_handler(Command("info"))
    async def cmd_info(message: types.Message):
        target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        try:
            chat_member = await dp.bot.get_chat_member(message.chat.id, target.id)
            user = chat_member.user
            status_emoji = {'creator': '👑', 'administrator': '👮', 'member': '👤'}
            role = status_emoji.get(chat_member.status, '👤')
            join_date = "Noma'lum"
            if hasattr(chat_member, 'joined_at') and chat_member.joined_at:
                join_date = chat_member.joined_at.strftime('%Y-%m-%d')
            text = (
                f"{role} <b>Foydalanuvchi ma'lumoti</b>\n\n"
                f"🆔 ID: <code>{target.id}</code>\n"
                f"👤 Ism: {target.first_name or ''} {target.last_name or ''}\n"
                f"📛 Username: @{target.username if target.username else '-'}\n"
                f"📅 Qo'shilgan: {join_date}\n"
                f"🔰 Status: {chat_member.status}")
            await message.answer(text, parse_mode='HTML')
        except Exception as e:
            Logger.error(f"Info error: {e}")
            await message.answer("❌ Ma'lumot olishda xatolik!")
