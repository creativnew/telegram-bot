"""
╔══════════════════════════════════════════════════════════════╗
║              FSM STATES - Holatlar Boshqaruvi                ║
║              aiogram.fsm yordamida                           ║
╚══════════════════════════════════════════════════════════════╝
"""

from aiogram.dispatcher.filters.state import State, StatesGroup


# ============================================================
# VERIFIKATSIYA HOLATLARI
# ============================================================

class VerificationStates(StatesGroup):
    """Verifikatsiya zanjiri holatlari"""

    # Ism va familya
    NAME = State()

    # Telefon raqam
    PHONE = State()

    # Selfi rasm
    PHOTO = State()

    # Yakunlandi
    COMPLETE = State()


# ============================================================
# OMMAVIY XABAR HOLATLARI
# ============================================================

class BroadcastStates(StatesGroup):
    """Ommaviy xabar yuborish holatlari"""

    # Xabar matnini kiritish
    MESSAGE = State()

    # Tasdiqlash
    CONFIRM = State()


# ============================================================
# ADMIN BOSHQARUV HOLATLARI
# ============================================================

class AdminStates(StatesGroup):
    """Admin boshqaruv holatlari"""

    # Admin ID kiritish
    ADD_ID = State()

    # Admin o'chirish ID
    REMOVE_ID = State()


# ============================================================
# GURUH SOZLAMALARI HOLATLARI
# ============================================================

class GroupSettingsStates(StatesGroup):
    """Guruh sozlamalari holatlari"""

    # Guruh linkini o'zgartirish
    GROUP_LINK = State()

    # Guruh nomini o'zgartirish
    GROUP_NAME = State()


# ============================================================
# XABARLAR HOLATLARI
# ============================================================

class MessageStates(StatesGroup):
    """Xabarlar holatlari"""

    # Xabarni tahrirlash
    EDIT = State()

    # Xabarni javob berish
    REPLY = State()
