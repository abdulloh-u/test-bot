import uuid
import time
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.database import AsyncSessionLocal
from database.crud import get_daily_questions, get_or_create_user, add_user_xp
from utils.quiz import BATTLE_QUEUE, BATTLE_ROOMS, USER_BATTLE_ROOM, BattleRoom
from keyboards.main import back_to_main_keyboard

router = Router()

def battle_answers_keyboard(option_a: str, option_b: str, option_c: str, option_d: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"A) {option_a}", callback_data="btl_ans_A")],
        [InlineKeyboardButton(text=f"B) {option_b}", callback_data="btl_ans_B")],
        [InlineKeyboardButton(text=f"C) {option_c}", callback_data="btl_ans_C")],
        [InlineKeyboardButton(text=f"D) {option_d}", callback_data="btl_ans_D")]
    ])

@router.callback_query(F.data == "start_battle")
async def cb_start_battle(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id

    if user_id in USER_BATTLE_ROOM:
        await call.answer("Siz allaqachon faol duel xonasidasiz!", show_alert=True)
        return

    if user_id in BATTLE_QUEUE:
        await call.answer("Siz allaqachon raqib qidiryapsiz...", show_alert=True)
        return

    # Navbatda raqib bormi?
    if BATTLE_QUEUE and BATTLE_QUEUE[0] != user_id:
        opponent_id = BATTLE_QUEUE.pop(0)
        room_id = str(uuid.uuid4())

        async with AsyncSessionLocal() as session:
            questions_db = await get_daily_questions(session, limit=5)

        q_list = []
        for q in questions_db:
            q_list.append({
                "question": q.question,
                "a": q.option_a,
                "b": q.option_b,
                "c": q.option_c,
                "d": q.option_d,
                "correct": q.correct_answer
            })

        room = BattleRoom(
            room_id=room_id,
            player1_id=opponent_id,
            player2_id=user_id,
            questions=q_list
        )

        BATTLE_ROOMS[room_id] = room
        USER_BATTLE_ROOM[opponent_id] = room_id
        USER_BATTLE_ROOM[user_id] = room_id

        # Har ikki o'yinchiga o'yin boshlanganini ma'lum qilish
        for p_id in [opponent_id, user_id]:
            q = q_list[0]
            text = (
                f"⚔️ **1v1 DUEL BOSHLANDI!**\n\n"
                f"❓ **Savol 1/5:** {q['question']}"
            )
            try:
                await bot.send_message(
                    chat_id=p_id,
                    text=text,
                    reply_markup=battle_answers_keyboard(q['a'], q['b'], q['c'], q['d']),
                    parse_mode="Markdown"
                )
            except Exception:
                pass
        
        await call.answer()
    else:
        BATTLE_QUEUE.append(user_id)
        text = (
            "🔍 **Raqib izlanmoqda...**\n\n"
            "Mos raqib topilganda duel avtosohada boshlanadi. Bosh menyuga qaytish uchun tugmani bosing."
        )
        cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Navbatdan chiqish", callback_data="cancel_battle_search")]
        ])
        await call.message.edit_text(text, reply_markup=cancel_kb, parse_mode="Markdown")

@router.callback_query(F.data == "cancel_battle_search")
async def cb_cancel_battle_search(call: CallbackQuery):
    user_id = call.from_user.id
    if user_id in BATTLE_QUEUE:
        BATTLE_QUEUE.remove(user_id)
    await call.message.edit_text("❌ Raqib qidirish bekor qilindi.", reply_markup=back_to_main_keyboard())

@router.callback_query(F.data.startswith("btl_ans_"))
async def cb_battle_answer(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    user_ans = call.data.split("_")[2]

    room_id = USER_BATTLE_ROOM.get(user_id)
    if not room_id or room_id not in BATTLE_ROOMS:
        await call.answer("O'yin xonasi topilmadi.", show_alert=True)
        return

    room = BATTLE_ROOMS[room_id]
    current_q = room.questions[room.current_question_idx]

    is_correct = (user_ans == current_q['correct'])
    if is_correct:
        if user_id == room.player1_id:
            room.player1_score += 100
        else:
            room.player2_score += 100

    room.current_question_idx += 1

    if room.current_question_idx >= len(room.questions):
        # O'yinchi savollarni tugatdi
        if user_id == room.player1_id:
            room.player1_finished = True
        else:
            room.player2_finished = True

        await call.message.edit_text("⏳ **Siz savollarni tugatdingiz!** Raqibingiz natijasi kutilmoqda...", parse_mode="Markdown")

        # Har ikki o'yinchi tugatgan bo'lsa
        if room.player1_finished and room.player2_finished:
            await finalize_battle(room, bot)
    else:
        q = room.questions[room.current_question_idx]
        text = (
            f"⚔️ **1v1 DUEL**\n\n"
            f"❓ **Savol {room.current_question_idx + 1}/5:** {q['question']}"
        )
        await call.message.edit_text(
            text,
            reply_markup=battle_answers_keyboard(q['a'], q['b'], q['c'], q['d']),
            parse_mode="Markdown"
        )

async def finalize_battle(room: BattleRoom, bot: Bot):
    p1 = room.player1_id
    p2 = room.player2_id
    s1 = room.player1_score
    s2 = room.player2_score

    winner_text = ""
    if s1 > s2:
        winner_id = p1
        winner_text = f"🥇 Player 1 g'alaba qozondi! ({s1} vs {s2})"
    elif s2 > s1:
        winner_id = p2
        winner_text = f"🥇 Player 2 g'alaba qozondi! ({s2} vs {s1})"
    else:
        winner_id = None
        winner_text = f"🤝 **DANGSIT NAKRO (DURANG)!** ({s1} vs {s2})"

    async with AsyncSessionLocal() as session:
        if winner_id:
            u = await get_or_create_user(session, winner_id, "User")
            await add_user_xp(session, u, 300) # G'olibga +300 XP

    msg = (
        f"🏆 **DUEL YAKUNLANDI!**\n\n"
        f"{winner_text}\n\n"
        f"⚡ G'olib +300 XP ega bo'ldi!"
    )

    for pid in [p1, p2]:
        try:
            await bot.send_message(chat_id=pid, text=msg, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")
        except Exception:
            pass

    # Xonani tozalash
    USER_BATTLE_ROOM.pop(p1, None)
    USER_BATTLE_ROOM.pop(p2, None)
    BATTLE_ROOMS.pop(room.room_id, None)