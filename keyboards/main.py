import urllib.parse
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard(user_id: int, admin_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🧠 TESTLAR", callback_data="start_tests")
        ],
        [
            InlineKeyboardButton(text="🌟 DAILY CHALLENGE", callback_data="daily_challenge"),
            InlineKeyboardButton(text="⚔️ 1v1 DUEL", callback_data="start_battle")
        ],
        [
            InlineKeyboardButton(text="🏆 REYTING", callback_data="leaderboard"),
            InlineKeyboardButton(text="👤 PROFIL", callback_data="profile")
        ],
        [
            InlineKeyboardButton(text="👥 DO'STLARNI TAKLIF QILISH (100 XP)", callback_data="referral")
        ],
        [
            InlineKeyboardButton(text="📊 STATISTIKA", callback_data="stats")
        ]
    ]
    
    if user_id == admin_id:
        buttons.append([InlineKeyboardButton(text="👑 ADMIN PANEL", callback_data="admin_panel")])
        
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def referral_keyboard(ref_link: str) -> InlineKeyboardMarkup:
    share_text = "🧠 Test uz botida o'z bilimingizni sinab ko'ring va eng yaxshilar qatoridan joy oling! Hoziroq qo'shiling 👇"
    share_url = f"https://t.me/share/url?url={urllib.parse.quote(ref_link)}&text={urllib.parse.quote(share_text)}"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↗️ Do'stlarga ulashish (Share)", url=share_url)],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")]
    ])


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")]
    ])