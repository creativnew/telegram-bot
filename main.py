"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🤖 TELEGRAM VERIFICATION BOT - aiogram 2.x versiyasi        ║
║                                                                  ║
║     Python 3.14 bilan mos, pydantic talab qilmaydi             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

# Konfiguratsiya
from config import BOT_TOKEN, OWNER_ID

# Ma'lumotlar bazasi
from database import db

# Logging sozlamalari
class StdoutStreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(sys.stdout)
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except UnicodeEncodeError:
            # Emoji va maxsus belgilarni olib tashlab yozish
            try:
                msg = self.format(record).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                stream = self.stream
                stream.write(msg.encode(stream.encoding, errors='replace').decode(stream.encoding, errors='replace') + self.terminator)
                self.flush()
            except Exception:
                self.handleError(record)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        StdoutStreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


async def on_startup(dispatcher):
    """Bot ishga tushganda with security checks"""
    logger.info("=" * 60)
    logger.info("🤖 Bot ishga tushmoqda...")
    logger.info("=" * 60)

    # Security: Anti-clone protection check
    try:
        from utils.anti_clone import validate_protection, anti_clone
        if validate_protection():
            logger.info("✅ Security checks passed")
        else:
            logger.warning("⚠️ Security checks failed - running in degraded mode")
    except Exception as e:
        logger.error(f"Security check error: {e}")

    # Ma'lumotlar bazasi katalogini yaratish
    try:
        data_dir = os.path.dirname("data/bot_database.db")
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            logger.info(f"✅ Data directory created: {data_dir}")
    except Exception as e:
        logger.error(f"Cannot create data directory: {e}")

    # Ma'lumotlar bazasini ulanish
    await db.connect()
    logger.info("✅ Database connected")

    # Ownerni admin sifatida qo'shish (agar yo'q bo'lsa)
    await db.add_admin(
        user_id=OWNER_ID,
        added_by=OWNER_ID,
        is_owner=True
    )
    logger.info(f"✅ Owner configured: {OWNER_ID}")

    # Bot ma'lumotlarini olish
    try:
        bot_info = await dispatcher.bot.get_me()
        logger.info(f"✅ Bot: @{bot_info.username} (ID: {bot_info.id})")
    except Exception as e:
        logger.error(f"Cannot get bot info: {e}")
        return

    # Set commands
    try:
        commands = [
            types.BotCommand(command="start", description="Botni boshlash"),
            types.BotCommand(command="help", description="Yordam"),
            types.BotCommand(command="panel", description="Admin panel"),
            types.BotCommand(command="stats", description="Statistika"),
        ]
        await dispatcher.bot.set_my_commands(commands)
        logger.info("✅ Commands set")
    except Exception as e:
        logger.error(f"Cannot set commands: {e}")

    # Send startup notification to owner
    try:
        from utils.language import get_text
        from utils.security import SecurityLogger
        start_lang = await db.get_bot_language()
        await dispatcher.bot.send_message(
            chat_id=OWNER_ID,
            text=get_text('startup_message', start_lang, owner_id=OWNER_ID),
            parse_mode='HTML'
        )
        logger.info(f"✅ Startup notification sent to owner {OWNER_ID}")
        SecurityLogger.log_security_event('BOT_STARTUP', OWNER_ID, 'Bot started successfully')
    except Exception as e:
        logger.error(f"Cannot send startup notification: {e}")

    logger.info("=" * 60)
    logger.info("🚀 Bot muvaffaqiyatli ishga tushdi!")
    logger.info("🔒 Security systems enabled")
    logger.info("=" * 60)


async def on_shutdown(dispatcher):
    """Bot to'xtaganda"""
    logger.info("=" * 60)
    logger.info("🛑 Bot to'xtatilmoqda...")
    logger.info("=" * 60)

    # Bazani yopish
    await db.close()
    logger.info("✅ Database closed")

    logger.info("👋 Xayr!")


def setup_handlers(dp):
    """Handler va middlewarelarni sozlash"""
    from handlers.start_handler import router as start_r
    start_r(dp)
    from handlers.verification_handler import router as ver_r
    ver_r(dp)
    from handlers.admin_handler import router as admin_r
    admin_r(dp)
    from handlers.group_handler import router as group_r
    group_r(dp)
    from middlewares import setup_group_middleware, setup_admin_middleware
    setup_group_middleware(dp)
    setup_admin_middleware(dp)


