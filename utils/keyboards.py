from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

import json


# ============================================================
# PANEL V2 — 2 QAVATLI MENYU
# ============================================================

CATEGORIES = {
    'verification': {
        'icon': '🔐', 'label_uz': "Verifikatsiya tizimi", 'label_ru': "Верификация", 'label_en': "Verification",
        'features': ['verification_enabled', 'ask_photo_enabled', 'ask_phone_enabled']
    },
    'security': {
        'icon': '🛡️', 'label_uz': "Guruh himoyasi", 'label_ru': "Защита группы", 'label_en': "Group security",
        'features': ['antiflood_enabled', 'antispam_enabled', 'antiporn_enabled', 'captcha_enabled',
                     'nightmode_enabled', 'wordfilter_enabled', 'media_restrict_enabled',
                     'invite_restrict_enabled', 'anti_raid_enabled', 'new_member_restrict_enabled',
                     'service_msg_delete_enabled', 'bio_filter_enabled',
                     'antilink_enabled', 'antibot_enabled', 'antiswear_enabled']
    },
    'users': {
        'icon': '👤', 'label_uz': "Foydalanuvchilar", 'label_ru': "Пользователи", 'label_en': "Users",
        'features': ['userinfo_enabled', 'namehistory_enabled', 'user_ranking_enabled', 'user_search_enabled']
    },
    'management': {
        'icon': '⚙️', 'label_uz': "Boshqaruv", 'label_ru': "Управление", 'label_en': "Management",
        'features': ['welcome_custom_enabled', 'rules_enabled', 'autoreply_enabled', 'scheduled_enabled',
                     'polls_enabled', 'backup_enabled', 'log_channel_enabled', 'blocklist_enabled']
    },
}

CATEGORY_ORDER = ['verification', 'security', 'users', 'management']

LANG = {'uz': 0, 'ru': 1, 'en': 2}


def _label(cat_key, lang_code):
    cat = CATEGORIES[cat_key]
    lang_idx = LANG.get(lang_code, 0)
    labels = [cat['label_uz'], cat['label_ru'], cat['label_en']]
    return f"{cat['icon']} {labels[lang_idx]}"


def _get_lang(callback_or_message):
    """Helper to get language from callback/message (simplified)"""
    return 'uz'  # default, actual lang will be passed from handler


async def count_enabled(group_id, features, db):
    """Count how many features are enabled in a list"""
    count = 0
    for key in features:
        try:
            if await db.get_group_bool_setting(group_id, key):
                count += 1
        except Exception:
            pass
    return count


# ============================================================
# 1-QAVAT: ASOSIY MENYU
# ============================================================

