import traceback
from aiogram import Router, Bot
from aiogram.types import ErrorEvent
from config import ADMIN_ID

router = Router()

@router.error()
async def global_error_handler(event: ErrorEvent, bot: Bot):
    """
    Botda yuz bergan barcha kutilmagan xatoliklarni ushlab qoladi 
    va adminga batafsil xabar yuboradi.
    """
    exception = event.exception
    update = event.update

    # User haqida ma'lumot olish (agar update ichida bo'lsa)
    user_info = "Noma'lum"
    if update.message and update.message.from_user:
        user = update.message.from_user
        user_info = f"@{user.username} (ID: {user.id})" if user.username else f"{user.full_name} (ID: {user.id})"
    elif update.callback_query and update.callback_query.from_user:
        user = update.callback_query.from_user
        user_info = f"@{user.username} (ID: {user.id})" if user.username else f"{user.full_name} (ID: {user.id})"

    # Full Stack Trace olish
    tb = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))

    # Adminga yuboriladigan xabar matni
    error_message = (
        f"🚨 **XATOLIK YUZ BERDI!**\n\n"
        f"👤 **Foydalanuvchi:** {user_info}\n"
        f"❌ **Xatolik turi:** `{type(exception).__name__}`\n"
        f"📝 **Tavsifi:** `{str(exception)}`\n\n"
        f"🔍 **Stack Trace:**\n"
        f"```python\n{tb[-1500:]}\n```"  # Telegram limitiga sig'ishi uchun oxirgi 1500 belgini olamiz
    )

    try:
        if ADMIN_ID:
            await bot.send_message(
                chat_id=ADMIN_ID, 
                text=error_message, 
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"Adminga xatolik yuborishda muammo bo'ldi: {e}")