import time
import html
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.database import AsyncSessionLocal
from database.crud import (
    get_questions_by_difficulty, get_category_by_id, 
    get_or_create_user, update_user_streak, add_user_xp, save_result
)
from utils.quiz import QUIZ_SESSIONS, QuizSession
from utils.helpers import DIFFICULTY_XP, DIFFICULTY_LABELS
from keyboards.tests import quiz_answers_keyboard, quiz_next_keyboard, quiz_finish_keyboard
from handlers.tests import cb_start_tests

router = Router()

@router.callback_query(F.data.startswith("diff_"))
async def cb_start_quiz(call: CallbackQuery):
    parts = call.data.split("_")
    cat_id = int(parts[1])
    diff = parts[2]
    
    async with AsyncSessionLocal() as session:
        category = await get_category_by_id(session, cat_id)
        questions = await get_questions_by_difficulty(session, cat_id, diff, limit=10)
    
    if not questions:
        await call.answer("⚠️ Ushbu bo'limda hozircha savollar yo'q!", show_alert=True)
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
    
    QUIZ_SESSIONS[call.from_user.id] = QuizSession(
        category_id=cat_id,
        category_name=category.name,
        difficulty=diff,
        questions=q_list,
        start_time=time.time()
    )
    
    await send_quiz_question(call)

async def send_quiz_question(call: CallbackQuery):
    session_data = QUIZ_SESSIONS.get(call.from_user.id)
    if not session_data or session_data.current_index >= len(session_data.questions):
        return
        
    q = session_data.questions[session_data.current_index]
    
    cat_name = html.escape(session_data.category_name)
    q_text = html.escape(q['question'])
    diff_label = DIFFICULTY_LABELS.get(session_data.difficulty, session_data.difficulty)

    text = (
        f"<b>{cat_name} — {diff_label}</b>\n\n"
        f"❓ <b>Savol:</b> {q_text}\n\n"
        f"⏱ Vaqt: 15 sekund\n"
        f"📊 Savol: {session_data.current_index + 1}/{len(session_data.questions)}\n"
        f"⭐ Ball: {session_data.score}"
    )
    
    await call.message.edit_text(
        text, 
        reply_markup=quiz_answers_keyboard(q['a'], q['b'], q['c'], q['d']),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("ans_"))
async def cb_answer_quiz(call: CallbackQuery):
    user_ans = call.data.split("_")[1]
    session_data = QUIZ_SESSIONS.get(call.from_user.id)
    
    if not session_data:
        await call.answer("Test sessiyasi topilmadi.", show_alert=True)
        return

    q = session_data.questions[session_data.current_index]
    is_correct = (user_ans == q['correct'])
    
    if is_correct:
        session_data.correct_count += 1
        xp_gained = DIFFICULTY_XP[session_data.difficulty]
        session_data.score += 100
        session_data.total_xp += xp_gained
        feedback = "✅ <b>To‘g‘ri!</b>"
    else:
        session_data.wrong_count += 1
        expl = html.escape(q['expl'] or "Izoh berilmagan.")
        feedback = f"❌ <b>Noto‘g‘ri!</b>\n\n💡 <b>Tushuntirish:</b> {expl}"
    
    await call.message.edit_text(
        f"{feedback}\n\nKeyingi savolga o'tish uchun bosing:",
        reply_markup=quiz_next_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "next_question")
async def cb_next_question(call: CallbackQuery):
    session_data = QUIZ_SESSIONS.get(call.from_user.id)
    if not session_data:
        await cb_start_tests(call)
        return
        
    session_data.current_index += 1
    if session_data.current_index >= len(session_data.questions):
        await finish_quiz(call)
    else:
        await send_quiz_question(call)

async def finish_quiz(call: CallbackQuery):
    session_data = QUIZ_SESSIONS.get(call.from_user.id)
    if not session_data:
        await cb_start_tests(call)
        return

    elapsed_seconds = int(time.time() - session_data.start_time)
    minutes, seconds = divmod(elapsed_seconds, 60)
    time_str = f"{minutes:02d}:{seconds:02d}"
    
    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(
            session, 
            user_id=call.from_user.id, 
            username=call.from_user.username, 
            full_name=call.from_user.full_name
        )
        await update_user_streak(session, user)
        await add_user_xp(session, user, session_data.total_xp)
        await save_result(
            session, 
            user_id=user.id, 
            category_id=session_data.category_id, 
            correct=session_data.correct_count, 
            wrong=session_data.wrong_count, 
            score=session_data.score, 
            xp=session_data.total_xp
        )

    cat_name = html.escape(session_data.category_name)
    diff_label = DIFFICULTY_LABELS.get(session_data.difficulty, session_data.difficulty)

    text = (
        f"🏆 <b>TEST YAKUNI</b>\n\n"
        f"💻 {cat_name} — {diff_label}\n"
        f"✅ To‘g‘ri: {session_data.correct_count}\n"
        f"❌ Noto‘g‘ri: {session_data.wrong_count}\n"
        f"⭐ Ball: {session_data.score}\n"
        f"⚡ To'plangan XP: +{session_data.total_xp}\n"
        f"⏱ Vaqt: {time_str}\n\n"
        f"Natija: 🔥 <b>Juda yaxshi!</b>"
    )
    
    QUIZ_SESSIONS.pop(call.from_user.id, None)
    await call.message.edit_text(text, reply_markup=quiz_finish_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "retry_quiz")
async def cb_retry_quiz(call: CallbackQuery):
    await cb_start_tests(call)

@router.callback_query(F.data == "cancel_quiz")
async def cb_cancel_quiz(call: CallbackQuery):
    QUIZ_SESSIONS.pop(call.from_user.id, None)
    await call.answer("Test bekor qilindi.")
    await cb_start_tests(call)