import asyncio
from sqlalchemy.future import select
from database.database import AsyncSessionLocal
from database.models import Category, Question

CATEGORIES = [
    {"id": 1, "name": "IQ va Mantiq", "icon": "🧠"},
    {"id": 2, "name": "Python", "icon": "💻"},
    {"id": 3, "name": "Ingliz tili", "icon": "🇬🇧"},
    {"id": 4, "name": "Geografiya", "icon": "🌍"},
    {"id": 5, "name": "Tarix", "icon": "🏛"},
    {"id": 6, "name": "Fan va Tabiat", "icon": "🔬"},
    {"id": 7, "name": "IT va Texnologiya", "icon": "🖥"},
    {"id": 8, "name": "O'yinlar", "icon": "🎮"},
    {"id": 9, "name": "Kino va San'at", "icon": "🎬"},
    {"id": 10, "name": "Umumiy bilim", "icon": "🧩"}
]

QUESTIONS_DATA = [
    # --- 1. IQ VA MANTIQ ---
    {"cat_id": 1, "difficulty": "oson", "question": "Ketma-ketlikni davom ettiring: 2, 4, 8, 16, ...?", "a": "24", "b": "32", "c": "64", "d": "20", "correct": "B", "explanation": "Har bir son 2 ga ko'paytirib boriladi."},
    {"cat_id": 1, "difficulty": "oson", "question": "Poygada 2-o'rindagi yuguruvchini quvib o'tsangiz nechanchi bo'lasiz?", "a": "1-o'rin", "b": "2-o'rin", "c": "3-o'rin", "d": "Oxirgi", "correct": "B", "explanation": "2-o'rindagining o'rnini egallaysiz."},
    {"cat_id": 1, "difficulty": "orta", "question": "Ota 36, o'g'il 6 yoshda. Necha yildan keyin ota o'g'ildan 4 marta katta bo'ladi?", "a": "2 yil", "b": "4 yil", "c": "6 yil", "d": "3 yil", "correct": "B", "explanation": "4 yildan keyin ota 40, o'g'il 10 da bo'ladi."},
    {"cat_id": 1, "difficulty": "qiyin", "question": "3 ta mushuk 3 sichqonni 3 minutda tutsa, 100 mushuk 100 sichqonni necha minutda tutadi?", "a": "100 minut", "b": "33 minut", "c": "3 minut", "d": "1 minut", "correct": "C", "explanation": "Har bir mushuk 1 sichqonni 3 minutda tutadi."},
    {"cat_id": 1, "difficulty": "expert", "question": "Soat 3:15 da soat va daqiqa millari orasidagi burchak necha daraja?", "a": "0°", "b": "7.5°", "c": "15°", "d": "12.5°", "correct": "B", "explanation": "Soat mili 15 minutda 7.5 darajaga suriladi."},

    # --- 2. PYTHON ---
    {"cat_id": 2, "difficulty": "oson", "question": "Python-da konsolga ma'lumot chiqarish funksiyasi qaysi?", "a": "echo()", "b": "print()", "c": "output()", "d": "write()", "correct": "B", "explanation": "print() standart chiqarish funksiyasidir."},
    {"cat_id": 2, "difficulty": "oson", "question": "Python fayllarining kengaytmasi qanday?", "a": ".pt", "b": ".py", "c": ".pyt", "d": ".python", "correct": "B", "explanation": "Python fayllari .py kengaytmasiga ega."},
    {"cat_id": 2, "difficulty": "orta", "question": "Qaysi ma'lumot turi o'zgarmas (immutable) hisoblanadi?", "a": "list", "b": "dict", "c": "set", "d": "tuple", "correct": "D", "explanation": "Tuple elementlarini o'zgartirib bo'lmaydi."},
    {"cat_id": 2, "difficulty": "qiyin", "question": "List'ga element qo'shish uchun qaysi metod ishlatiladi?", "a": "add()", "b": "push()", "c": "append()", "d": "insert_end()", "correct": "C", "explanation": "append() ro'yxat oxiriga element qo'shadi."},
    {"cat_id": 2, "difficulty": "expert", "question": "Python-da GIL nimani anglatadi?", "a": "Global Interpreter Lock", "b": "General Input Language", "c": "Global Interface Logic", "d": "General Internal Loop", "correct": "A", "explanation": "GIL - Global Interpreter Lock hisoblanadi."},

    # --- 3. INGLIZ TILI ---
    {"cat_id": 3, "difficulty": "oson", "question": "'Apple' so'zining o'zbekcha tarjimasi nima?", "a": "Nok", "b": "Olma", "c": "Uzum", "d": "Anor", "correct": "B", "explanation": "Apple - Olma degani."},
    {"cat_id": 3, "difficulty": "orta", "question": "'Go' fe'lining o'tgan zamon (Past Simple) shakli qaysi?", "a": "Goned", "b": "Went", "c": "Gone", "d": "Going", "correct": "B", "explanation": "Go -> Went -> Gone."},
    {"cat_id": 3, "difficulty": "qiyin", "question": "Qaysi so'z 'Huge' so'ziga sinonim hisoblanadi?", "a": "Tiny", "b": "Small", "c": "Enormous", "d": "Narrow", "correct": "C", "explanation": "Huge va Enormous - ulkan, juda katta degani."},

    # --- 4. GEOGRAFIYA ---
    {"cat_id": 4, "difficulty": "oson", "question": "O'zbekiston poytaxti qaysi shahar?", "a": "Samarqand", "b": "Toshkent", "c": "Buxoro", "d": "Namangan", "correct": "B", "explanation": "Toshkent O'zbekiston poytaxti."},
    {"cat_id": 4, "difficulty": "orta", "question": "Dunyodagi eng uzun daryo qaysi?", "a": "Amazonka", "b": "Nil", "c": "Yanszi", "d": "Missisipi", "correct": "B", "explanation": "Nil daryosi eng uzundir."},
    {"cat_id": 4, "difficulty": "qiyin", "question": "Maydoni bo'yicha dunyodagi eng katta mamlakat qaysi?", "a": "Xitoy", "b": "AQSh", "c": "Rossiya", "d": "Kanada", "correct": "C", "explanation": "Rossiya eng katta hududga ega."},

    # --- 5. TARIX ---
    {"cat_id": 5, "difficulty": "oson", "question": "Amir Temur nechanchi yilda tug'ilgan?", "a": "1336-yil", "b": "1405-yil", "c": "1220-yil", "d": "1441-yil", "correct": "A", "explanation": "Amir Temur 1336-yil 9-aprelda tug'ilgan."},
    {"cat_id": 5, "difficulty": "orta", "question": "Ikkinchi jahon urushi nechanchi yillarda bo'lib o'tgan?", "a": "1914-1918", "b": "1939-1945", "c": "1941-1945", "d": "1935-1940", "correct": "B", "explanation": "2-Jahon urushi 1939-1945 yillarda bo'lgan."},

    # --- 6. FAN VA TABIAT ---
    {"cat_id": 6, "difficulty": "oson", "question": "Suvning kimyoviy formulasi qanday?", "a": "CO2", "b": "H2O", "c": "O2", "d": "NaCl", "correct": "B", "explanation": "H2O - suv formulasi."},
    {"cat_id": 6, "difficulty": "orta", "question": "Quyosh tizimidagi eng katta planeta qaysi?", "a": "Mars", "b": "Yupiter", "c": "Saturn", "d": "Venera", "correct": "B", "explanation": "Yupiter eng katta gazli planeta."},

    # --- 7. IT VA TEXNOLOGIYA ---
    {"cat_id": 7, "difficulty": "oson", "question": "CPU nimani anglatadi?", "a": "Central Processing Unit", "b": "Computer Power Unit", "c": "Central Performance User", "d": "Control Program Unit", "correct": "A", "explanation": "CPU - Markaziy protsessor."},

    # --- 8. O'YINLAR ---
    {"cat_id": 8, "difficulty": "oson", "question": "Minecraft o'yinining asosiy figurasi nima?", "a": "Shakllar", "b": "Kublar (Block)", "c": "Sfera", "d": "Uchburchak", "correct": "B", "explanation": "Minecraft bloklardan tashkil topgan."},

    # --- 9. KINO VA SAN'AT ---
    {"cat_id": 9, "difficulty": "oson", "question": "Mona Liza kartinasini kim chizgan?", "a": "Pikasso", "b": "Leonardo da Vinchi", "c": "Van Gog", "d": "Mikelanjelo", "correct": "B", "explanation": "Leonardo da Vinchi asari."},

    # --- 10. UMUMIY BILIM ---
    {"cat_id": 10, "difficulty": "oson", "question": "Bir yilda nechta fasl bor?", "a": "2 ta", "b": "4 ta", "c": "12 ta", "d": "7 ta", "correct": "B", "explanation": "Bahor, Yoz, Kuz, Qish."}
]

