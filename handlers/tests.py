from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.database import AsyncSessionLocal
from database.crud import get_all_categories, get_category_by_id
from keyboards.tests import categories_keyboard, difficulty_keyboard

router = Router()

@router.callback_query(F.data == "start_tests")
async def cb_start_tests(call: CallbackQuery):
    async with AsyncSessionLocal() as session:
        cats = await get_all_categories(session)
    
    text = "📚 **TEST YO'NALISHINI TANLANG:**\n\nO'zingiz qiziqqan sohaga oid testlarni ishlang:"
    await call.message.edit_text(text, reply_markup=categories_keyboard(cats), parse_mode="Markdown")

@router.callback_query(F.data.startswith("cat_"))
async def cb_category_select(call: CallbackQuery):
    cat_id = int(call.data.split("_")[1])
    async with AsyncSessionLocal() as session:
        category = await get_category_by_id(session, cat_id)
    
    text = f"{category.emoji} **{category.name.upper()} TEST**\n\nO'zingizga mos qiyinchilik darajasini tanlang:"
    await call.message.edit_text(text, reply_markup=difficulty_keyboard(cat_id), parse_mode="Markdown")