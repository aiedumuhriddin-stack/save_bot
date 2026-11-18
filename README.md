# SAVE BOT — YouTube / Instagram Telegram bot

Bot YouTube yoki ommaga ochiq Instagram havolasini qabul qiladi. Foydalanuvchi faqat ikki tugmadan birini tanlaydi: **Video (MP4)** yoki **Audio (MP3)**. Sifat tanlash oynasi yo'q.

## Imkoniyatlar
- YouTube va Instagram havolalarini qabul qilish.
- MP4 video yoki MP3 audio tanlash.
- Video Telegram yuborish hajmi chegarasidan oshsa, FFmpeg orqali tezkor (`ultrafast`) avtomatik siqish.
- Tezlik uchun oldindan birlashtirilgan MP4 oqimini afzal tanlash; bu alohida video/audio oqimlarini yuklab birlashtirish vaqtini kamaytiradi.
- Tarmoq uzilib qolsa uzoq kutib qolmaslik uchun qisqartirilgan timeout va retry sozlamalari.
- Uchta parallel yuklash sloti; har bir yuklash Telegram event loopini bloklamaydi.
- FFmpeg uchun `imageio-ffmpeg` paketidagi Windows/Linux mos binarydan foydalanish; tizimdagi FFmpeg ham qo'llab-quvvatlanadi.
- Har bir yuklama uchun alohida vaqtinchalik papka va yuborilgach avtomatik tozalash.
- Xatolarni `logs/bot.log` fayliga tokenni oshkor qilmasdan yozish.

## Talablar
- Python 3.10 yoki yangiroq (Python 3.12 tavsiya qilinadi; 3.13 ham mos bo'lishi kerak).
- Telegram bot tokeni.
- Internet ulanishi.

## Windows (PowerShell) o'rnatish
Loyiha papkasida quyidagilarni bajaring:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` faylini ochib BotFather bergan tokenni `BOT_TOKEN=` qatoriga yozing. Haqiqiy tokenni hech kimga yubormang.

Botni ishga tushirish:

```powershell
python save_bot.py
```

Yoki:

```powershell
python bot.py
```

## Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
nano .env
python save_bot.py
```

## Sozlamalar (.env)

```env
BOT_TOKEN=YOUR_NEW_TOKEN
MAX_FILE_SIZE_MB=48
MAX_SOURCE_FILE_SIZE_MB=500
```

`MAX_FILE_SIZE_MB` Telegramga yuboriladigan yakuniy fayl uchun xavfsiz chegara. Katta video avtomatik siqiladi. `MAX_SOURCE_FILE_SIZE_MB` manba faylning maksimal yuklash hajmi.

Agar tizimingizda FFmpeg alohida o'rnatilgan bo'lsa, ixtiyoriy `FFMPEG_DIR` orqali uning `bin` papkasini ko'rsatishingiz mumkin. Odatda `imageio-ffmpeg` yetarli.

## Ishlatish
1. Telegramda botga `/start` yuboring.
2. YouTube yoki ommaga ochiq Instagram havolasini yuboring.
3. `🎥 Video (MP4)` yoki `🎵 Audio (MP3)` tugmasini bosing.
4. Bot tayyor faylni shu chatga yuboradi.
5. Bekor qilish uchun `/cancel` yuboring (yuklash boshlanganidan keyin joriy jarayonni to'xtatmaydi).

## Muhim cheklovlar
- Faqat ommaga ochiq va yuklab olishga ruxsatingiz bo'lgan kontentdan foydalaning.
- Private, o'chirilgan, login/cookies talab qiladigan yoki platforma tomonidan bloklangan materialni olish kafolatlanmaydi.
- YouTube/Instagram o'z himoyasini o'zgartirishi mumkin; `yt-dlp` ni yangilab turing: `python -m pip install -U yt-dlp`.
- Telegram botining bulut API yuklash chegarasi mavjud. Yakuniy fayl standart holatda 48 MB dan oshmaydi; video shu chegaraga moslab siqiladi.
- Tezlik platforma, internet va video hajmiga bog'liq; havola yuborilishi bilan tanlov tugmalari chiqadi, haqiqiy yuklash VIDEO yoki MP3 tugmasi bosilgach boshlanadi. Hech bir platformada yuklashni mutlaqo bir zumda bajarish kafolatlanmaydi.
- Tezlik uchun tanlangan `best[ext=mp4]/best` odatda eng yaxshi bitta faylli oqimni oladi; ayrim YouTube videolarida bu eng yuqori mavjud adaptiv sifatdan pastroq bo'lishi mumkin, lekin qayta birlashtirishni kamaytiradi.
- Instagram login/cookies talab qilsa, bot buni chetlab o'tmaydi; ommaviy havola kerak.

## Diagnostika

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -v
```

Xato takrorlansa, `logs/bot.log` oxiridagi xabarni tekshiring. `.env` faylini yoki tokenni hech kimga yubormang.
