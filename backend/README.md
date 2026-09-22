# Shifokorxona CRM — Backend (Django + DRF + PostgreSQL)

Klinika/shifokorxona CRM API — email tasdiqlash (Brevo), OTP, shifokor
katalogi (qidiruv/filtr), admin panel va demo-ma'lumotlar.

## Ishga tushirish (lokal)

1. `.env` tayyorlang (qarang backend/.env.example) — `BREVO_API_KEY` email
   yuborish uchun majburiy, `DB_*` yoki `DATABASE_URL` PostgreSQL uchun.
2. Migratsiya va tekshiruv:

   ```bash
   python manage.py migrate
   python manage.py check
   ```

## Demo hisoblar (1 admin + 10 shifokor)

Idempotent seed-command — har safar takror ishlatsa bo'ladi (mavjud hisoblarga
tegilmaydi, parol random generatsiyalanib terminalda chiqariladi):

```bash
python manage.py seed_demo
```

Parollar **bilinadigan** bo'lishi uchun (demo/staging) — noma'lum demo parol:

```bash
python manage.py seed_demo --fixed-password 'Shifokor@2026'
```

| Hisob           | Email                   | Parol           |
|-----------------|-------------------------|-----------------|
| Admin           | admin@shifokorxona.uz   | Shifokor@2026   |
| Shifokor #1     | doctor1@shifokorxona.uz | Shifokor@2026   |
| Shifokor #2..10 | doctor2..10@shifokorxona.uz | Shifokor@2026 |

> Xavfsizlik: `--fixed-password` faqat demo/staging uchun. Ishlab chiqarishda
> `seed_demo`-ni default (random parol, terminalda chiqadi) rejimda ishlating
> yoki har shifokorga alohida parol o'rnating.

## Email (Brevo)

- Kalit: `BREVO_API_KEY` (`.env` / Render env var).
- OTP va regstratsiya tasdiqlash email'lari Brevo Transactional API orqali
  HTML brendli (Shifokorxona) shaklda yuboriladi.
- Brevo kalitisiz email `console` backend'ga tushadi (test uchun).

## Integratsiya

- Health-check: `GET /api/health/` — DB holati bilan (200/503).
- Doctor katalogi: `GET /api/doctors/` — qidiruv (`?search=`), filtr
  (`?specialty=`), tartiblash (`?ordering=`) ishlaydi.

## Deploy (Render)

`render.yaml` — backend (web) + PostgreSQL + oldend (static) — Render'da bir
marta deploy qilinadi; `BREVO_API_KEY` Render dashboard'da sozlanadi.
