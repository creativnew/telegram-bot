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
                InlineKeyboardButton(text=get_text('btn_security_section', lang), callback_data="sec_main"),
                InlineKeyboardButton(text=get_text('btn_users_section', lang), callback_data="users_main"),
                InlineKeyboardButton(text=get_text('btn_management_section', lang), callback_data="mgmt_main"),
            ],
            [
                InlineKeyboardButton(text=get_text('btn_stats', lang), callback_data="stats_main"),
                InlineKeyboardButton(text=get_text('btn_broadcast', lang), callback_data="broadcast"),
                InlineKeyboardButton(text=get_text('btn_admins', lang), callback_data="admins_main"),
            ],
            [
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


def _build_category_keyboard(buttons: list, lang: str, cols: int = 2) -> InlineKeyboardMarkup:
    """Category tugmalarini yaratish (2 ustun)"""
    rows = []
    for i in range(0, len(buttons), cols):
        row_buttons = buttons[i:i+cols]
        rows.append(row_buttons)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_security_category_keyboard(settings: dict, lang='uz') -> InlineKeyboardMarkup:
    items = [
        ('btn_antiflood', 'toggle:antiflood'),
        ('btn_antispam', 'toggle:antispam'),
        ('btn_antiporn', 'toggle:antiporn'),
        ('btn_captcha', 'toggle:captcha'),
        ('btn_nightmode', 'toggle:nightmode'),
        ('btn_wordfilter', 'toggle:wordfilter'),
        ('btn_media_restrict', 'toggle:media_restrict'),
        ('btn_invite_restrict', 'toggle:invite_restrict'),
    ]
    buttons = []
    for key, cb in items:
        status = settings.get(key.replace('btn_', ''), False)
        buttons.append(InlineKeyboardButton(
            text=_toggle_text(key, status, lang),
            callback_data=cb
        ))
    buttons.append(InlineKeyboardButton(text=get_text('btn_back', lang), callback_data="panel_back"))
    return _build_category_keyboard(buttons, lang)


def get_users_category_keyboard(settings: dict, lang='uz') -> InlineKeyboardMarkup:
    key_map = {
        'btn_userinfo': 'userinfo',
        'btn_namehistory': 'namehistory',
        'btn_ranking': 'user_ranking',
        'btn_user_search': 'user_search',
    }
    buttons = []
    for btn_key, setting_key in key_map.items():
        status = settings.get(setting_key, False)
        buttons.append(InlineKeyboardButton(
            text=_toggle_text(btn_key, status, lang),
            callback_data=f"toggle:{setting_key}"
        ))
    buttons.append(InlineKeyboardButton(text=get_text('btn_back', lang), callback_data="panel_back"))
    return _build_category_keyboard(buttons, lang)


def get_management_category_keyboard(settings: dict, lang='uz') -> InlineKeyboardMarkup:
    items = [
        ('btn_welcome', 'toggle:welcome_custom'),
        ('btn_rules', 'toggle:rules'),
        ('btn_autoreply', 'toggle:autoreply'),
        ('btn_scheduled', 'toggle:scheduled'),
        ('btn_polls', 'toggle:polls'),
        ('btn_backup', 'toggle:backup'),
        ('btn_log_channel', 'toggle:log_channel'),
        ('btn_blocklist', 'toggle:blocklist'),
    ]
    buttons = []
    for key, cb in items:
        setting_key = cb.split(':')[1]
        status = settings.get(setting_key, False)
        buttons.append(InlineKeyboardButton(
            text=_toggle_text(key, status, lang),
            callback_data=cb
        ))
    buttons.append(InlineKeyboardButton(text=get_text('btn_back', lang), callback_data="panel_back"))
    return _build_category_keyboard(buttons, lang)
