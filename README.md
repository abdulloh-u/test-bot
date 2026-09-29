# 🤖 Test Master Bot — Telegram Quiz Platform

Zamonaviy intellektual test va bilim bellashuvi Telegram boti. Python va Aiogram 3 yordamida to'liq asinxron arxitektura asosida ishlab chiqilgan.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green?logo=telegram)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

---

## 🌟 Asosiy imkoniyatlar

- 📚 **10 ta yo'nalish:** IQ & Mantiq, Python, Ingliz tili, Geografiya, Tarix, Fan va Tabiat, IT & Texnologiya, O'yinlar, Kino va Umumiy bilim.
- 🎯 **4 xil qiyinchilik darajasi:** Oson, O‘rta, Qiyin va Expert.
- 🎲 **Tasodifiy testlar:** Har safar bazadan random savollar ajratiladi.
- 🌟 **Daily Challenge:** Har kuni yangi testlar va 2 baravar ko‘p XP (Streak zanjiri bilan).
- ⚔️ **1v1 Duel:** Real-vaqt rejimida do‘stlar bilan bilim bellashuvi.
- 👥 **Referral tizimi:** Do'stlarni taklif qilganlik uchun har 3 kishiga **+100 XP** avtomatik mukofot.
- 🏆 **Jonli Reyting & Profil:** XP, Level, Streak va testlardagi aniqlik foizi.
- 👑 **Admin Panel:** Yangi testlar kiritish, jonli statistika va barcha foydalanuvchilarga xabar tarqatish (Broadcast).

---

## 📂 Loyiha tuzilishi

```text
test_bot/
├── bot.py                  # Botni ishga tushirish
├── config.py               # Sozlamalar va muhit o'zgaruvchilari
├── requirements.txt        # Kerakli kutubxonalar
├── database/
│   ├── models.py           # SQLAlchemy modellari (User, Question, Result, Referral...)
│   ├── database.py         # Asinxron baza ulanishi
│   └── crud.py             # Bazaviy CRUD operatsiyalari
├── handlers/
│   ├── start.py            # /start va Referral menyusi
│   ├── tests.py            # Yo'nalishlar va daraja tanlash
│   ├── quiz.py             # Test yechish mexanizmi
│   ├── daily.py            # Kunlik challenge
│   ├── battle.py           # 1v1 duel
│   ├── profile.py          # Profil va statistika
│   ├── leaderboard.py      # Top foydalanuvchilar reytingi
│   └── admin.py            # Admin boshqaruv paneli
├── keyboards/              # Inline va Reply klaviaturalar
├── states/                 # FSM holatlari
└── utils/                  # Yordamchi vositalar va savollar bazasi