async def seed_all_questions():
    async with AsyncSessionLocal() as session:
        # 1. KATEGORIYALARNI SAQLASH
        for cat in CATEGORIES:
            res = await session.execute(select(Category).filter_by(id=cat["id"]))
            if not res.scalars().first():
                session.add(Category(id=cat["id"], name=cat["name"], icon=cat["icon"]))
        await session.commit()

        # 2. Model ustunlarining nomlarini aniqlash (correct_option / correct / answer va h.k.)
        question_columns = [c.name for c in Question.__table__.columns]
        
        correct_col = "correct"
        if "correct_option" in question_columns:
            correct_col = "correct_option"
        elif "correct_answer" in question_columns:
            correct_col = "correct_answer"
        elif "answer" in question_columns:
            correct_col = "answer"

        # 3. SAVOLLARNI SAQLASH
        for q in QUESTIONS_DATA:
            res = await session.execute(select(Question).filter_by(question=q["question"]))
            if not res.scalars().first():
                q_data = {
                    "category_id": q["cat_id"],
                    "difficulty": q["difficulty"],
                    "question": q["question"],
                    "option_a": q["a"],
                    "option_b": q["b"],
                    "option_c": q["c"],
                    "option_d": q["d"],
                    correct_col: q["correct"],
                    "explanation": q["explanation"]
                }
                session.add(Question(**q_data))
        await session.commit()
        print("✅ Barcha kategoriyalar va savollar muvaffaqiyatli saqlandi!")

if __name__ == "__main__":
    asyncio.run(seed_all_questions())