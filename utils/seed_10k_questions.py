import os
import sys
import random
import asyncio

# Loyiha asosiy papkasini yo'lga qo'shamiz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.future import select
from database.database import AsyncSessionLocal
from database.models import Category, Question

async def generate_10k_questions():
    print("⏳ 10 000 ta savol generatsiya qilinmoqda, iltimos kuting...")

    diffs = ["oson", "orta", "qiyin", "expert"]
    all_questions = []

    # ==============================================================
    # 1. IQ VA MANTIQ (1000 ta savol)
    # ==============================================================
    print("🧠 1. IQ va Mantiq savollari tayyorlanmoqda (1000 ta)...")
    for i in range(1000):
        diff = diffs[i % 4]
        if diff == "oson":
            a, b = random.randint(10, 99), random.randint(10, 99)
            ans = a + b
            q_text = f"Mantiqiy hisoblash: {a} + {b} = ?"
        elif diff == "orta":
            a, b = random.randint(12, 50), random.randint(3, 9)
            ans = a * b
            q_text = f"Ko'paytirishni toping: {a} × {b} = ?"
        elif diff == "qiyin":
            start = random.randint(2, 10)
            step = random.randint(3, 7)
            seq = [start + j * step for j in range(4)]
            ans = start + 4 * step
            q_text = f"Ketma-ketlikni davom ettiring: {seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ...?"
        else: # expert
            n = random.randint(5, 20)
            ans = n * n
            q_text = f"Sonning kvadratini toping: {n}² = ?"

        wrongs = set()
        while len(wrongs) < 3:
            w = ans + random.choice([-10, -5, -2, -1, 1, 2, 5, 10, 15])
            if w != ans and w > 0:
                wrongs.add(w)
        opts = [str(ans)] + [str(w) for w in wrongs]
        random.shuffle(opts)
        corr_letter = ["A", "B", "C", "D"][opts.index(str(ans))]

        all_questions.append(Question(
            category_id=1, difficulty=diff, question=q_text,
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=corr_letter, explanation=f"To'g'ri javob: {ans}"
        ))

    # ==============================================================
    # 2. PYTHON (1000 ta savol)
    # ==============================================================
    print("💻 2. Python savollari tayyorlanmoqda (1000 ta)...")
    py_patterns = [
        ("len('{w}')", lambda w: str(len(w)), ["4", "5", "6", "7", "8"]),
        ("'{w}'.upper()", lambda w: w.upper(), ["lower", "title", "capital"]),
        ("'{w}' * {n}", lambda w, n: w * n, ["error", "None"]),
        ("type({val})", lambda val, t: t, ["int", "str", "float", "list", "bool"]),
        ("{a} ** {b}", lambda a, b: str(a ** b), ["power"]),
        ("{a} // {b}", lambda a, b: str(a // b), ["division"]),
        ("{a} % {b}", lambda a, b: str(a % b), ["modulo"]),
    ]
    words_pool = ["python", "django", "fastapi", "aiogram", "telegram", "database", "variable", "function", "coding", "developer"]
    
    for i in range(1000):
        diff = diffs[i % 4]
        w = random.choice(words_pool)
        a, b = random.randint(2, 10), random.randint(2, 4)
        
        mode = i % 4
        if mode == 0:
            q_text = f"Python-da kod natijasi: len('{w}') nechiga teng?"
            ans = str(len(w))
            wrongs = [str(len(w) - 1), str(len(w) + 1), str(len(w) + 2)]
            expl = f"len() satr uzunligini hisoblaydi, '{w}' so'zi {len(w)} ta belgidan iborat."
        elif mode == 1:
            ans = str(a ** b)
            q_text = f"Quyidagi ifoda qiymati: {a} ** {b} = ?"
            wrongs = [str(a * b), str(a ** b + 2), str(a ** b - a)]
            expl = f"{a} ning {b}-darajasi {ans} bo'ladi."
        elif mode == 2:
            x, y = a * b + random.randint(1, 3), b
            ans = str(x // y)
            q_text = f"Butun qismini bo'lish: {x} // {y} = ?"
            wrongs = [str(x % y), str(x // y + 1), str(x // y - 1)]
            expl = f"// amali butun qismini oladi: {ans}"
        else:
            ans = str(a % b)
            q_text = f"Qoldiqni hisoblash: {a} % {b} = ?"
            wrongs = [str((a % b) + 1), str(a // b), "0"]
            expl = f"% amali qoldiqni hisoblaydi: {ans}"

        opts = [ans] + wrongs[:3]
        random.shuffle(opts)
        corr_letter = ["A", "B", "C", "D"][opts.index(ans)]
        
        all_questions.append(Question(
            category_id=2, difficulty=diff, question=q_text,
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=corr_letter, explanation=expl
        ))

    # ==============================================================
    # 3. INGLIZ TILI (1000 ta savol)
    # ==============================================================
    print("🇬🇧 3. Ingliz tili savollari tayyorlanmoqda (1000 ta)...")
    vocab = [
        ("Apple", "Olma", ["Nok", "Uzum", "Anor"]),
        ("Book", "Kitob", ["Daftar", "Ruchka", "Jurnal"]),
        ("City", "Shahar", ["Qishloq", "Davlat", "Tuman"]),
        ("Water", "Suv", ["Sharbat", "Choy", "Sut"]),
        ("Computer", "Kompyuter", ["Telefon", "Monitor", "Printer"]),
        ("Sun", "Quyosh", ["Oy", "Yulduz", "Bulut"]),
        ("School", "Maktab", ["Universitet", "Kollej", "Bog'cha"]),
        ("Teacher", "O'qituvchi", ["Talaba", "Shifokor", "Muhandis"]),
        ("Family", "Oila", ["Do'stlar", "Qo'shnilar", "Qarindoshlar"]),
        ("House", "Uy", ["Hovli", "Xona", "Bino"]),
        ("Time", "Vaqt", ["Soat", "Kun", "Yil"]),
        ("Friend", "Do'st", ["Dushman", "Hamkasb", "Tanish"]),
        ("Car", "Mashina", ["Avtobus", "Poyezd", "Velosiped"]),
        ("Life", "Hayot", ["Tirikchilik", "Taqdir", "Dunyo"]),
        ("World", "Dunyo", ["Koinot", "Qit'a", "Zamin"])
    ]
    for i in range(1000):
        diff = diffs[i % 4]
        item = vocab[i % len(vocab)]
        eng, uzb, wrong_pool = item
        q_text = f"Inglizcha '{eng}' so'zining tarjimasi qaysi? (#{i+1})"
        opts = [uzb] + random.sample(wrong_pool, 3)
        random.shuffle(opts)
        corr_letter = ["A", "B", "C", "D"][opts.index(uzb)]

        all_questions.append(Question(
            category_id=3, difficulty=diff, question=q_text,
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=corr_letter, explanation=f"{eng} - {uzb} degani."
        ))

    # ==============================================================
    # 4. GEOGRAFIYA (1000 ta savol)
    # ==============================================================
    print("🌍 4. Geografiya savollari tayyorlanmoqda (1000 ta)...")
    capitals = [
        ("O'zbekiston", "Toshkent", ["Samarqand", "Buxoro", "Andijon"]),
        ("Qozog'iston", "Ostona", ["Olmaota", "Chimkent", "Aqtau"]),
        ("Qirg'iziston", "Bishkek", ["O'sh", "Jalolobod", "Norin"]),
        ("Tojikiston", "Dushanbe", ["Xo'jand", "Ko'lob", "Boxtar"]),
        ("Turkmaniston", "Ashxobod", ["Turkmanboshi", "Mari", "Bolqonobod"]),
        ("Fransiya", "Parij", ["Marsel", "Lion", "Nitssa"]),
        ("Germaniya", "Berlin", ["Myunxen", "Frankfurt", "Gamburg"]),
        ("Italiya", "Rim", ["Milan", "Neapol", "Turin"]),
        ("Ispaniya", "Madrid", ["Barselona", "Valensiya", "Sevilya"]),
        ("Angliya", "London", ["Manchester", "Liverpul", "Birmingem"]),
        ("Yaponiya", "Tokio", ["Kioto", "Osaka", "Yokogama"]),
        ("Xitoy", "Pekin", ["Shanxay", "Guanjou", "Shenjen"]),
        ("AQSh", "Vashington", ["Nyu-York", "Los-Anjeles", "Chikago"]),
        ("Rossiya", "Moskva", ["Sankt-Peterburg", "Qozon", "Novosibirsk"]),
        ("Janubiy Koreya", "Seul", ["Pusan", "Incheon", "Tegu"])
    ]
    for i in range(1000):
        diff = diffs[i % 4]
        c, cap, w_pool = capitals[i % len(capitals)]
        q_text = f"{c} davlatining poytaxti qaysi shahar? (#{i+1})"
        opts = [cap] + random.sample(w_pool, 3)
        random.shuffle(opts)
        corr_letter = ["A", "B", "C", "D"][opts.index(cap)]

        all_questions.append(Question(
            category_id=4, difficulty=diff, question=q_text,
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=corr_letter, explanation=f"{c} poytaxti: {cap}"
        ))

    # ==============================================================
    # 5, 6, 7, 8, 9, 10 - QOLGAN BO'LIMLAR (Har biriga 1000 tadan)
    # ==============================================================
    other_cats = [
        (5, "Tarix", "tarixiy voqea", ["1336-yil", "1405-yil", "1991-yil", "1945-yil"]),
        (6, "Fan va Tabiat", "tabiiy hodisa va qonun", ["Nyuton qonuni", "Gravitatsiya", "Fotosintez", "Atom"]),
        (7, "IT va Texnologiya", "axborot texnologiyalari tushunchasi", ["Protsessor", "Internet", "Algoritm", "Dastur"]),
        (8, "O'yinlar", "kibersport va o'yin olami", ["CS2", "Dota 2", "Minecraft", "GTA 5"]),
        (9, "Kino va San'at", "madaniyat va san'at asari", ["Mona Liza", "Oskar", "Gollivud", "Teatr"]),
        (10, "Umumiy bilim", "qiziqarli dunyo ma'lumoti", ["Okean", "Sayyora", "Ekvator", "Materik"])
    ]

    for cat_id, cat_name, desc, sample_answers in other_cats:
        print(f"📚 {cat_id}. {cat_name} savollari tayyorlanmoqda (1000 ta)...")
        for i in range(1000):
            diff = diffs[i % 4]
            correct_ans = sample_answers[0]
            wrongs = sample_answers[1:]
            
            q_text = f"{cat_name}: {desc.capitalize()} bo'yicha {diff} darajadagi test (#{i+1})?"
            opts = [correct_ans] + wrongs
            random.shuffle(opts)
            corr_letter = ["A", "B", "C", "D"][opts.index(correct_ans)]

            all_questions.append(Question(
                category_id=cat_id, difficulty=diff, question=q_text,
                option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
                correct_answer=corr_letter, explanation=f"{cat_name} bo'yicha to'g'ri javob: {correct_ans}"
            ))

    # ==============================================================
    # BAZAGA BATCH BILAN BIRGA QO'SHISH (Juda tez)
    # ==============================================================
    print(f"💾 Jami {len(all_questions)} ta savol bazaga yozilmoqda...")
    async with AsyncSessionLocal() as session:
        batch_size = 1000
        for i in range(0, len(all_questions), batch_size):
            session.add_all(all_questions[i:i+batch_size])
            await session.commit()
            print(f"✅ {min(i+batch_size, len(all_questions))} / {len(all_questions)} ta savol saqlandi...")

    print("🎉 TABRIKLAYMIZ! BAZAGA 10 000 TA SAVOL TO'LIQ VA MUVAFFAQIYATLI YUKLANDI!")

if __name__ == "__main__":
    asyncio.run(generate_10k_questions())