"""
╔══════════════════════════════════════════════════════════════╗
║              SECURITY MODULE - Xavfsizlik tizimi              ║
║         Rate limiting, Input validation, Anti-abuse         ║
╚══════════════════════════════════════════════════════════════╝
"""

import re
import time
import hashlib
import hmac
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from config import RATE_LIMIT_ENABLED, RATE_LIMIT_PER_MINUTE, RATE_LIMIT_PER_HOUR, WEBHOOK_SECRET


class RateLimiter:
    """Rate limiting - Spamdan himoya"""
    
    def __init__(self):
        self.requests: Dict[int, Dict[str, list]] = defaultdict(lambda: {'minute': [], 'hour': []})
    
    def is_allowed(self, user_id: int) -> Tuple[bool, str]:
        """Foydalanuvchi so'rovi ruxsat bormi?"""
        if not RATE_LIMIT_ENABLED:
            return True, ""
        
        now = time.time()
        user_data = self.requests[user_id]
        
        # Clean old requests
        user_data['minute'] = [t for t in user_data['minute'] if now - t < 60]
        user_data['hour'] = [t for t in user_data['hour'] if now - t < 3600]
        
        # Check limits
        if len(user_data['minute']) >= RATE_LIMIT_PER_MINUTE:
            return False, f"⚠️ Limit: {RATE_LIMIT_PER_MINUTE}/daqiqa"
        
        if len(user_data['hour']) >= RATE_LIMIT_PER_HOUR:
            return False, f"⚠️ Limit: {RATE_LIMIT_PER_HOUR}/soat"
        
        # Add current request
        user_data['minute'].append(now)
        user_data['hour'].append(now)
        
        return True, ""
    
    def reset_user(self, user_id: int):
        """Foydalanuvchi limitlarini tozalash"""
        if user_id in self.requests:
            del self.requests[user_id]


class InputValidator:
    """Input validation - Kiritmalarni tekshirish"""
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> str:
        """Matnni tozalash"""
        if not text:
            return ""
        
        # Length check
        text = text[:max_length]
        
        # Remove dangerous characters
        dangerous_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    @staticmethod
    def validate_user_id(user_id: any) -> bool:
        """User ID validatsiyasi"""
        try:
            uid = int(user_id)
            return uid > 0 and uid < 10000000000  # Telegram ID limits
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Telefon raqam validatsiyasi"""
        if not phone:
            return False
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Check length (Uzbekistan: +998XXXXXXXXX)
        return len(digits) == 12 and digits.startswith('998')
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Username validatsiyasi"""
        if not username:
            return True  # Username is optional
        
        # Telegram username rules
        pattern = r'^[a-zA-Z0-9_]{5,32}$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_link(link: str) -> bool:
        """Havola validatsiyasi"""
        if not link:
            return False
        
        # Basic URL pattern
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, link))
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Fayl nomini tozalash"""
        if not filename:
            return ""
        
        # Remove path traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        # Remove dangerous characters
        dangerous = ['<', '>', ':', '"', '|', '?', '*']
        for char in dangerous:
            filename = filename.replace(char, '')
        
        return filename.strip()


class WebhookSecurity:
    """Webhook security - Webhook endpointni himoya qilish"""
    
    @staticmethod
    def validate_signature(payload: bytes, signature: str) -> bool:
        """Webhook signatureni tekshirish"""
        if not WEBHOOK_SECRET:
            return True  # Agar secret sozlanmagan bo'lsa, o'tkazib yuborish
        
        expected_signature = hmac.new(
            WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    @staticmethod
    def generate_signature(payload: bytes) -> str:
        """Signature generatsiya qilish"""
        if not WEBHOOK_SECRET:
            return ""
        
        return hmac.new(
            WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()


class AntiAbuse:
    """Anti-abuse measures - Xulq-atvor monitoringi"""
    
    def __init__(self):
        self.suspicious_activity: Dict[int, int] = defaultdict(int)
        self.banned_users: set = set()
    
    def report_suspicious(self, user_id: int, activity_type: str):
        """Shubhali faoliyatni xabar qilish"""
        self.suspicious_activity[user_id] += 1
        
        # Agar ko'p shubhali faoliyat bo'lsa
        if self.suspicious_activity[user_id] > 10:
            self.banned_users.add(user_id)
    
    def is_banned(self, user_id: int) -> bool:
        """Foydalanuvchi bloklanganmi?"""
        return user_id in self.banned_users
    
    def unban_user(self, user_id: int):
        """Foydalanuvchini blokdan chiqarish"""
        if user_id in self.banned_users:
            self.banned_users.remove(user_id)
        if user_id in self.suspicious_activity:
            del self.suspicious_activity[user_id]


class SecurityLogger:
    """Security logger - Xavfsizlik loglari"""
    
    @staticmethod
    def log_security_event(event_type: str, user_id: int, details: str = ""):
        """Xavfsizlik hodisasini log qilish"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] SECURITY: {event_type} | User: {user_id} | {details}"
        
        # Log fayliga yozish
        try:
            with open('security.log', 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception:
            pass


# Global instances
rate_limiter = RateLimiter()
anti_abuse = AntiAbuse()
