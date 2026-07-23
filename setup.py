"""
╔══════════════════════════════════════════════════════════════╗
║              SETUP SCRIPT - Botni o'rnatish                   ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import secrets
import sys


def generate_webhook_secret():
    """Random webhook secret generatsiya qilish"""
    return secrets.token_urlsafe(32)


def setup_environment():
    """Environment faylini yaratish"""
    print("🔧 Botni o'rnatish...")
    print("=" * 60)
    
    # .env.example dan .env yaratish
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            with open('.env.example', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Webhook secret generatsiya qilish
            webhook_secret = generate_webhook_secret()
            content = content.replace('your_random_secret_key_here', webhook_secret)
            
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ .env fayli yaratildi")
            print(f"🔑 Webhook Secret: {webhook_secret}")
        else:
            print("❌ .env.example fayli topilmadi")
            return False
    else:
        print("⚠️ .env fayli allaqachon mavjud")
    
    print("=" * 60)
    print("📝 Quyidagilarni .env faylida to'ldiring:")
    print("   - BOT_TOKEN (BotFather dan oling)")
    print("   - OWNER_ID (@userinfobot dan oling)")
    print("=" * 60)
    
    return True


def install_dependencies():
    """Dependencies o'rnatish"""
    print("\n📦 Dependencies o'rnatilmoqda...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies o'rnatildi")
        return True
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False


def create_directories():
    """Kataloglarni yaratish"""
    print("\n📁 Kataloglar yaratilmoqda...")
    directories = ['data', 'logs']
    
    for dir_name in directories:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            print(f"✅ {dir_name}/ katalogi yaratildi")
    
    return True


def main():
    """Asosiy setup funksiyasi"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          TELEGRAM BOT - O'RNATISH WIZARDI                   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Environment
    if not setup_environment():
        print("❌ Setup tugadi")
        return
    
    # Step 2: Directories
    create_directories()
    
    # Step 3: Dependencies
    if not install_dependencies():
        print("⚠️ Dependencies o'rnatilmadi. Qo'lda o'rnating: pip install -r requirements.txt")
    
    print("\n" + "=" * 60)
    print("🎉 Setup tugadi!")
    print("=" * 60)
    print("\nKeyingi qadamlar:")
    print("1. .env faylini oching va BOT_TOKEN, OWNER_ID ni kiriting")
    print("2. python main.py bilan botni ishga tushing")
    print("3. SECURITY.md faylini o'qing")
    print("\n🔒 Xavfsizlik uchun .env faylni Gitga qo'shmang!")


if __name__ == "__main__":
    main()
