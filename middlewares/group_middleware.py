"""
╔══════════════════════════════════════════════════════════════╗
║           GROUP MIDDLEWARE - aiogram 2.x                     ║
║     Anti-Link, Anti-Bot, Anti-Swear filtrlari                ║
╚══════════════════════════════════════════════════════════════╝
"""

import asyncio
from aiogram import Dispatcher
from aiogram.types import Message, ChatMemberUpdated

from database import db
from config import (
    ANTI_LINK_WARNING, ANTI_BOT_WARNING, ANTI_SWEAR_WARNING,
    MUTE_MESSAGE, DELETE_AFTER_SECONDS, WARN_DELETE_AFTER,
    WARN_LIMIT, MUTE_DURATION_HOURS
)
from utils.helpers import contains_link, contains_bad_words, Logger


def setup_middleware(dp: Dispatcher):
    """Middleware'larni sozlash"""

    @dp.message_handler()
    async def group_middleware(message: Message):
        """Guruh xabarlarini avtomatik nazorat qilish"""

        # Faqat guruh va superguruhlarda ishlaydi
        if message.chat.type not in ['group', 'supergroup']:
            return

        # Adminlarga ta'sir qilmaydi
        try:
            member = await dp.bot.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in ['creator', 'administrator']:
                return
        except Exception:
            pass

        # 1. ANTI-LINK (Reklama himoyasi)
        antilink_enabled = await db.get_bool_setting('antilink_enabled')
        if antilink_enabled and message.text:
            if contains_link(message.text):
                try:
                    # Xabarni o'chirish
                    await message.delete()

                    # Ogohlantirish
                    warning = await message.answer(
                        ANTI_LINK_WARNING.format(name=message.from_user.first_name),
                        parse_mode='HTML'
                    )

                    # Ogohlantirishni avtomatik o'chirish
                    await asyncio.sleep(DELETE_AFTER_SECONDS)
                    await warning.delete()

                    Logger.warning(f"Anti-Link: User {message.from_user.id} blocked")
                    return

                except Exception as e:
                    Logger.error(f"Anti-Link error: {e}")

        # 2. ANTI-SWEAR (So'kinish himoyasi)
        antiswear_enabled = await db.get_bool_setting('antiswear_enabled')
        if antiswear_enabled and message.text:
            has_bad_word, word = contains_bad_words(message.text)
            if has_bad_word:
                try:
                    # Xabarni o'chirish
                    await message.delete()

                    # Ogohlantirish qo'shish
                    warn_count = await db.add_warn(
                        user_id=message.from_user.id,
                        group_id=message.chat.id,
                        reason=f"Haqoratli so'z: {word}",
                        warned_by=dp.bot.id
                    )

                    # Ogohlantirish xabari
                    warning = await message.answer(
                        ANTI_SWEAR_WARNING.format(
                            name=message.from_user.first_name,
                            warn=warn_count,
                            limit=WARN_LIMIT
                        ),
                        parse_mode='HTML'
                    )

                    # Ogohlantirishni avtomatik o'chirish
                    await asyncio.sleep(WARN_DELETE_AFTER)
                    await warning.delete()

                    # Agar 3 ta ogohlantirish bo'lsa, mut qilish
                    if warn_count >= WARN_LIMIT:
                        try:
                            await dp.bot.restrict_chat_member(
                                chat_id=message.chat.id,
                                user_id=message.from_user.id,
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

                            mute_msg = await message.answer(
                                MUTE_MESSAGE.format(
                                    name=message.from_user.first_name,
                                    warn=warn_count
                                ),
                                parse_mode='HTML'
                            )

                            await asyncio.sleep(DELETE_AFTER_SECONDS)
                            await mute_msg.delete()

                            Logger.warning(f"User {message.from_user.id} muted for 24h")

                        except Exception as e:
                            Logger.error(f"Mute error: {e}")

                    return

                except Exception as e:
                    Logger.error(f"Anti-Swear error: {e}")