async def run_webhook(bot, dp):
    """Webhook rejimida ishga tushirish with security"""
    from aiohttp import web
    from utils.security import WebhookSecurity, SecurityLogger

    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')
    WEBHOOK_PATH = '/' + BOT_TOKEN
    WEBHOOK_HOST = os.environ.get('RENDER_EXTERNAL_URL', WEBHOOK_URL).rstrip('/')
    PORT = int(os.environ.get('PORT', 8080))

    if not WEBHOOK_HOST:
        print("❌ WEBHOOK_URL environment variable not set!")
        return

    await on_startup(dp)
    await bot.set_webhook(url=WEBHOOK_HOST + WEBHOOK_PATH)

    app = web.Application()
    
    async def webhook_handler(request):
        try:
            # Security: Get signature from headers
            signature = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
            
            # Read payload
            json_data = await request.json()
            payload_bytes = str(json_data).encode('utf-8')
            
            # Security: Validate signature
            if not WebhookSecurity.validate_signature(payload_bytes, signature):
                SecurityLogger.log_security_event('WEBHOOK_SIGNATURE_INVALID', 0, 'Invalid webhook signature')
                logger.warning("⚠️ Invalid webhook signature!")
                return web.Response(status=403, text='Forbidden')
            
            # Process update
            update = types.Update(**json_data)
            await dp.process_update(update)
            
            SecurityLogger.log_security_event('WEBHOOK_SUCCESS', 0, f'Update ID: {update.update_id}')
            return web.Response(status=200, text='ok')
            
        except Exception as e:
            SecurityLogger.log_security_event('WEBHOOK_ERROR', 0, str(e))
            logger.error(f"Webhook error: {e}")
            return web.Response(status=500)

    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"✅ Webhook started on port {PORT}")
    logger.info(f"✅ Webhook URL: {WEBHOOK_HOST}{WEBHOOK_PATH}")
    logger.info(f"✅ Webhook security enabled")

    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        await bot.delete_webhook()
        await on_shutdown(dp)
        await runner.cleanup()


def main():
    """Asosiy funksiya with enhanced error handling"""

    try:
        # Token tekshirish
        if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            print("❌ XATOLIK: Bot tokeni kiritilmagan!")
            print(".env faylida BOT_TOKEN ni o'zgartiring.")
            print("\nTokenni @BotFather dan olishingiz mumkin.")
            return

        if OWNER_ID == 123456789:
            print("⚠️ OGOHLANTIRISH: OWNER_ID o'zgartirilmagan!")
            print(".env faylida o'zingizning Telegram ID raqamingizni kiriting.")
            print("\nID raqamni @userinfobot dan olishingiz mumkin.")

        # Bot va Dispatcher yaratish
        try:
            bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
        except Exception as e:
            print(f"❌ Bot yaratishda xatolik: {e}")
            logger.error(f"Bot creation failed: {e}")
            return

        storage = MemoryStorage()
        dp = Dispatcher(bot, storage=storage)
        setup_handlers(dp)

        # WEBHOOK_URL o'zgaruvchisi bor bo'lsa - webhook, aks holda polling
        webhook_url = os.environ.get('WEBHOOK_URL') or os.environ.get('RENDER_EXTERNAL_URL')
        if webhook_url:
            os.environ['WEBHOOK_URL'] = webhook_url
            logger.info("🌐 Webhook mode enabled")
            asyncio.get_event_loop().run_until_complete(run_webhook(bot, dp))
        else:
            logger.info("📡 Polling mode enabled")
            executor.start_polling(
                dp,
                skip_updates=True,
                on_startup=on_startup,
                on_shutdown=on_shutdown
            )
    
    except KeyboardInterrupt:
        print("\n\n👋 Bot to'xtatildi (Ctrl+C)")
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\n❌ Kutilmagan xatolik: {e}")
        logger.error(f"Unexpected error in main: {e}")
        from utils.security import SecurityLogger
        SecurityLogger.log_security_event('CRITICAL_ERROR', 0, str(e))


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    # Python 3.14+ uchun event loop yaratish
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bot to'xtatildi (Ctrl+C)")
    except Exception as e:
        print(f"\n\n❌ Kutilmagan xatolik: {e}")