async def get_panel_main_keyboard(group_id, lang, db, show_bot_settings=False):
    rows = []
    for cat_key in CATEGORY_ORDER:
        cat = CATEGORIES[cat_key]
        enabled = await count_enabled(group_id, cat['features'], db)
        total = len(cat['features'])
        label = _label(cat_key, lang)
        rows.append([InlineKeyboardButton(
            text=f"{label} ({enabled}/{total})",
            callback_data=f"panel:cat:{cat_key}"
        )])
    rows.append([InlineKeyboardButton(
        text="🔍 Barcha sozlamalar", callback_data="panel:all"
    )])
    tool_buttons = []
    tool_buttons.append(InlineKeyboardButton(text="🔧 Asboblar", callback_data="panel:tools"))
    if show_bot_settings:
        tool_buttons.append(InlineKeyboardButton(text="🔗 Bot sozlamalari", callback_data="panel:bot_settings"))
    if tool_buttons:
        rows.append(tool_buttons)
    rows.append([InlineKeyboardButton(
        text="🌐 Til", callback_data="panel:lang"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ============================================================
# 2-QAVAT: BO'LIM ICHKI MENYU
# ============================================================

async def get_category_menu(group_id, cat_key, lang, db):
    cat = CATEGORIES[cat_key]
    label = _label(cat_key, lang)
    text = f"<b>{label}</b>\n\n"
    enabled = 0

    # Feature buttons
    feature_map = {
        'verification_enabled': ('btn_verification', 'toggle'),
        'ask_photo_enabled': ('btn_photo', 'toggle'),
        'ask_phone_enabled': ('btn_phone', 'toggle'),
        'antilink_enabled': ('btn_antilink', 'toggle'),
        'antibot_enabled': ('btn_antibot', 'toggle'),
        'antiswear_enabled': ('btn_antiswear', 'toggle'),
        'antiflood_enabled': ('btn_antiflood', 'toggle'),
        'antispam_enabled': ('btn_antispam', 'toggle'),
        'antiporn_enabled': ('btn_antiporn', 'toggle'),
        'captcha_enabled': ('btn_captcha', 'toggle'),
        'nightmode_enabled': ('btn_nightmode', 'toggle'),
        'wordfilter_enabled': ('btn_wordfilter', 'toggle'),
        'media_restrict_enabled': ('btn_media_restrict', 'toggle'),
        'invite_restrict_enabled': ('btn_invite_restrict', 'toggle'),
        'anti_raid_enabled': ('btn_anti_raid', 'toggle'),
        'new_member_restrict_enabled': ('btn_new_member_restrict', 'toggle'),
        'service_msg_delete_enabled': ('btn_service_msg_delete', 'toggle'),
        'bio_filter_enabled': ('btn_bio_filter', 'toggle'),
        'userinfo_enabled': ('btn_userinfo', 'toggle'),
        'namehistory_enabled': ('btn_namehistory', 'toggle'),
        'user_ranking_enabled': ('btn_ranking', 'toggle'),
        'user_search_enabled': ('btn_user_search', 'toggle'),
        'welcome_custom_enabled': ('btn_welcome', 'toggle'),
        'rules_enabled': ('btn_rules', 'toggle'),
        'autoreply_enabled': ('btn_autoreply', 'toggle'),
        'scheduled_enabled': ('btn_scheduled', 'toggle'),
        'polls_enabled': ('btn_polls', 'toggle'),
        'backup_enabled': ('btn_backup', 'toggle'),
        'log_channel_enabled': ('btn_log_channel', 'toggle'),
        'blocklist_enabled': ('btn_blocklist', 'toggle'),
    }

    buttons = []
    for feat_key in cat['features']:
        info = feature_map.get(feat_key)
        if not info:
            continue
        btn_key, action = info
        status = await db.get_group_bool_setting(group_id, feat_key)
        if status:
            enabled += 1
            icon = "🟢"
        else:
            icon = "🔴"
        if action == 'toggle':
            callback = f"panel:toggle:{cat_key}:{feat_key}"
        else:
            callback = f"panel:input:{cat_key}:{feat_key}"
        # Use btn_key from language file
        from utils.language import get_text
        label_text = get_text(btn_key, lang)
        buttons.append(InlineKeyboardButton(
            text=f"{icon} {label_text}",
            callback_data=callback
        ))

    # Arrange buttons in pairs
    rows = []
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            rows.append([buttons[i], buttons[i + 1]])
        else:
            rows.append([buttons[i]])

    # Reset to default button
    rows.append([InlineKeyboardButton(
        text="🔄 Standart holatga qaytarish",
        callback_data=f"panel:reset:{cat_key}"
    )])
    rows.append([InlineKeyboardButton(
        text="⬅️ Orqaga",
        callback_data="panel:main"
    )])

    total = len(cat['features'])
    text = f"<b>{label}</b>\n\n{enabled}/{total} yoqiq"
    return text, InlineKeyboardMarkup(inline_keyboard=rows)


# ============================================================
# BARCHA SOZLAMALAR
# ============================================================

async def get_all_settings_text(group_id, lang, db):
    from utils.language import get_text_all
    lines = ["<b>🔍 Barcha sozlamalar</b>\n"]
    for cat_key in CATEGORY_ORDER:
        cat = CATEGORIES[cat_key]
        label = _label(cat_key, lang)
        lines.append(f"\n<b>{label}:</b>")
        for feat_key in cat['features']:
            status = await db.get_group_bool_setting(group_id, feat_key)
            icon = "🟢" if status else "🔴"
            # Get a display name
            display = feat_key.replace('_enabled', '').replace('_', ' ').title()
            lines.append(f"  {icon} {display}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="panel:main")]
    ])
    return "\n".join(lines), keyboard


# ============================================================
# BOT SOZLAMALARI
# ============================================================

def get_bot_settings_keyboard(links: dict, lang='uz'):
    from utils.language import get_text
    rows = [
        [InlineKeyboardButton(text=f"👥 Guruh: {links.get('group_link','❌')[:20]}", callback_data="panel:bot:group")],
        [InlineKeyboardButton(text=f"📢 Kanal: {links.get('channel_link','❌')[:20]}", callback_data="panel:bot:channel")],
        [InlineKeyboardButton(text=f"🆘 Support: {links.get('support_link','❌')[:20]}", callback_data="panel:bot:support")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="panel:main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ============================================================
# GROUP SELECTION (for DM mode)
# ============================================================

def get_group_selection_keyboard(groups: list, lang='uz'):
    rows = []
    for g in groups:
        rows.append([InlineKeyboardButton(
            text=f"👥 {g.get('group_name', g['group_id'])}",
            callback_data=f"panel:select_group:{g['group_id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ============================================================
# CONFIRMATION KEYBOARD
# ============================================================

def get_confirm_keyboard(action: str, lang='uz'):
    from utils.language import get_text
    rows = [
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=action),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="panel:main"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ============================================================
# LEGACY KEYBOARDS (backward compatibility)
# ============================================================

def get_contact_keyboard() -> ReplyKeyboardMarkup:
    from config import BTN_SHARE_CONTACT, BTN_CANCEL
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_SHARE_CONTACT, request_contact=True)],
            [KeyboardButton(text=BTN_CANCEL)]
        ], resize_keyboard=True, one_time_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    from config import BTN_CANCEL
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True, one_time_keyboard=True)


def get_remove_keyboard():
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()


def get_admin_approve_keyboard(request_id: int, user_id: int) -> InlineKeyboardMarkup:
    from config import BTN_APPROVE, BTN_REJECT
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BTN_APPROVE, callback_data=f"approve:{request_id}:{user_id}"),
         InlineKeyboardButton(text=BTN_REJECT, callback_data=f"reject:{request_id}:{user_id}")]
    ])


