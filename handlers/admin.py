import asyncio
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from keyboards.admin import admin_panel_keyboard, cancel_keyboard, difficulty_keyboard, admin_categories_keyboard
from database.database import AsyncSessionLocal
from database.crud import get_all_categories, add_question, get_admin_stats, get_all_user_ids
from states.admin_states import AddQuestionFSM, BroadcastFSM

router = Router()

# Bekor qilish
@router.callback_query(F.data == "admin_cancel")
@router.message(Command("cancel"))
async def cancel_handler(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    text = "❌ Jarayon bekor qilindi."
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=admin_panel_keyboard())
        await event.answer()
    else:
        await event.answer(text, reply_markup=admin_panel_keyboard())

# Admin Panel Menyu
@router.message(Command("admin"))
@router.callback_query(F.data == "admin_panel")
async def cb_admin_panel(event: Message | CallbackQuery, state: FSMContext):
    user_id = event.from_user.id
    if user_id != ADMIN_ID:
        if isinstance(event, CallbackQuery):
            await event.answer("⚠️ Kechirasiz, siz admin emassiz!", show_alert=True)
        else:
            await event.answer(f"⚠️ Siz admin emassiz! Sizning Telegram ID: {user_id}")
        return

    await state.clear()
    text = "👑 **ADMIN PANEL**\n\nKerakli amalni tanlang:"
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=admin_panel_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=admin_panel_keyboard(), parse_mode="Markdown")

# 1. Kategoriya tanlash (admin_categories_keyboard bilan)
@router.callback_query(F.data == "admin_add_q")
async def cb_admin_add_q(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat berilmadi!", show_alert=True)
        return
        
    async with AsyncSessionLocal() as session:
        cats = await get_all_categories(session)
    
    await state.set_state(AddQuestionFSM.category)
    await call.message.edit_text(
        "📚 **Savol qo'shish uchun kategoriya tanlang:**", 
        reply_markup=admin_categories_keyboard(cats), 
        parse_mode="Markdown"
    )
    await call.answer()

# 2. Qiyinchilik darajasini tanlash (admincat_ orqali)
@router.callback_query(AddQuestionFSM.category, F.data.startswith("admincat_"))
async def process_cat(call: CallbackQuery, state: FSMContext):
    cat_id = int(call.data.split("_")[1])
    await state.update_data(cat_id=cat_id)
    await state.set_state(AddQuestionFSM.difficulty)
    await call.message.edit_text(
        "🎯 **Qiyinchilik darajasini tanlang:**",
        reply_markup=difficulty_keyboard(),
        parse_mode="Markdown"
    )
    await call.answer()

# 3. Daraja tanlangach -> Savol matnini so'rash (admindiff_ orqali)
@router.callback_query(AddQuestionFSM.difficulty, F.data.startswith("admindiff_"))
async def process_diff_btn(call: CallbackQuery, state: FSMContext):
    diff = call.data.split("_")[1]
    await state.update_data(difficulty=diff)
    await state.set_state(AddQuestionFSM.question)
    await call.message.edit_text(
        "❓ **Savol matnini yozib yuboring:**",
        reply_markup=cancel_keyboard()
    )
    await call.answer()

# 4. Savol matni qabul qilindi -> 4 ta variant so'rash
@router.message(AddQuestionFSM.question)
async def process_q_text(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Iltimos, matn ko'rinishida yuboring.")
        return
    await state.update_data(question=message.text)
    await state.set_state(AddQuestionFSM.options)
    await message.answer(
        "📝 **Variantlarni 4 qatorda yuboring:**\n\n"
        "Masalan:\n"
        "Toshkent\n"
        "Samarqand\n"
        "Buxoro\n"
        "Xiva",
        reply_markup=cancel_keyboard()
    )

# 5. Variantlar qabul qilindi -> To'g'ri javobni so'rash
@router.message(AddQuestionFSM.options)
async def process_options(message: Message, state: FSMContext):
    lines = [line.strip() for line in message.text.strip().split("\n") if line.strip()]
    if len(lines) != 4:
        await message.answer(
            f"⚠️ Siz {len(lines)} ta variant kiritdingiz!\n"
            "Iltimos, roppa-rosa 4 ta variantni bitta xabarda har birini yangi qatordan yuboring:", 
            reply_markup=cancel_keyboard()
        )
        return
        
    await state.update_data(a=lines[0], b=lines[1], c=lines[2], d=lines[3])
    await state.set_state(AddQuestionFSM.correct)
    await message.answer(
        f"Variantlar qabul qilindi:\nA) {lines[0]}\nB) {lines[1]}\nC) {lines[2]}\nD) {lines[3]}\n\n"
        "✅ **To'g'ri javob harfini yuboring (A, B, C yoki D):**", 
        reply_markup=cancel_keyboard()
    )

# 6. To'g'ri javob qabul qilindi -> Izohni so'rash
@router.message(AddQuestionFSM.correct)
async def process_correct(message: Message, state: FSMContext):
    ans = message.text.upper().strip()
    if ans not in ["A", "B", "C", "D"]:
        await message.answer("⚠️ Faqat A, B, C yoki D harfini yuboring:", reply_markup=cancel_keyboard())
        return
        
    await state.update_data(correct=ans)
    await state.set_state(AddQuestionFSM.explanation)
    await message.answer("💡 **Savol izohini yuboring (izoh bo'lmasa '-' deb yozing):**", reply_markup=cancel_keyboard())

# 7. Izoh qabul qilindi -> Bazaga saqlash
@router.message(AddQuestionFSM.explanation)
async def process_explanation(message: Message, state: FSMContext):
    expl = message.text if message.text != "-" else ""
    data = await state.get_data()
    
    async with AsyncSessionLocal() as session:
        await add_question(
            session=session,
            cat_id=data['cat_id'],
            difficulty=data['difficulty'],
            q_text=data['question'],
            a=data['a'],
            b=data['b'],
            c=data['c'],
            d=data['d'],
            correct=data['correct'],
            expl=expl
        )
    
    await state.clear()
    await message.answer("🎉 **Savol muvaffaqiyatli saqlandi!**", reply_markup=admin_panel_keyboard())

# 8. Admin Statistika
@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    async with AsyncSessionLocal() as session:
        users_count, questions_count = await get_admin_stats(session)
    
    text = (
        f"📊 **BOT STATISTIKASI**\n\n"
        f"👥 Foydalanuvchilar: {users_count} ta\n"
        f"❓ Jami savollar: {questions_count} ta"
    )
    await call.message.edit_text(text, reply_markup=admin_panel_keyboard(), parse_mode="Markdown")

# 9. Admin Broadcast
@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await state.set_state(BroadcastFSM.message)
    await call.message.edit_text(
        "📢 **Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yozing:**",
        reply_markup=cancel_keyboard()
    )

@router.message(BroadcastFSM.message)
async def process_broadcast_message(message: Message, state: FSMContext, bot: Bot):
    async with AsyncSessionLocal() as session:
        user_ids = await get_all_user_ids(session)
    
    sent = 0
    for uid in user_ids:
        try:
            await bot.send_message(chat_id=uid, text=message.text)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
            
    await state.clear()
    await message.answer(f"✅ Xabar {sent} ta foydalanuvchiga yuborildi.", reply_markup=admin_panel_keyboard())