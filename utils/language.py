import json
import os
from typing import Optional

LANGUAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'languages')

_lang_cache = {}

def load_language(lang_code: str) -> dict:
    if lang_code in _lang_cache:
        return _lang_cache[lang_code]
    file_path = os.path.join(LANGUAGES_DIR, f"{lang_code}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _lang_cache[lang_code] = data
            return data
    return load_language('uz')

def get_text(key: str, lang_code: str = 'uz', **kwargs) -> str:
    lang_data = load_language(lang_code)
    text = lang_data.get(key, load_language('uz').get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text

def get_all_languages() -> list[dict]:
    return [
        {'code': 'uz', 'name': "🇺🇿 O'zbekcha", 'flag': '🇺🇿'},
        {'code': 'ru', 'name': '🇷🇺 Русский', 'flag': '🇷🇺'},
        {'code': 'en', 'name': '🇺🇸 English', 'flag': '🇺🇸'},
    ]

def get_user_lang(user_id: int, db=None) -> str:
    if db:
        return 'uz'
    return 'uz'
