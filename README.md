# Shifokorxona CRM

Bemorlar (user), shifokorlar va admin uchun onlayn navbat/bron tizimi, dori yozish (retsept) va Telegram bot orqali eslatma funksiyalariga ega klinika boshqaruv tizimi.

## Qisqacha

- **User** — shifokorlarni ko'radi, yo'nalish bo'yicha qidiradi, bron qiladi, navbatini va retseptlarini kuzatadi, sharh qoldiradi.
- **Shifokor** — o'z navbatini ko'radi, ish jadvalini belgilaydi, bemorga dori yozadi.
- **Admin** — userlar, shifokorlar, yo'nalishlar va bronlarni boshqaradi.

Bron 5 daqiqalik vaqtinchalik bandlik (hold) bilan ishlaydi, login faqat bron bosqichida so'raladi, register email OTP orqali tasdiqlanadi, dori vaqti kelganda Telegram bot orqali eslatma keladi, 2 mode (light/dark) va 3 til (uz/ru/en) qo'llab-quvvatlanadi.

## Fayllar strukturasi

```
shifokorxona-crm/
├── backend/                        # Django + DRF
│   ├── config/                     # asosiy sozlamalar (settings, urls, celery)
│   └── apps/
│       ├── users/                  # auth, rollar, OTP
│       ├── doctors/                # shifokor, mutaxassislik, ish jadvali
│       ├── bookings/                # bron/navbat + 5 daqiqalik hold logikasi
│       ├── prescriptions/          # dori yozish (retsept)
│       ├── reviews/                # reyting va sharh
│       └── notifications/          # Telegram bot orqali eslatma
│
└── frontend/                       # React
    └── src/
        ├── api/                     # backend bilan bog'lanish (so'rovlar)
        ├── routes/                  # public / user / doctor / admin yo'nalishlari
        ├── pages/
        │   ├── public/              # login shart bo'lmagan sahifalar
        │   ├── auth/                # login, register, OTP tasdiqlash
        │   ├── user/                # bemor paneli (navbat, retsept, sharh)
        │   ├── doctor/              # shifokor paneli (navbat, dori yozish, jadval)
        │   └── admin/               # admin paneli (userlar, shifokorlar, bronlar)
        ├── components/              # umumiy qismlar, tema va til almashtirish
        ├── context/                 # auth va tema holati
        └── locales/                 # uz / ru / en tarjimalar
```

**Qisqa izoh:** `backend` — har bir bo'lim (users, bookings, prescriptions va h.k.) alohida Django app sifatida ajratilgan, shu bilan har bir funksiya mustaqil rivojlantiriladi. `frontend` esa 3 xil panel (user/doctor/admin) uchun alohida sahifalar va yo'nalishlarga bo'lingan, umumiy qismlar (tema, til, komponentlar) barcha panellarda qayta ishlatiladi.