import os
import sys
# Loyihaning asosiy papkasini Python yo'liga qo'shish
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import random
from sqlalchemy.future import select
from database.database import AsyncSessionLocal
from database.models import Category, Question
from sqlalchemy.future import select
from database.database import AsyncSessionLocal
from database.models import Category, Question



async def generate_and_seed_questions():
    async with AsyncSessionLocal() as session:
        # Barcha kategoriyalarni tekshiramiz
        res = await session.execute(select(Category))
        categories = res.scalars().all()
        
        if not categories:
            print("⚠️ Avval bot.py ni ishga tushirib kategoriyalarni yarating!")
            return

        print("🚀 Bazaga minglab savollarni yuklash boshlandi...")
        
        difficulties = ["oson", "orta", "qiyin", "expert"]
        questions_to_add = []

        # 1. IQ VA MANTIQ (1-bo'lim)
        for i in range(1, 101):
            n1 = random.randint(10, 99)
            n2 = random.randint(10, 99)
            ans = n1 + n2
            wrongs = random.sample([ans + 1, ans - 1, ans + 10, ans - 5, ans + 2], 3)
            opts = [str(ans)] + [str(w) for w in wrongs]
            random.shuffle(opts)
            correct_letter = ["A", "B", "C", "D"][opts.index(str(ans))]
            
            questions_to_add.append(Question(
                category_id=1,
                difficulty=random.choice(difficulties),
                question=f"Mantiqiy hisoblash: {n1} + {n2} = ?",
                option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
                correct_answer=correct_letter,
                explanation=f"{n1} ga {n2} qo'shilsa {ans} bo'ladi."
            ))

        # 2. PYTHON BO'YICHA KODLI SAVOLLAR (2-bo'lim)
        python_topics = [
            ("len('Python')", "6", "5", "7", "None", "A", "len() satr uzunligini qaytaradi"),
            ("type(5.5)", "float", "int", "str", "double", "A", "5.5 o'nlik kasr ya'ni float"),
            ("type([1, 2])", "list", "tuple", "dict", "set", "A", "Kvadrat qavs list turini bildiradi"),
            ("2 ** 3", "8", "6", "9", "5", "A", "** darajaga ko'tarish amali"),
            ("10 // 3", "3", "3.33", "1", "0", "A", "// butun qismni oladi"),
            ("10 % 3", "1", "3", "0", "2", "A", "% qoldiqni hisoblaydi"),
            ("bool('')", "False", "True", "None", "Error", "A", "Bo'sh satr mantiqiy False beradi"),
            ("bool('AI')", "True", "False", "None", "Error", "A", "Bo'sh bo'lmagan satr True beradi"),
            ("'a' in 'apple'", "True", "False", "Error", "None", "A", "in operatori mavjudlikni tekshiradi"),
            ("list(range(3))", "[0, 1, 2]", "[1, 2, 3]", "[0, 1, 2, 3]", "[]", "A", "range(3) 0 dan 2 gacha sonlar"),
            ("abs(-15)", "15", "-15", "0", "None", "A", "abs() sonning modulini qaytaradi"),
            ("min(4, 8, 2, 9)", "2", "4", "8", "9", "A", "min() eng kichik elementni qaytaradi"),
            ("max(4, 8, 2, 9)", "9", "8", "4", "2", "A", "max() eng katta elementni qaytaradi"),
            ("round(3.7)", "4", "3", "3.5", "5", "A", "round() sonni eng yaqin butun songa yaxlitlaydi"),
            ("'Hello'.lower()", "hello", "HELLO", "Hello", "hELLO", "A", "lower() harflarni kichik qiladi")
        ]
        
        for q, a, b, c, d, corr, expl in python_topics:
            for diff in difficulties:
                questions_to_add.append(Question(
                    category_id=2,
                    difficulty=diff,
                    question=f"Quyidagi kod natijasi nima bo'ladi: {q}?",
                    option_a=a, option_b=b, option_c=c, option_d=d,
                    correct_answer=corr,
                    explanation=expl
                ))

        # 3. INGLIZ TILI SO'ZLIK (3-bo'lim)
        english_words = [
            ("Book", "Kitob", "Daftar", "Qalam", "Stol", "A"),
            ("Water", "Suv", "Non", "Choy", "Sharbat", "A"),
            ("Sun", "Quyosh", "Oy", "Yulduz", "Bulut", "A"),
            ("Moon", "Oy", "Quyosh", "Yer", "Osmon", "A"),
            ("Earth", "Yer", "Oy", "Quyosh", "Mars", "A"),
            ("Friend", "Do'st", "Dushman", "Qo'shni", "Ustoz", "A"),
            ("Teacher", "O'qituvchi", "Talaba", "Shifokor", "Muhandis", "A"),
            ("Doctor", "Shifokor", "Hamshira", "O'qituvchi", "Haydovchi", "A"),
            ("City", "Shahar", "Qishloq", "Davlat", "Ko'cha", "A"),
            ("Country", "Mamlakat", "Shahar", "Viloyat", "Qit'a", "A"),
            ("Always", "Har doim", "Hech qachon", "Ba'zan", "Kamdan-kam", "A"),
            ("Never", "Hech qachon", "Har doim", "Tez-tez", "Hozir", "A"),
            ("Beautiful", "Chiroyli", "Xunuk", "Katta", "Kichik", "A"),
            ("Strong", "Kuchli", "Kuchsiz", "Tez", "Sekin", "A"),
            ("Fast", "Tez", "Sekin", "Og'ir", "Yengil", "A")
        ]
        
        for word, a, b, c, d, corr in english_words:
            for diff in difficulties:
                questions_to_add.append(Question(
                    category_id=3,
                    difficulty=diff,
                    question=f"'{word}' so'zining o'zbekcha tarjimasi qaysi?",
                    option_a=a, option_b=b, option_c=c, option_d=d,
                    correct_answer=corr,
                    explanation=f"{word} - {a} degani."
                ))

        # 4. GEOGRAFIYA (4-bo'lim)
        geo_capitals = [
            ("Fransiya", "Parij", "Lion", "Marsel", "Bordo", "A"),
            ("Germaniya", "Berlin", "Myunxen", "Gamburg", "Frankfurt", "A"),
            ("Ispaniya", "Madrid", "Barselona", "Valensiya", "Sevilya", "A"),
            ("Italiya", "Rim", "Milan", "Neapol", "Venetsiya", "A"),
            ("Yaponiya", "Tokio", "Kioto", "Osaka", "Xirosima", "A"),
            ("Janubiy Koreya", "Seul", "Pusan", "Incheon", "Tegu", "A"),
            ("Turkiya", "Anqara", "Istanbul", "Izmir", "Antaliya", "A"),
            ("Misr", "Qohira", "Iskandariya", "Giza", "Luksor", "A"),
            ("Kanada", "Ottava", "Toronto", "Vankuver", "Monreal", "A"),
            ("Braziliya", "Brazilia", "Rio-de-Janeyro", "San-Paulu", "Salvador", "A")
        ]
        
        for country, a, b, c, d, corr in geo_capitals:
            for diff in difficulties:
                questions_to_add.append(Question(
                    category_id=4,
                    difficulty=diff,
                    question=f"{country} davlatining poytaxti qaysi?",
                    option_a=a, option_b=b, option_c=c, option_d=d,
                    correct_answer=corr,
                    explanation=f"{country} poytaxti — {a} shahri."
                ))

        # 5. TARIX (5-bo'lim)
        history_data = [
            ("Al-Xorazmiy qaysi fanga asos solgan?", "Algebra", "Geometriya", "Fizika", "Kimyo", "A", "Al-Xorazmiy algebra asoschisidir."),
            ("Abu Ali ibn Sino qaysi sohada mashhur bo'lgan?", "Tibbiyot", "Astronomiya", "Falsafa", "Harbiy ish", "A", "Ibn Sino 'Tib qonunlari' asari muallifi."),
            ("Mirzo Ulug'bek qayerda rasadxona qurgan?", "Samarqand", "Buxoro", "Xiva", "Toshkent", "A", "Ulug'bek rasadxonasi Samarqandda joylashgan."),
            ("Amir Temur davlatining poytaxti qaysi shahar bo'lgan?", "Samarqand", "Kesh (Shahrisabz)", "Buxoro", "Hirot", "A", "Amir Temur Samarqandni poytaxt qilgan."),
            ("Alisher Navoiy qaysi tilda ijod qilgan?", "Turkiy (Eski o'zbek)", "Arab", "Lotin", "Rus", "A", "Navoiy turkiy adabiyot asoschisidir.")
        ]
        for q, a, b, c, d, corr, expl in history_data:
            for diff in difficulties:
                questions_to_add.append(Question(
                    category_id=5,
                    difficulty=diff,
                    question=q,
                    option_a=a, option_b=b, option_c=c, option_d=d,
                    correct_answer=corr,
                    explanation=expl
                ))

        # 6. FAN VA TABIAT (6-bo'lim)
        science_data = [
            ("Yorug'lik tezligi sekundiga taxminan necha km?", "300 000 km/s", "150 000 km/s", "500 000 km/s", "100 000 km/s", "A", "Vakuumda yorug'lik tezligi ~300 000 km/s."),
            ("Odam tanasining necha foizi suvdan iborat?", "~60-70%", "~30-40%", "~90%", "~50%", "A", "Katta odam tanasining 60-70% qismi suvdan iborat."),
            ("Eng og'ir ichki a'zo qaysi?", "Jigar", "Yurak", "O'pka", "Buyrak", "A", "Jigar eng og'ir ichki a'zo (~1.5 kg)."),
            ("Fotosintez jarayonida o'simliklar nima ajratadi?", "Kislorod (O2)", "Karbonat angidrid (CO2)", "Azot (N2)", "Vodorod (H2)", "A", "O'simliklar kislorod ajratadi.")
        ]
        for q, a, b, c, d, corr, expl in science_data:
            for diff in difficulties:
                questions_to_add.append(Question(
                    category_id=6,
                    difficulty=diff,
                    question=q,
                    option_a=a, option_b=b, option_c=c, option_d=d,
                    correct_answer=corr,
                    explanation=expl
                ))

        # 7. IT VA TEXNOLOGIYA (7-bo'lim)
        it_data = [
            ("HTML nimani anglatadi?", "HyperText Markup Language", "HighText Machine Language", "Hyperlink Text Mode", "Home Tool Markup", "A", "HTML - Gipermatn belgilash tili."),
            ("CSS ning asosiy vazifasi nima?", "Sahifa dizayni va uslubi", "Ma'lumotlar bazasi", "Server boshqaruvi", "Algoritm yozish", "A", "CSS - sahifa ko'rinishini belgilaydi."),
            ("RAM nima?", "Tezkor xotira", "Doimiy xotira", "Protsessor", "Videokarta", "A", "RAM - Random Access Memory."),
            ("IP adres nima?", "Tarmoqdagi qurilmaning unikal manzili", "Internet tezligi", "Sayt nomi", "Kompakt disk", "A", "IP - Internet Protocol manzili.")
        ]
        for q, a, b, c, d, corr, expl in it_data:
            for diff in difficulties:
                questions_to_add.append(Question(
                    category_id=7,
                    difficulty=diff,
                    question=q,
                    option_a=a, option_b=b, option_c=c, option_d=d,
                    correct_answer=corr,
                    explanation=expl
                ))

        # 8, 9, 10-kategoriyalar (O'yinlar, Kino, Umumiy bilim)
        general_data = [
            (8, "Dota 2 o'yinining janri qaysi?", "MOBA", "Shooter", "RPG", "Strategiya", "A", "Dota 2 MOBA janriga kiradi."),
            (8, "CS:GO / CS2 o'yinida asosiy maqsad nima?", "Bombani qo'yish yoki zararsizlantirish", "Poyga", "Uy qurish", "Futbol", "A", "Terrorist va Counter-Terrorist to'qnashuvi."),
            (9, "'Titanik' filmi rejissyori kim?", "Jeyms Kemeron", "Stiven Spilberg", "Kristofer Nolan", "Kventin Tarantino", "A", "James Cameron filmi."),
            (9, "'Oskar' mukofoti qaysi sohada beriladi?", "Kino san'ati", "Musiqa", "Adabiyot", "Sport", "A", "Oskar AQSh kinoakademiyasi mukofoti."),
            (10, "Dunyo okeanlari nechta?", "5 ta", "4 ta", "6 ta", "7 ta", "A", "Tinch, Atlantika, Hind, Shimoliy Muz va Janubiy okeanlar.")
        ]
        for cat_id, q, a, b, c, d, corr, expl in general_data:
            for diff in difficulties:
                questions_to_add.append(Question(
                    category_id=cat_id,
                    difficulty=diff,
                    question=q,
                    option_a=a, option_b=b, option_c=c, option_d=d,
                    correct_answer=corr,
                    explanation=expl
                ))

        # Barcha savollarni bazaga qo'shamiz
        session.add_all(questions_to_add)
        await session.commit()
        print(f"✅ BAZAGA JAMI {len(questions_to_add)} TA YANGI SAVOLLAR MUVAFFAQIYATLI QO'SHILDI!")

if __name__ == "__main__":
    asyncio.run(generate_and_seed_questions())