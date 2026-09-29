from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from database.database import AsyncSessionLocal
from database.crud import get_or_create_user, add_referral, get_user_referrals_count, add_user_xp
from keyboards.main import main_menu_keyboard, referral_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject, bot: Bot):
    await state.clear()

    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    async with AsyncSessionLocal() as session:
        # Foydalanuvchini bazaga qo'shamiz yoki olamiz
        user = await get_or_create_user(session, user_id=user_id, username=username, full_name=full_name)
        
        # Referral havola orqali kirganligini tekshiramiz
        referrer_arg = command.args
        if referrer_arg and referrer_arg.isdigit():
            referrer_id = int(referrer_arg)
            added, total_refs = await add_referral(session, referrer_id=referrer_id, referee_id=user_id)
            
            if added:
                # Har 3 ta do'st uchun +100 XP beramiz
                if total_refs % 3 == 0:
                    await add_user_xp(session, referrer_id, 100)
                    try:
                        await bot.send_message(
                            chat_id=referrer_id,
                            text=(
                                f"🎉 <b>TABRIKLAYMIZ!</b>\n\n"
                                f"Siz jami <b>{total_refs} ta</b> do'stingizni taklif qildingiz!\n"
                                f"🎁 Sizga navbatdagi <b>+100 XP</b> taqdim etildi!"
                            ),
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
                else:
                    needed = 3 - (total_refs % 3)
                    try:
                        await bot.send_message(
                            chat_id=referrer_id,
                            text=(
                                f"👤 Sizning havolangiz orqali <b>{full_name}</b> botga qo'shildi!\n"
                                f"📊 Jami takliflaringiz: <b>{total_refs} ta</b>.\n"
                                f"⚡ Yana <b>{needed} ta</b> do'stingiz qo'shilsa, sizga <b>+100 XP</b> beriladi!"
                            ),
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass

    text = (
        f"👋 <b>Assalomu alaykum, {full_name}!</b>\n\n"
        "🤖 <b>Test uz bot</b>ga xush kelibsiz!\n"
        "Bilimingizni sinash va do'stlaringiz bilan bellashish uchun quyidagi bo'limlardan birini tanlang:"
    )

    await message.answer(
        text,
        reply_markup=main_menu_keyboard(user_id=user_id, admin_id=ADMIN_ID),
        parse_mode="HTML"
    )

# Referral Bo'limi (Do'stlarni taklif qilish oynasi)
@router.callback_query(F.data == "referral")
async def cb_referral(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    bot_info = await bot.get_me()
    
    # Foydalanuvchining shaxsiy taklif havolasi
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"

    async with AsyncSessionLocal() as session:
        count = await get_user_referrals_count(session, user_id)

    needed = 3 - (count % 3) if count % 3 != 0 else 3
    earned_xp = (count // 3) * 100

    text = (
        f"👥 <b>DO'STLARNI TAKLIF QILISH</b>\n\n"
        f"🎁 Har <b>3 ta</b> taklif qilingan do'stingiz uchun <b>+100 XP</b> oling!\n\n"
        f"📊 Siz taklif qilgan do'stlar: <b>{count} ta</b>\n"
        f"⚡ Keyingi mukofotgacha: <b>{needed} ta do'st</b>\n"
        f"💰 Referallardan ishlangan jami XP: <b>+{earned_xp} XP</b>\n\n"
        f"🔗 <b>Sizning taklif havolangiz:</b>\n<code>{ref_link}</code>\n\n"
        f"Pastdagi tugmani bosib, havolani do'stlaringiz va guruhlarga yuboring 👇"
    )

    await call.message.edit_text(
        text,
        reply_markup=referral_keyboard(ref_link),
        parse_mode="HTML"
    )

@router.message(Command("cancel"))
@router.callback_query(F.data == "main_menu")
async def cb_main_menu(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = event.from_user.id
    text = "🏠 <b>Bosh menyu</b>\n\nKerakli bo'limni tanlang:"
    kb = main_menu_keyboard(user_id=user_id, admin_id=ADMIN_ID)

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb, parse_mode="HTML")