import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from sqlalchemy.future import select

from config import BOT_TOKEN
from database.database import init_db, AsyncSessionLocal
from database.crud import seed_categories
from database.models import Question
from utils.seed_data import seed_all_questions

# Handler va Error Handlerni import qilish
from handlers import start, tests, quiz, profile, leaderboard, admin, daily, battle
from utils.error_handler import router as error_router 

logging.basicConfig(level=logging.INFO)

# --- Render port xatosini bartaraf etish uchun Soxta Web Server ---
async def handle(request):
    return web.Response(text="Bot is running smoothly!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render bergan PORTni oladi, topilmasa 8080 ishlatadi
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"🌐 Fake Web Server {port}-portda ishga tushdi.")
# ------------------------------------------------------------------

async def main():
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_categories(session)
        
        stmt = select(Question)
        res = await session.execute(stmt)
        if not res.scalars().all():
            print("📦 Savollar bazasi bo'sh! Savollar avtomatik yuklanmoqda...")
            await seed_all_questions()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Error router va barcha handler routerlarini biriktirish
    dp.include_router(error_router)
    
    # Handlerlarni ro'yxatga olish
    dp.include_routers(
        admin.router,
        start.router,
        tests.router,
        quiz.router,
        daily.router,
        battle.router,
        profile.router,
        leaderboard.router
    )

    # Render xatosini yo'qotish uchun fon rejimida HTTP serverni ishga tushiramiz
    asyncio.create_task(start_web_server())

    print("🚀 BOT MUVAFFAQIYATLI ISHGA TUSHDI!")
    
    # Eski to'planib qolgan xabarlarni tozalaymiz va boshqa ulanishlarni uzamiz
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi.")