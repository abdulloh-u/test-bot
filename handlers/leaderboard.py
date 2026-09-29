from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.database import AsyncSessionLocal
from database.crud import get_top_players, get_user_rank, get_or_create_user
from keyboards.main import back_to_main_keyboard

router = Router()

@router.callback_query(F.data == "leaderboard")
async def cb_leaderboard(call: CallbackQuery):
    async with AsyncSessionLocal() as session:
        top_users = await get_top_players(session, limit=10)
        curr_user = await get_or_create_user(session, call.from_user.id, call.from_user.full_name)
        rank = await get_user_rank(session, curr_user.id)

    text = "🏆 **TOP PLAYERS**\n\n"
    medals = ["🥇", "🥈", "🥉"]
    
    for idx, u in enumerate(top_users):
        icon = medals[idx] if idx < 3 else f"#{idx+1}"
        text += f"{icon} {u.full_name} — {u.xp} XP\n"
        
    text += f"\n--------------------\n📍 Sizning pozitsiyangiz: #{rank} ({curr_user.xp} XP)"
    await call.message.edit_text(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")