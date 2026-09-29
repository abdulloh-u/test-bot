import time
from datetime import date
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.database import AsyncSessionLocal
from database.crud import (
    get_or_create_user, check_daily_completion, get_daily_questions,
    update_user_streak, add_user_xp, mark_daily_completed, save_result
)
from utils.quiz import QUIZ_SESSIONS, QuizSession
from keyboards.tests import quiz_answers_keyboard, quiz_next_keyboard, quiz_finish_keyboard
from keyboards.main import back_to_main_keyboard

router = Router()

@router.callback_query(F.data == "daily_challenge")
async def cb_daily_challenge(call: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(session, call.from_user.id, call.from_user.full_name)
        is_completed = await check_daily_completion(user)

        if is_completed:
            text = (
                f"🌟 **BUGUNGI CHALLENGE TUGATILGAN!**\n\n"
                f"Siz bugungi testlarni muvaffaqiyatli topshirdingiz.\n"
                f"🔥 **Hozirgi streak:** {user.streak} kun\n\n"
                f"Ertaga yangi testlarni ishlash uchun qaytib keling!"
            )
            await call.message.edit_text(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")
            return

        questions = await get_daily_questions(session, limit=10)

        if len(questions) < 5:
            await call.answer("⚠️ Kunlik challenge uchun savollar yetarli emas. Admin savollar qo'shishi kerak!", show_alert=True)
            return

        q_list = []
        for q in questions:
            q_list.append({
                "id": q.id,
                "question": q.question,
                "a": q.option_a,
                "b": q.option_b,
                "c": q.option_c,
                "d": q.option_d,
                "correct": q.correct_answer,
                "expl": q.explanation
            })

        # Daily Challenge sessiyasini saqlash (category_id = 0 qilib belgilaymiz)
        QUIZ_SESSIONS[call.from_user.id] = QuizSession(
            category_id=0,
            category_name="🌟 Daily Challenge",
            difficulty="orta",
            questions=q_list,
            start_time=time.time()
        )

    await send_daily_question(call)

async def send_daily_question(call: CallbackQuery):
    session_data = QUIZ_SESSIONS.get(call.from_user.id)
    q = session_data.questions[session_data.current_index]

    text = (
        f"🌟 **DAILY CHALLENGE (2X XP)**\n\n"
        f"❓ **Savol:** {q['question']}\n\n"
        f"⏱ Vaqt: 15 sekund\n"
        f"📊 Savol: {session_data.current_index + 1}/{len(session_data.questions)}\n"
        f"⭐ Ball: {session_data.score}"
    )

    await call.message.edit_text(
        text,
        reply_markup=quiz_answers_keyboard(q['a'], q['b'], q['c'], q['d']),
        parse_mode="Markdown"
    )

# Note: Javob berish va keyingisiga o'tish logikasi quiz.py dagi kabi ishlaydi, 
# lekin yakunlanganda Daily Challenge belgisi qo'yiladi.

@router.callback_query(F.data == "finish_daily")
async def finish_daily_quiz(call: CallbackQuery):
    session_data = QUIZ_SESSIONS.get(call.from_user.id)
    if not session_data:
        return

    elapsed_seconds = int(time.time() - session_data.start_time)
    minutes, seconds = divmod(elapsed_seconds, 60)
    time_str = f"{minutes:02d}:{seconds:02d}"

    # Daily Challenge uchun 2 baravar ko'p XP beriladi
    double_xp = session_data.total_xp * 2

    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(session, call.from_user.id, call.from_user.full_name)
        await update_user_streak(session, user)
        await add_user_xp(session, user, double_xp)
        await mark_daily_completed(session, user)

    text = (
        f"🏆 **DAILY CHALLENGE YAKUNLANDI!**\n\n"
        f"✅ To‘g‘ri: {session_data.correct_count}\n"
        f"❌ Noto‘g‘ri: {session_data.wrong_count}\n"
        f"⭐ Ball: {session_data.score}\n"
        f"⚡ **To'plangan XP (2X): +{double_xp}**\n"
        f"⏱ Vaqt: {time_str}\n\n"
        f"🔥 **Streak oshdi!** Bugun ham faol bo'lganingiz uchun rahmat."
    )

    QUIZ_SESSIONS.pop(call.from_user.id, None)
    await call.message.edit_text(text, reply_markup=quiz_finish_keyboard(), parse_mode="Markdown")