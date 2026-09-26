"""Shifoxona CRM real ma'lumotlarini AI modeli uchun kontekstga aylantiradi.

Hech qanday ma'lumot hardcode qilinmaydi — barchasi DB'dan o'qiladi.
AI faqat shu kontekstga tayanib jamoaviy ma'lumot beradi.
"""

import json

from django.utils import timezone

from apps.bookings.models import Booking
from apps.doctors.models import Doctor, Specialty
from apps.prescriptions.models import Prescription


def _doctors_context():
    doctors = (
        Doctor.objects.filter(is_active=True)
        .select_related("user", "specialty")
        .order_by("specialty__name")
    )
    rows = []
    for d in doctors:
        rows.append(
            {
                "id": d.id,
                "name": d.user.get_full_name() or d.user.email,
                "specialty": d.specialty.name if d.specialty else None,
                "experience_years": d.experience_years,
                "price": str(d.price),
                "rating": str(d.average_rating),
            }
        )
    return {"doctors": rows}


def _specialties_context():
    return {
        "specialties": [
            {"name": s.name, "slug": s.slug}
            for s in Specialty.objects.all().order_by("name")
        ]
    }


def _bookings_context(user):
    if user.role not in ("patient",):
        return {}
    bookings = (
        Booking.objects.filter(user=user)
        .exclude(status=Booking.Status.CANCELLED)
        .select_related("doctor", "doctor__user", "doctor__specialty")
        .order_by("-date", "-time")[:10]
    )
    rows = []
    for b in bookings:
        rows.append(
            {
                "id": b.id,
                "doctor": b.doctor.user.get_full_name() or b.doctor.user.email,
                "specialty": (
                    b.doctor.specialty.name if b.doctor.specialty else None
                ),
                "date": b.date.isoformat(),
                "time": b.time.strftime("%H:%M"),
                "status": b.status,
            }
        )
    return {"my_bookings": rows}


def _prescriptions_context(user):
    if user.role not in ("patient",):
        return {}
    prescriptions = (
        Prescription.objects.filter(patient=user)
        .select_related("doctor", "doctor__user")
        .order_by("-created_at")[:10]
    )
    rows = []
    for p in prescriptions:
        rows.append(
            {
                "id": p.id,
                "doctor": p.doctor.user.get_full_name() or p.doctor.user.email,
                "medicine_name": p.medicine_name,
                "instruction": p.instruction,
                "times_per_day": p.times_per_day,
                "days": p.days,
            }
        )
    return {"my_prescriptions": rows}


def _doctor_panel_context(user):
    if user.role != "doctor":
        return {}
    try:
        me = Doctor.objects.get(user=user)
    except Doctor.DoesNotExist:
        return {}
    today = timezone.localdate()
    today_count = Booking.objects.filter(
        doctor=me, date=today
    ).exclude(status=Booking.Status.CANCELLED).count()
    upcoming = Booking.objects.filter(
        doctor=me, date__gte=today
    ).exclude(status=Booking.Status.CANCELLED).count()
    return {
        "my_doctor_panel": {
            "specialty": me.specialty.name if me.specialty else None,
            "today_visits_count": today_count,
            "upcoming_total": upcoming,
        }
    }


def build_crm_context(user):
    """Foydalanuvchining rolidan kelib chiqib AI uchun ma'lumot moduli qaytaradi."""
    context = {}
    context.update(_specialties_context())
    context.update(_doctors_context())
    context.update(_bookings_context(user))
    context.update(_prescriptions_context(user))
    context.update(_doctor_panel_context(user))
    context["clinic"] = {
        "name": "Shifokorxona CRM",
        "intro": (
            "Klinika onlayn shifokorga yozilish, navbat va e-retsept "
            "xizmatlarini taqdim etadi."
        ),
    }
    return context


def context_to_json(user, lang="uz"):
    context = build_crm_context(user)
    hint = {
        "uz": (
            "Quyidagi Shifokorxona CRM ma'lumotlari shu daqiqadagi bazadan "
            "olingan (real). Bemorning shaxsiy ma'lumotlari faqat o'sha user "
            "ko'rsatilgan. Javobingni shu tilga mos yoz."
        ),
        "ru": (
            "Ниже приведены актуальные данные из CRM Shifokorxona (реальные). "
            "Отвечай на языке пользователя."
        ),
        "en": (
            "Below is the real, current Shifokorxona CRM data. "
            "Answer in the user's language."
        ),
    }[lang]
    return f"{hint}\n\n{json.dumps(context, ensure_ascii=False)}"