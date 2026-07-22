"""
╔══════════════════════════════════════════════════════════════╗
║                    TELEGRAM VERIFICATION BOT                 ║
║              Professional Group Protection System            ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
from dataclasses import dataclass

# ============================================================
# ASOSIY SOZLAMALAR (O'ZGARTIRISH KERAK)
# ============================================================

# 1. Bot tokenini @BotFather dan oling va shu yerga qo'ying
BOT_TOKEN = "8780396351:AAH9wejiw1EFHWeTbrka4ygdjai49hp5Z8g"

# 2. Guruh egasining Telegram ID raqami (faqat raqam)
# Buni @userinfobot dan olishingiz mumkin
OWNER_ID = 8489964401

# 3. Adminlar guruhining ID raqami (agar bor bo'lsa)
# Bu guruhga verifikatsiya so'rovlari yuboriladi
ADMIN_GROUP_ID = None  # -1001234567890

# 4. Asosiy guruh ID raqami
MAIN_GROUP_ID = None  # -1009876543210

# 5. Ma'lumotlar bazasi fayli
DATABASE_PATH = "data/bot_database.db"

# 6. Ogohlantirish chegarasi (3 ta ogohlantirganda mut qilish)
WARN_LIMIT = 3

# 7. Mut vaqti (soat)
MUTE_DURATION_HOURS = 24

# 8. Premium stiker (file_id yoki None)
# @StickerDownloadBot dan olishingiz mumkin
PREMIUM_STICKER = None  # "CAACAgIAAxkBAA..."

# 9. Gruh/kanal havolalari (GroupHelpBot uchun)
GROUP_LINK = None  # "https://t.me/your_group"
CHANNEL_LINK = None  # "https://t.me/your_channel"
SUPPORT_LINK = None  # "https://t.me/your_support"

# ============================================================
# QO'SHIMCHA SOZLAMALAR
# ============================================================

# Xabarlarni o'chirish vaqti (soniya)
DELETE_AFTER_SECONDS = 5

# Ogohlantirish xabarini o'chirish vaqti (soniya)
WARN_DELETE_AFTER = 10

# Verifikatsiya xabarini o'chirish vaqti (soniya)
VERIFY_MSG_DELETE = 30

# ============================================================
# SO'KINISH SO'ZLARI RO'YXATI (O'ZBEKCHA)
# ============================================================

BAD_WORDS = [
    # So'kinishlar
    "ahmoq", "jinni", "xar", "eshak", "tentak", "mol", "xomshax",
    "qotil", "yaramas", "pastki", "sharmanda", "beozor", "beqaror",
    "yolg'onchi", "o'g'ri", "qallqon", "pokiz", "xayin", "yaramas",
    "beodob", "beqoida", "beaxloq", "beadab", "beinsop", "beetibor",
    "beoila", "bevaqif", "betaraf", "bejiz", "bejizga", "bejizlik",
    "bejizcha", "bejizchilik", "bejizchilikka", "bejizchilikdan",
    "qaltis", "qalbak", "qalbaki", "qalbakiylik", "qalbakiylikka",
    "qalbakiylikdan", "qalbakiylikni", "qalbakiylikni",

    # Siyosat va noqulay so'zlar
    "terror", "terrorist", "diniy", "ekstremist", "radikal",

    # Ingliz tilidagi so'kinishlar
    "damn", "stupid", "idiot", "fool", "moron", "jerk", "loser",
    "trash", "garbage", "worthless", "useless", "pathetic",
    "asshole", "bastard", "bitch", "dick", "fuck", "shit",
    "crap", "hell", "damn", "damned", "damnable",
]

# ============================================================
# XABARLAR MATNLARI
# ============================================================

WELCOME_MESSAGE = """
👋 <b>Assalomu alaykum!</b>

Guruhimizga xush kelibsiz! 🌸

Bu guruh faqat <b>ayol-qizlar</b> uchun. Xavfsizlik maqsadida verifikatsiyadan o'tishingiz kerak.

Iltimos, quyidagi ma'lumotlarni to'g'ri kiriting:
"""

VERIFICATION_COMPLETE = """
🎉 <b>Rahmat!</b> Ma'lumotlaringiz adminga yuborildi.

Tez orada tekshirilib, guruhga qo'shilasiz.

⏳ Iltimos, kuting...
"""

APPROVED_MESSAGE = """
✅ <b>Tabriklaymiz!</b>

Sizning so'rovingiz admin tomonidan qabul qilindi.

Guruhga qo'shilishingiz mumkin: {link}

🌸 Xush kelibsiz!
"""

REJECTED_MESSAGE = """
❌ <b>Afsuski...</b>

Sizning so'rovingiz admin tomonidan rad etildi.

Agar savollaringiz bo'lsa, admin bilan bog'laning.
"""

ADMIN_APPROVE_TEXT = """
🔔 <b>Yangi a'zolik so'rovi!</b>

