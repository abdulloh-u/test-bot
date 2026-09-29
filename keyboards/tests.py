from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.helpers import DIFFICULTY_LABELS

def categories_keyboard(categories) -> InlineKeyboardMarkup:
    keyboard = []
    row = []
    for cat in categories:
        row.append(InlineKeyboardButton(text=f"{cat.emoji} {cat.name}", callback_data=f"cat_{cat.id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def difficulty_keyboard(cat_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=DIFFICULTY_LABELS["oson"], callback_data=f"diff_{cat_id}_oson")],
        [InlineKeyboardButton(text=DIFFICULTY_LABELS["orta"], callback_data=f"diff_{cat_id}_orta")],
        [InlineKeyboardButton(text=DIFFICULTY_LABELS["qiyin"], callback_data=f"diff_{cat_id}_qiyin")],
        [InlineKeyboardButton(text=DIFFICULTY_LABELS["expert"], callback_data=f"diff_{cat_id}_expert")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="start_tests")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def quiz_answers_keyboard(option_a: str, option_b: str, option_c: str, option_d: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=f"A) {option_a}", callback_data="ans_A")],
        [InlineKeyboardButton(text=f"B) {option_b}", callback_data="ans_B")],
        [InlineKeyboardButton(text=f"C) {option_c}", callback_data="ans_C")],
        [InlineKeyboardButton(text=f"D) {option_d}", callback_data="ans_D")],
        [InlineKeyboardButton(text="❌ Testni to'xtatish", callback_data="cancel_quiz")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def quiz_next_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ KEYINGI SAVOL", callback_data="next_question")]
    ])

def quiz_finish_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Qayta ishlash", callback_data="retry_quiz")],
        [InlineKeyboardButton(text="📚 Boshqa test", callback_data="start_tests")],
        [InlineKeyboardButton(text="🏆 Reyting", callback_data="leaderboard")],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")]
    ])


def admin_categories_keyboard(categories) -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        # Admin uchun alohida prefix: admincat_
        buttons.append([InlineKeyboardButton(text=f"{cat.icon} {cat.name}", callback_data=f"admincat_{cat.id}")])
    
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)