def get_approved_keyboard(admin_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ {admin_name} tomonidan qabul qilindi", callback_data="done")]])


def get_rejected_keyboard(admin_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"❌ {admin_name} tomonidan rad etildi", callback_data="done")]])


def get_back_keyboard() -> InlineKeyboardMarkup:
    from config import BTN_BACK
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BTN_BACK, callback_data="panel_back")]])


def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yuborish", callback_data="broadcast_send"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel")]])


def get_stats_keyboard() -> InlineKeyboardMarkup:
    from config import BTN_BACK
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Yangilash", callback_data="stats_refresh")],
        [InlineKeyboardButton(text=BTN_BACK, callback_data="panel_back")]])


def get_language_keyboard(lang='uz') -> InlineKeyboardMarkup:
    from utils.language import get_text
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('language_uz', lang), callback_data="panel:lang:uz")],
        [InlineKeyboardButton(text=get_text('language_ru', lang), callback_data="panel:lang:ru")],
        [InlineKeyboardButton(text=get_text('language_en', lang), callback_data="panel:lang:en")],
        [InlineKeyboardButton(text=get_text('btn_back', lang), callback_data="panel:main")]])


def get_grouphelp_keyboard(bot_username='', group_link='', channel_link='', support_link='') -> InlineKeyboardMarkup:
    add_url = f"https://t.me/{bot_username}?startgroup=admin" if bot_username else "https://t.me/"
    buttons = [
        [InlineKeyboardButton(text="➕ Добавить меня в группу", url=add_url)],
        [InlineKeyboardButton(text="👥 Группа", url=group_link or "https://t.me/"),
         InlineKeyboardButton(text="📢 Канал", url=channel_link or "https://t.me/")],
        [InlineKeyboardButton(text="🆘 Поддержка", url=support_link or "https://t.me/"),
         InlineKeyboardButton(text="ℹ️ Информация", callback_data="help")],
        [InlineKeyboardButton(text="🌐 Languages", callback_data="start_lang_menu")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_start_language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="start_lang:uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="start_lang:ru")],
        [InlineKeyboardButton(text="🇺🇸 English", callback_data="start_lang:en")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="start_back")]])


def get_tools_keyboard(lang='uz') -> InlineKeyboardMarkup:
    from utils.language import get_text
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('btn_word_filter_tool', lang), callback_data="panel:tool:wordfilter"),
         InlineKeyboardButton(text=get_text('btn_blocklist_tool', lang), callback_data="panel:tool:blocklist")],
        [InlineKeyboardButton(text=get_text('btn_rules_tool', lang), callback_data="panel:tool:rules"),
         InlineKeyboardButton(text=get_text('btn_autoreply_tool', lang), callback_data="panel:tool:autoreply")],
        [InlineKeyboardButton(text=get_text('btn_log_channel_tool', lang), callback_data="panel:tool:log_channel"),
         InlineKeyboardButton(text=get_text('btn_export_tool', lang), callback_data="panel:tool:export")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="panel:main")]])
