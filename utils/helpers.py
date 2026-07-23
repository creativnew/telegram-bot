import re
import random
import asyncio
from typing import Optional, Tuple, List
from datetime import datetime
from config import BAD_WORDS


def contains_bad_words(text: str) -> Tuple[bool, Optional[str]]:
    if not text:
        return False, None
    text_lower = text.lower()
    for word in BAD_WORDS:
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        if re.search(pattern, text_lower):
            return True, word
    return False, None


def contains_link(text: str) -> bool:
    if not text:
        return False
    link_patterns = [
        r'http[s]?://', r't\.me/', r'telegram\.me/', r'tg://',
        r'www\.', r'@[a-zA-Z0-9_]{5,}',
    ]
    for pattern in link_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def contains_bot_mention(text: str) -> bool:
    if not text:
        return False
    bot_patterns = [r'@\w+_bot', r'@\w+bot']
    for pattern in bot_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def is_spam(text: str) -> bool:
    if not text:
        return False
    spam_patterns = [
        r'(.)\1{15,}', r'[A-Za-z0-9]{30,}', r'\b(\w+\s)\1{4,}',
        r'\b(подпишись|подписка|реклама|реклам|заработок|заработай|приглашаю|официальный|бесплатно|халява)\b',
        r'\b(реклама|спам|рассылка|бот|зарплата|доход|пассивный|прибыль|миллионер)\b',
    ]
    for pattern in spam_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def contains_forward_spam(text: str, forward_from: Optional[object] = None) -> bool:
    if forward_from:
        return True
    return False


def check_bio_for_ad(username: str = None, bio: str = None) -> Tuple[bool, Optional[str]]:
    text = f"{username or ''} {bio or ''}".lower()
    ad_signals = [
        r't\.me/', r'http[s]?://', r'@\w+_bot', r'@\w+bot',
        r'\b(реклама|подпишись|заработок|сайт|канал|чат)\b',
        r'\b(reklama|reklama|kanal|kanalim|guruh)\b',
        r'\b(пополнение|крипта|криптовалюта|инвестиция|биткоин)\b',
    ]
    for pattern in ad_signals:
        if re.search(pattern, text, re.IGNORECASE):
            return True, pattern
    return False, None


def generate_captcha(difficulty: str = 'easy') -> Tuple[str, str]:
    if difficulty == 'easy':
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        op = random.choice(['+', '-'])
        if op == '-':
            if a < b:
                a, b = b, a
            answer = str(a - b)
        else:
            answer = str(a + b)
        question = f"{a} {op} {b} = ?"
    else:
        a = random.randint(10, 50)
        b = random.randint(1, 20)
        op = random.choice(['+', '-', '*'])
        if op == '-':
            if a < b:
                a, b = b, a
            answer = str(a - b)
        elif op == '*':
            a = random.randint(2, 12)
            b = random.randint(2, 10)
            answer = str(a * b)
        else:
            answer = str(a + b)
        question = f"{a} {op} {b} = ?"
    return question, answer


def format_phone_number(phone: str) -> str:
    if not phone:
        return "Noma'lum"
    if phone.startswith('+'):
        return phone
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 12 and digits.startswith('998'):
        return f"+{digits}"
    elif len(digits) == 9:
        return f"+998{digits}"
    return phone


def escape_markdown(text: str) -> str:
    if not text:
        return ""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def truncate_text(text: str, max_length: int = 100) -> str:
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_user_mention(user_id: int, first_name: str, last_name: str = None) -> str:
    full_name = f"{first_name or ''} {last_name or ''}".strip()
    return f'<a href="tg://user?id={user_id}">{escape_markdown(full_name)}</a>'


def is_valid_user_id(user_id: str) -> bool:
    try:
        uid = int(user_id)
        return uid > 0
    except (ValueError, TypeError):
        return False


def generate_invite_link(bot_username: str, group_id: int) -> str:
    return f"https://t.me/{bot_username}?start=join_{group_id}"


def is_service_message(message) -> bool:
    if message.new_chat_members or message.left_chat_member:
        return True
    if message.pinned_message:
        return True
    if message.new_chat_title or message.new_chat_photo or message.delete_chat_photo:
        return True
    if message.group_chat_created or message.supergroup_chat_created:
        return True
    return False


def contains_cached_link(text: str) -> bool:
    if not text:
        return False
    patterns = [
        r'instagram\.com/', r'twitter\.com/', r'x\.com/',
        r'youtube\.com/', r'youtu\.be/', r'tiktok\.com/',
        r'facebook\.com/', r'fb\.com/', r'vk\.com/',
        r'whatsapp\.com/', r'discord\.gg/', r'github\.com/',
    ]
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


async def delete_after(message, seconds: int = 5):
    await asyncio.sleep(seconds)
    try:
        await message.delete()
    except Exception:
        pass


async def log_to_channel(bot, action: str, details: str = None, user_id: int = None, admin_id: int = None):
    from database import db
    try:
        channel_id = await db.get_setting('log_channel_id', '')
        if channel_id:
            text = f"📝 <b>Log</b>\n\n"
            text += f"🔹 <b>Amal:</b> {action}\n"
            if user_id:
                text += f"👤 Foydalanuvchi: <code>{user_id}</code>\n"
            if admin_id:
                text += f"👮 Admin: <code>{admin_id}</code>\n"
            if details:
                text += f"📄 Tafsilot: {details}\n"
            from datetime import datetime
            text += f"🕐 Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            await bot.send_message(chat_id=int(channel_id), text=text, parse_mode='HTML')
    except Exception:
        pass


class Logger:
    @staticmethod
    def info(message: str):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: {message}")

    @staticmethod
    def error(message: str):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {message}")

    @staticmethod
    def warning(message: str):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WARNING: {message}")

    @staticmethod
    def success(message: str):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SUCCESS: {message}")
