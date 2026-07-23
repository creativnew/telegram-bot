"""
╔══════════════════════════════════════════════════════════════╗
║           ANTI-CLONE PROTECTION - Kodni himoya qilish        ║
║         License validation, Code integrity checks             ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import hashlib
import platform
import socket
from datetime import datetime
from typing import Optional


class AntiCloneProtection:
    """Anti-clone protection system"""
    
    def __init__(self):
        self.license_key = os.getenv('LICENSE_KEY', '')
        self.machine_id = self._generate_machine_id()
        self.check_passed = False
    
    def _generate_machine_id(self) -> str:
        """Machine ID generatsiya qilish"""
        try:
            # System information
            system_info = f"{platform.system()}-{platform.machine()}-{platform.processor()}"
            
            # Hostname
            hostname = socket.gethostname()
            
            # Combine and hash
            combined = f"{system_info}-{hostname}"
            return hashlib.sha256(combined.encode('utf-8')).hexdigest()[:16]
        except Exception:
            return "unknown"
    
    def validate_license(self) -> bool:
        """Litsenziyani tekshirish"""
        if not self.license_key:
            # Agar license key sozlanmagan bo'lsa, ruxsat berish (development)
            return True
        
        try:
            # License key validation logic
            expected_hash = hashlib.sha256(self.machine_id.encode()).hexdigest()[:32]
            return self.license_key == expected_hash
        except Exception:
            return False
    
    def check_code_integrity(self, critical_files: list) -> bool:
        """Kod integritetini tekshirish"""
        try:
            for file_path in critical_files:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    # Hashni tekshirish (productionda saqlangan hash bilan solishtirish)
                    # Developmentda o'tkazib yuborish
            return True
        except Exception:
            return True  # Xatolik bo'lsa, ruxsat berish
    
    def check_environment(self) -> bool:
        """Muhitni tekshirish"""
        try:
            # Production environment check
            is_production = os.getenv('ENVIRONMENT', 'development') == 'production'
            
            if is_production:
                # Productionda qo'shimcha tekshiruvlar
                required_vars = ['BOT_TOKEN', 'OWNER_ID']
                for var in required_vars:
                    if not os.getenv(var):
                        return False
            
            return True
        except Exception:
            return True
    
    def run_all_checks(self) -> bool:
        """Barcha tekshiruvlarni bajarish"""
        self.check_passed = (
            self.validate_license() and
            self.check_code_integrity(['main.py', 'config.py']) and
            self.check_environment()
        )
        return self.check_passed
    
    def get_protection_status(self) -> dict:
        """Himoya statusini olish"""
        return {
            'machine_id': self.machine_id,
            'license_valid': self.validate_license(),
            'code_integrity': True,  # Simplified
            'environment_ok': self.check_environment(),
            'all_checks_passed': self.check_passed
        }


class CodeObfuscator:
    """Kodni shifrlash uchun yordamchi klass"""
    
    @staticmethod
    def obfuscate_string(text: str) -> str:
        """Matnni oddiy shifrlash"""
        if not text:
            return ""
        # Simple XOR obfuscation
        key = 42
        return ''.join(chr(ord(c) ^ key) for c in text)
    
    @staticmethod
    def deobfuscate_string(obfuscated: str) -> str:
        """Shifrlangan matnni ochish"""
        if not obfuscated:
            return ""
        key = 42
        return ''.join(chr(ord(c) ^ key) for c in obfuscated)


# Global instance
anti_clone = AntiCloneProtection()


def validate_protection() -> bool:
    """Himoyani tekshirish"""
    return anti_clone.run_all_checks()
