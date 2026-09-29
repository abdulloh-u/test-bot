from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.database import AsyncSessionLocal
from database.crud import get_or_create_user, get_user_rank, get_user_stats
from keyboards.main import back_to_main_keyboard

router = Router()

@router.callback_query(F.data == "profile")
async def cb_profile(call: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(session, call.from_user.id, call.from_user.full_name)
        rank = await get_user_rank(session, user.id)
        stats = await get_user_stats(session, user.id)
    
    text = (
        f"👤 **PROFIL**\n\n"
        f"👤 Ism: {user.full_name}\n"
        f"🎖 Level: {user.level}\n"
        f"⚡ XP: {user.xp}\n"
        f"🏆 Reyting: #{rank}\n"
        f"🔥 Streak: {user.streak} kun\n"
        f"🧠 Ishlangan testlar: {stats['tests']}\n"
        f"✅ To‘g‘ri javoblar: {stats['correct']}"
    )
    await call.message.edit_text(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "stats")
async def cb_stats(call: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(session, call.from_user.id, call.from_user.full_name)
        stats = await get_user_stats(session, user.id)

    total = stats['correct'] + stats['wrong']
    acc = int((stats['correct'] / total) * 100) if total > 0 else 0

    text = (
        f"📊 **STATISTIKA**\n\n"
        f"📈 Umumiy aniklik: {acc}%\n"
        f"✅ To'g'ri: {stats['correct']}\n"
        f"❌ Xato: {stats['wrong']}\n"
        f"🧠 Jami urinishlar: {stats['tests']}"
    )
    await call.message.edit_text(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")