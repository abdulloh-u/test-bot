from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Savol qo'shish", callback_data="admin_add_q")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Broadcast (Xabar yuborish)", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")]
    ])

# Admin uchun alohida kategoriyalar menyusi (admincat_ prefiksi bilan):
def admin_categories_keyboard(categories) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for cat in categories:
        emoji = getattr(cat, 'emoji', '📝')
        row.append(InlineKeyboardButton(text=f"{emoji} {cat.name}", callback_data=f"admincat_{cat.id}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Admin uchun alohida daraja tugmalari (admindiff_ prefiksi bilan):
def difficulty_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 Oson", callback_data="admindiff_oson"),
            InlineKeyboardButton(text="🟡 O'rta", callback_data="admindiff_orta")
        ],
        [
            InlineKeyboardButton(text="🔴 Qiyin", callback_data="admindiff_qiyin"),
            InlineKeyboardButton(text="💀 Expert", callback_data="admindiff_expert")
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel")]
    ])

def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel")]
    ])