👤 <b>Ism:</b> {name}
📱 <b>Tel:</b> {phone}
🆔 <b>Telegram ID:</b> <code>{user_id}</code>
🔗 <b>Profil:</b> {mention}
📅 <b>Sana:</b> {date}
"""

ADMIN_ACTION_APPROVED = "\n\n🟢 Admin <b>{admin_name}</b> tomonidan qabul qilindi ✅"
ADMIN_ACTION_REJECTED = "\n\n🔴 Admin <b>{admin_name}</b> tomonidan rad etildi ❌"

ANTI_LINK_WARNING = "⚠️ {name}, guruhda havola va reklama tarqatish taqiqlangan!"
ANTI_BOT_WARNING = "🤖 {name}, guruhga bot qo'shish taqiqlangan! Bot bloklandi."
ANTI_SWEAR_WARNING = "🚫 {name}, guruhda haqoratli so'zlar ishlatish taqiqlangan! ({warn}/{limit})"
MUTE_MESSAGE = "🔇 {name} 24 soatga mutga qo'yildi. ({warn} ogohlantirish)"

# ============================================================
# PANEL MATNLARI
# ============================================================

PANEL_TEXT = """
👑 <b>ADMIN PANEL</b>

Quyidagi sozlamalarni boshqarishingiz mumkin:
"""

BROADCAST_TEXT = """
📢 <b>Ommaviy xabar</b>

Yuboriladigan xabar matnini yoki rasmni yuboring.
Barcha ro'yxatdan o'tgan a'zolarga yuboriladi.

Bekor qilish uchun /cancel
"""

BROADCAST_SENT = "✅ Xabar {count} ta foydalanuvchiga yuborildi!"
BROADCAST_CANCELLED = "❌ Bekor qilindi."

# ============================================================
# BUTTON MATNLARI
# ============================================================

BTN_SHARE_CONTACT = "📱 Telefon raqamni ulashish"
BTN_APPROVE = "✅ Qabul qilish"
BTN_REJECT = "❌ Rad etish"
BTN_BACK = "🔙 Orqaga"
BTN_CANCEL = "❌ Bekor qilish"

# Toggle button texts
BTN_VERIFICATION_ON = "🔐 Verifikatsiya: 🟢 Yoqilgan"
BTN_VERIFICATION_OFF = "🔐 Verifikatsiya: 🔴 O'chirilgan"
BTN_ANTILINK_ON = "🔗 Anti-Link: 🟢 Yoqilgan"
BTN_ANTILINK_OFF = "🔗 Anti-Link: 🔴 O'chirilgan"
BTN_ANTIBOT_ON = "🤖 Anti-Bot: 🟢 Yoqilgan"
BTN_ANTIBOT_OFF = "🤖 Anti-Bot: 🔴 O'chirilgan"
BTN_ANTISWEAR_ON = "🛡️ Anti-Swear: 🟢 Yoqilgan"
BTN_ANTISWEAR_OFF = "🛡️ Anti-Swear: 🔴 O'chirilgan"
BTN_BROADCAST = "📢 Ommaviy xabar"
BTN_ADD_ADMIN = "➕ Admin qo'shish"
BTN_REMOVE_ADMIN = "➖ Admin o'chirish"
BTN_ADMIN_LIST = "👥 Adminlar ro'yxati"
BTN_STATS = "📊 Statistika"

# ============================================================
# FSM STATE NOMLARI
# ============================================================

class VerificationStates:
    NAME = "verification_name"
    PHONE = "verification_phone"
    PHOTO = "verification_photo"
    COMPLETE = "verification_complete"

class BroadcastStates:
    MESSAGE = "broadcast_message"
    CONFIRM = "broadcast_confirm"

class AdminStates:
    ADD_ID = "admin_add_id"
    REMOVE_ID = "admin_remove_id"

# ============================================================
# YORDAMCHI FUNKSIYALAR
# ============================================================

def get_status_emoji(status: bool) -> str:
    """Statusni emoji ko'rinishida qaytaradi"""
    return "🟢" if status else "🔴"

def get_verification_status_text(is_enabled: bool) -> str:
    """Verifikatsiya status matnini qaytaradi"""
    return BTN_VERIFICATION_ON if is_enabled else BTN_VERIFICATION_OFF

def get_antilink_status_text(is_enabled: bool) -> str:
    """Anti-link status matnini qaytaradi"""
    return BTN_ANTILINK_ON if is_enabled else BTN_ANTILINK_OFF

def get_antibot_status_text(is_enabled: bool) -> str:
    """Anti-bot status matnini qaytaradi"""
    return BTN_ANTIBOT_ON if is_enabled else BTN_ANTIBOT_OFF

def get_antiswear_status_text(is_enabled: bool) -> str:
    """Anti-swear status matnini qaytaradi"""
    return BTN_ANTISWEAR_ON if is_enabled else BTN_ANTISWEAR_OFF
