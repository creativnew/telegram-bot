from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

from utils.language import get_text


def _toggle_text(base_key: str, status: bool, lang: str) -> str:
    """Toggle tugmasi matni: [icon] [name]: [status]"""
    status_text = get_text('status_on', lang) if status else get_text('status_off', lang)
    return f"{get_text(base_key, lang)}: {status_text}"


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    from config import BTN_SHARE_CONTACT, BTN_CANCEL
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_SHARE_CONTACT, request_contact=True)],
            [KeyboardButton(text=BTN_CANCEL)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    from config import BTN_CANCEL
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_remove_keyboard():
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()


def get_admin_approve_keyboard(request_id: int, user_id: int) -> InlineKeyboardMarkup:
    from config import BTN_APPROVE, BTN_REJECT
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=BTN_APPROVE,
                    callback_data=f"approve:{request_id}:{user_id}"
                ),
                InlineKeyboardButton(
                    text=BTN_REJECT,
                    callback_data=f"reject:{request_id}:{user_id}"
                )
            ]
        ]
    )
    return keyboard


def get_approved_keyboard(admin_name: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"✅ {admin_name} tomonidan qabul qilindi",
                callback_data="done"
            )]
        ]
    )
    return keyboard


def get_rejected_keyboard(admin_name: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"❌ {admin_name} tomonidan rad etildi",
                callback_data="done"
            )]
        ]
    )
    return keyboard


def get_admin_panel_keyboard(
    verification: bool = True,
    antilink: bool = True,
    antibot: bool = True,
    antiswear: bool = True,
    lang: str = 'uz'
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=_toggle_text('btn_verification', verification, lang),
                callback_data="toggle:verification"
            ),
            InlineKeyboardButton(
                text=_toggle_text('btn_antilink', antilink, lang),
                callback_data="toggle:antilink"
            )
        ],
        [
            InlineKeyboardButton(
                text=_toggle_text('btn_antibot', antibot, lang),
                callback_data="toggle:antibot"
            ),
            InlineKeyboardButton(
                text=_toggle_text('btn_antiswear', antiswear, lang),
                callback_data="toggle:antiswear"
            )
        ],
        [
            InlineKeyboardButton(text=get_text('btn_broadcast', lang), callback_data="broadcast"),
            InlineKeyboardButton(text=get_text('btn_stats', lang), callback_data="stats")
        ],
        [
            InlineKeyboardButton(text=get_text('btn_admin_list', lang), callback_data="admin_list"),
        ],
        [
            InlineKeyboardButton(text=get_text('btn_add_admin', lang), callback_data="admin_add"),
            InlineKeyboardButton(text=get_text('btn_remove_admin', lang), callback_data="admin_remove"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard() -> InlineKeyboardMarkup:
    from config import BTN_BACK
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=BTN_BACK, callback_data="panel_back")]
        ]
    )
    return keyboard


def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yuborish", callback_data="broadcast_send"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel")
            ]
        ]
    )
    return keyboard


def get_stats_keyboard() -> InlineKeyboardMarkup:
    from config import BTN_BACK
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yangilash", callback_data="stats_refresh")],
            [InlineKeyboardButton(text=BTN_BACK, callback_data="panel_back")]
        ]
    )
    return keyboard


def get_main_menu_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_text('btn_security', lang), callback_data="security"),
                InlineKeyboardButton(text=get_text('btn_settings', lang), callback_data="settings"),
            ],
            [
                InlineKeyboardButton(text=get_text('btn_statistics', lang), callback_data="statistics"),
                InlineKeyboardButton(text=get_text('btn_broadcast', lang), callback_data="broadcast"),
            ],
            [
                InlineKeyboardButton(text=get_text('btn_admins', lang), callback_data="admins"),
                InlineKeyboardButton(text=get_text('btn_language', lang), callback_data="lang"),
            ],
        ]
    )
    return keyboard


def get_security_keyboard(
    verification, photo, phone, antilink, antibot, antiswear,
    lang='uz'
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=_toggle_text('btn_verification', verification, lang),
                callback_data="toggle:verification"
            )],
            [InlineKeyboardButton(
                text=_toggle_text('btn_photo', photo, lang),
                callback_data="toggle:ask_photo"
            )],
            [InlineKeyboardButton(
                text=_toggle_text('btn_phone', phone, lang),
                callback_data="toggle:ask_phone"
            )],
            [InlineKeyboardButton(
                text=_toggle_text('btn_antilink', antilink, lang),
                callback_data="toggle:antilink"
            )],
            [InlineKeyboardButton(
                text=_toggle_text('btn_antibot', antibot, lang),
                callback_data="toggle:antibot"
            )],
            [InlineKeyboardButton(
                text=_toggle_text('btn_antiswear', antiswear, lang),
                callback_data="toggle:antiswear"
            )],
            [InlineKeyboardButton(text=get_text('btn_back', lang), callback_data="panel_back")],
        ]
    )
    return keyboard


def get_language_keyboard(lang='uz') -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text('language_uz', lang), callback_data="lang:uz")],
            [InlineKeyboardButton(text=get_text('language_ru', lang), callback_data="lang:ru")],
            [InlineKeyboardButton(text=get_text('language_en', lang), callback_data="lang:en")],
            [InlineKeyboardButton(text=get_text('btn_back', lang), callback_data="panel_back")],
        ]
    )
    return keyboard


def get_start_keyboard(lang='uz') -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Yordam", callback_data="help"),
                InlineKeyboardButton(text=get_text('btn_language', lang), callback_data="lang"),
            ]
        ]
    )
    return keyboard
