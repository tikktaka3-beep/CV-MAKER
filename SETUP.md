# 📊 SLIDE BOT — O'rnatish qo'llanmasi

Bu bot foydalanuvchidan matn oladi, bir nechta savol beradi (til, slayd soni, uslub),
so'ng Gemini AI (BEPUL) yordamida tarkib yozadi va chiroyli **.pptx** taqdimot fayl qilib yuboradi.

## 📁 Fayllar tarkibi (hammasi flat, papkasiz — GitHub mobil uchun mos)

| Fayl | Vazifasi |
|------|----------|
| `main.py` | Botning asosiy fayli — barcha savol-javob va buyruqlar shu yerda |
| `database.py` | Kunlik limitni SQLite orqali saqlaydi |
| `ai_generator.py` | Gemini API ga so'rov yuborib, slaydlar matnini yaratadi (BEPUL) |
| `slide_generator.py` | Tayyor matn asosida chiroyli .pptx faylni yasaydi |
| `requirements.txt` | Kerakli kutubxonalar ro'yxati |
| `Procfile` | Railway uchun: botni qanday ishga tushirishni aytadi |

---

## 1-qadam: Telegram bot yaratish (agar hali yo'q bo'lsa)

1. Telegramda **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring, nom va username bering
3. U sizga **BOT_TOKEN** beradi (masalan: `123456789:ABCdefGhIJKlmNoPQRstuVWXyz`) — buni saqlab qo'ying

## 2-qadam: Gemini (Google AI) API kalitini olish — BEPUL, kartasiz

Bu bot taqdimot matnini yozish uchun Google'ning Gemini AI'sidan foydalanadi.
Bu **butunlay bepul** — kredit karta talab qilinmaydi, kuniga 1000+ so'rovga ruxsat beradi
(bizga esa kuniga bir necha taqdimot kerak bo'ladi, xolos):

1. Telefon brauzerida **aistudio.google.com** saytiga kiring
2. Google hisobingiz orqali kiring
3. **"Get API key"** yoki **"Create API key"** tugmasini bosing
4. Yangi loyiha yaratishni so'rasa — "Create API key in new project" ni tanlang
5. Yaratilgan kalitni nusxalab oling — u `AIza...` bilan boshlanadi
   ⚠️ Buni darhol saqlab qo'ying (masalan Eslatmalar appiga)
6. Kredit karta yoki to'lov qo'shish **shart emas** — bepul tarif shu tarzda ishlaydi

ℹ️ Agar kelajakda foydalanuvchilar ko'payib, limitga tez-tez tegib qolsangiz,
`ai_generator.py` faylida `MODEL = "gemini-2.5-flash"` qatorini
`MODEL = "gemini-2.5-flash-lite"` ga o'zgartiring — bu yanada ko'proq bepul so'rov beradi.

## 3-qadam: Admin ID ni olish (limitlarni boshqarish uchun)

1. Telegramda **@userinfobot** ga yozing
2. U sizga raqamli ID raqamingizni beradi (masalan `123456789`)
3. Shu raqamni saqlab qo'ying — bu **ADMIN_ID** bo'ladi (faqat siz `/setlimit` buyrug'ini ishlatib, foydalanuvchilarga qo'shimcha limit bera olasiz)

## 4-qadam: Fayllarni GitHub'ga yuklash (mobil orqali)

HARAJAT bot bilan qilganingizdek:

1. GitHub ilovasida (yoki mobil brauzerda github.com) **yangi repository** yarating (masalan `slide-bot`)
2. Repo ichida **"Add file" → "Upload files"** tugmasini bosing
3. Yuqoridagi 6 ta faylni (main.py, database.py, ai_generator.py, slide_generator.py, requirements.txt, Procfile) birma-bir yuklang
4. Har bir fayl nomi va kengaytmasi aynan saqlanishiga ishonch hosil qiling (masalan `.py` o'chib qolmasin)
5. **"Commit changes"** tugmasini bosing

## 5-qadam: Railway'da deploy qilish

1. **railway.app** ga kiring, GitHub orqali login qiling
2. **"New Project" → "Deploy from GitHub repo"** tanlang
3. Yuklagan `slide-bot` repongizni tanlang
4. Railway avtomatik `requirements.txt` va `Procfile`ni aniqlab, o'rnatishni boshlaydi

## 6-qadam: Environment Variables (muhim!)

Railway loyihangiz ichida **"Variables"** bo'limiga o'ting va quyidagilarni qo'shing:

| Nomi | Qiymati |
|------|---------|
| `BOT_TOKEN` | BotFather'dan olgan token |
| `GEMINI_API_KEY` | aistudio.google.com'dan olgan bepul kalit (`AIza...`) |
| `ADMIN_ID` | @userinfobot'dan olgan raqamli ID'ingiz |
| `ADMIN_CONTACT` | `@tikitaka1103` (yoki o'zgartirmoqchi bo'lsangiz boshqa username) |

Har birini qo'shgandan keyin Railway avtomatik qaytadan deploy qiladi.

## 7-qadam: Tekshirish

1. Railway'da **"Deployments"** bo'limidan loglarni kuzating — xatolik bo'lmasligi kerak
2. Telegram'da botingizga `/start` yuboring
3. Mavzu yozib, savollarga javob berib sinab ko'ring

---

## ⚙️ Limitlar haqida

- Har bir foydalanuvchi kuniga **1 ta** bepul taqdimot yarata oladi
- Limitni oshirish: `/setlimit <user_id> <yangi_limit>` — faqat siz (ADMIN_ID) ishlatishingiz mumkin
  - Misol: `/setlimit 123456789 10` — bu foydalanuvchiga kuniga 10 ta huquq beradi
- Foydalanuvchi o'z limitini `/mylimit` orqali ko'rishi mumkin

## 🎨 Dizayn haqida

Taqdimot dizayni 1 ta belgilangan, chiroyli, rangli shablon (to'q ko'k fon + oltin rang urg'usi
muqova/yopilish slaydlarida, oq fon + rangli belgilar mazmun slaydlarida). Foydalanuvchi
faqat til, slayd soni, uslub (matn ohangi) va qo'shimcha izohni tanlaydi — dizayn har doim bir xil.

## 🆘 Muammo bo'lsa

Railway logida xatolik chiqsa, ekran screenshotini yuborsangiz, men sababini aniqlab,
tuzatish uchun kerakli faylni qaytadan yozib beraman — avvalgi HARAJAT bot bilan qilganimizdek.
