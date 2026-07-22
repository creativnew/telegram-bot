"""
╔══════════════════════════════════════════════════════════════╗
║                  UTILS - Yordamchi Funksiyalar               ║
╚══════════════════════════════════════════════════════════════╝
"""

import re
from typing import Optional
from config import BAD_WORDS


def contains_bad_words(text: str) -> tuple[bool, Optional[str]]:
    """
    Matnda haqoratli so'zlarni tekshirish
    Returns: (topildi_mi, topilgan_soz)
    """
    if not text:
        return False, None

    text_lower = text.lower()

    for word in BAD_WORDS:
        # To'liq so'z sifatida tekshirish
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        if re.search(pattern, text_lower):
            return True, word

    return False, None


def contains_link(text: str) -> bool:
    """Matnda havola borligini tekshirish"""
    if not text:
        return False

    link_patterns = [
        r'http[s]?://',           # http:// yoki https://
        r't\.me/',                # t.me/
        r'telegram\.me/',         # telegram.me/
        r'tg://',                 # tg://
        r'www\.',                 # www.
        r'@[a-zA-Z0-9_]{5,}',     # @username (5 ta belgidan ko'p)
    ]

    for pattern in link_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def contains_bot_mention(text: str) -> bool:
    """Matnda bot mention borligini tekshirish"""
    if not text:
        return False

    # Bot username (o'zining username'ini tekshirish)
    bot_patterns = [
        r'@\w+_bot',
        r'@\w+bot',
    ]

    for pattern in bot_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def format_phone_number(phone: str) -> str:
    """Telefon raqamini formatlash"""
    if not phone:
        return "Noma'lum"

    # + belgisi bilan boshlansa
    if phone.startswith('+'):
        return phone

    # Faqat raqamlarni qoldirish
    digits = re.sub(r'\D', '', phone)

    if len(digits) == 12 and digits.startswith('998'):
        return f"+{digits}"
    elif len(digits) == 9:
        return f"+998{digits}"

    return phone


def escape_markdown(text: str) -> str:
    """Markdown maxsus belgilarini escape qilish"""
    if not text:
        return ""

    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

    for char in escape_chars:
        text = text.replace(char, f'\\{char}')

    return text


def truncate_text(text: str, max_length: int = 100) -> str:
    """Matnni qisqartirish"""
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."


def format_user_mention(user_id: int, first_name: str, last_name: str = None) -> str:
    """Foydalanuvchi mentionini yaratish"""
    full_name = f"{first_name or ''} {last_name or ''}".strip()
    return f'<a href="tg://user?id={user_id}">{escape_markdown(full_name)}</a>'


def is_valid_user_id(user_id: str) -> bool:
    """Foydalanuvchi ID raqamini tekshirish"""
    try:
        uid = int(user_id)
        return uid > 0
    except (ValueError, TypeError):
        return False


def generate_invite_link(bot_username: str, group_id: int) -> str:
    """Guruhga kirish havolasini yaratish"""
    return f"https://t.me/{bot_username}?start=join_{group_id}"


class Logger:
    """Oddiy logger"""

    @staticmethod
    def info(message: str):
        from datetime import datetime
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: {message}")

    @staticmethod
    def error(message: str):
        from datetime import datetime
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {message}")

    @staticmethod
    def warning(message: str):
        from datetime import datetime
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WARNING: {message}")

    @staticmethod
    def success(message: str):
        from datetime import datetime
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SUCCESS: {message}")
