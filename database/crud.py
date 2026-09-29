from datetime import datetime, date
from sqlalchemy.future import select
from sqlalchemy.sql import func
from database.models import User, Category, Question, Result, Referral

# ==========================================
# 1. FOYDALANUVCHILAR BILAN ISHLASH
# ==========================================
async def get_or_create_user(session, user_id: int = None, username: str = None, full_name: str = None, telegram_id: int = None):
    # Har ikkala nom (user_id yoki telegram_id) bilan chaqirilganda ham xatosiz ishlaydi
    tid = user_id or telegram_id
    stmt = select(User).filter(User.telegram_id == tid)
    result = await session.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        user = User(telegram_id=tid, username=username, full_name=full_name or "Foydalanuvchi")
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        updated = False
        if username and user.username != username:
            user.username = username
            updated = True
        if full_name and user.full_name != full_name:
            user.full_name = full_name
            updated = True
        if updated:
            await session.commit()
            await session.refresh(user)
    return user

async def get_user_by_id(session, user_id: int):
    stmt = select(User).filter(User.telegram_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()

async def add_user_xp(session, user_id, xp_amount: int):
    if isinstance(user_id, User):
        user = user_id
    else:
        user = await get_user_by_id(session, user_id)

    if user and hasattr(user, 'xp'):
        user.xp = (user.xp or 0) + xp_amount
        if hasattr(user, 'level'):
            user.level = max(1, (user.xp // 100) + 1)
        await session.commit()
        await session.refresh(user)
    return user

async def update_user_streak(session, user_id):
    if isinstance(user_id, User):
        user = user_id
    else:
        user = await get_user_by_id(session, user_id)

    if user and hasattr(user, 'streak'):
        user.streak = (user.streak or 0) + 1
        await session.commit()
        await session.refresh(user)
    return user


# ==========================================
# 2. KATEGORIYALAR BILAN ISHLASH
# ==========================================
async def get_all_categories(session):
    stmt = select(Category)
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_category_by_id(session, category_id: int):
    stmt = select(Category).filter(Category.id == category_id)
    result = await session.execute(stmt)
    return result.scalars().first()

async def seed_categories(session):
    try:
        from utils.seed_data import CATEGORIES
        for cat in CATEGORIES:
            stmt = select(Category).filter_by(id=cat["id"])
            result = await session.execute(stmt)
            if not result.scalars().first():
                session.add(Category(id=cat["id"], name=cat["name"], emoji=cat.get("icon", "📝")))
        await session.commit()
    except Exception as e:
        print(f"seed_categories xatosi: {e}")


# ==========================================
# 3. SAVOLLAR BILAN ISHLASH (Random & Daily)
# ==========================================
async def get_questions_by_difficulty(session, category_id: int, difficulty: str, limit: int = 3):
    stmt = (
        select(Question)
        .filter(Question.category_id == category_id, Question.difficulty == difficulty)
        .order_by(func.random())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_random_questions(session, cat_id: int, difficulty: str, limit: int = 3):
    return await get_questions_by_difficulty(session, cat_id, difficulty, limit)

async def get_daily_questions(session, limit: int = 10):
    stmt = select(Question).order_by(func.random()).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

async def add_question(session, cat_id: int, difficulty: str, q_text: str, a: str, b: str, c: str, d: str, correct: str, expl: str):
    new_q = Question(
        category_id=cat_id,
        difficulty=difficulty,
        question=q_text,
        option_a=a,
        option_b=b,
        option_c=c,
        option_d=d,
        correct_answer=correct,
        explanation=expl
    )
    session.add(new_q)
    await session.commit()
    return new_q


# ==========================================
# 4. DAILY CHALLENGE (KUNLIK TESTLAR)
# ==========================================
async def check_daily_completion(user):
    if not user:
        return False
    if hasattr(user, 'last_daily_date') and user.last_daily_date:
        return user.last_daily_date.date() == datetime.utcnow().date()
    return False

async def mark_daily_completed(session, user):
    if isinstance(user, User):
        u = user
    else:
        u = await get_user_by_id(session, user)
    if u:
        u.last_daily_date = datetime.utcnow()
        await session.commit()
        await session.refresh(u)
    return u


# ==========================================
# 5. NATIJALAR, STATISTIKA, PROFIL VA REYTING
# ==========================================
async def save_result(session, user_id: int, category_id: int, correct: int, wrong: int, score: int, xp: int = 0):
    res = Result(
        user_id=user_id,
        category_id=category_id,
        correct=correct,
        wrong=wrong,
        score=score,
        xp=xp
    )
    session.add(res)
    await session.commit()
    return res

async def get_user_stats(session, user_id: int):
    stmt = select(
        func.count(Result.id).label("tests"),
        func.coalesce(func.sum(Result.correct), 0).label("correct"),
        func.coalesce(func.sum(Result.wrong), 0).label("wrong")
    ).filter(Result.user_id == user_id)
    res = await session.execute(stmt)
    row = res.one_or_none()
    if row:
        return {"tests": row.tests, "correct": row.correct, "wrong": row.wrong}
    return {"tests": 0, "correct": 0, "wrong": 0}

async def get_user_rank(session, user_id: int):
    user_stmt = select(User).filter(User.id == user_id)
    u_res = await session.execute(user_stmt)
    user = u_res.scalars().first()
    if not user:
        return 1
    
    rank_stmt = select(func.count(User.id)).filter(User.xp > (user.xp or 0))
    rank_res = await session.execute(rank_stmt)
    count = rank_res.scalar() or 0
    return count + 1

async def get_top_players(session, limit: int = 10):
    if hasattr(User, 'xp'):
        stmt = select(User).order_by(User.xp.desc()).limit(limit)
    else:
        stmt = select(User).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

get_top_users = get_top_players

async def get_admin_stats(session):
    users_count = await session.execute(select(func.count(User.id)))
    questions_count = await session.execute(select(func.count(Question.id)))
    return users_count.scalar() or 0, questions_count.scalar() or 0

async def get_all_user_ids(session):
    stmt = select(User.telegram_id)
    result = await session.execute(stmt)
    return result.scalars().all()


# ==========================================
# 6. REFERRAL TIZIMI (YANGI QO'SHILDI)
# ==========================================
async def add_referral(session, referrer_id: int, referee_id: int):
    # O'zini o'zi taklif qilolmaydi
    if referrer_id == referee_id:
        return False, 0
    
    # Oldin ushbu odam kimningdir havolasi orqali qo'shilganmi tekshiramiz
    stmt = select(Referral).filter(Referral.referee_id == referee_id)
    res = await session.execute(stmt)
    if res.scalars().first():
        return False, 0
    
    # Yangi referral qo'shamiz
    new_ref = Referral(referrer_id=referrer_id, referee_id=referee_id)
    session.add(new_ref)
    await session.commit()
    
    # Jami taklif qilingan do'stlar sonini hisoblaymiz
    count_stmt = select(func.count(Referral.id)).filter(Referral.referrer_id == referrer_id)
    count_res = await session.execute(count_stmt)
    total_count = count_res.scalar() or 0
    return True, total_count

async def get_user_referrals_count(session, user_id: int):
    stmt = select(func.count(Referral.id)).filter(Referral.referrer_id == user_id)
    res = await session.execute(stmt)
    return res.scalar() or 0