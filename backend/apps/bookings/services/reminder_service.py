"""Navbat eslatmalari xizmati.

Confirmed bron vaqti kelguniga 5 daqiqa qolganda bemorga email yuboradi.
Faqat bir marta yuboriladi (reminder_sent_at to'ldiriladi).
"""

from datetime import datetime

from django.utils import timezone

from apps.bookings.models import Booking
from apps.users.services.email_service import (
    build_booking_reminder_html,
    send_transactional_email,
)

REMINDER_MINUTES_BEFORE = 5
WINDOW_MINUTES = 30


def _booking_datetime(booking):
    return timezone.make_aware(
        datetime.combine(booking.date, booking.time),
        timezone.get_current_timezone(),
    )


def send_due_reminders():
    """Navbatiga 5 daqiqa qolgan confirmed bronlarga email yuboradi.

    Bir necha marta ishga tushirilsa ham har bron faqat bir marta
    eslatiladi — email muvaffaqiyatli yuborilsagina reminder_sent_at
    o'rnatiladi. Qaytaradi: yuborildi_count.
    """
    now = timezone.now()
    sent = 0
    for booking in Booking.objects.filter(
        status=Booking.Status.CONFIRMED,
        reminder_sent_at__isnull=True,
    ).select_related("user", "doctor", "doctor__user", "doctor__specialty"):
        if booking.date != timezone.localdate():
            continue
        book_dt = _booking_datetime(booking)
        # Vaqt kelguniga 5 daqiqa qolganda yuboramiz (3-10 daqiqa oralig'ida,
        # TimeField sekundlarni kesishi sababli biroz keng tolantz olamiz).
        minutes_left = (book_dt - now).total_seconds() / 60
        if not (3 <= minutes_left <= REMINDER_MINUTES_BEFORE + 5):
            continue

        ok = _send_reminder(booking)
        if ok:
            booking.reminder_sent_at = now
            booking.save(update_fields=["reminder_sent_at"])
            sent += 1
    return sent


def _send_reminder(booking):
    patient = booking.user
    doctor = booking.doctor
    patient_name = patient.get_full_name() or patient.email
    html = build_booking_reminder_html(
        patient_name=patient_name,
        doctor_name=f"Dr. {doctor.user.get_full_name() or doctor.user.email}",
        specialty_name=doctor.specialty.name if doctor.specialty else "",
        date_str=booking.date.strftime("%d.%m.%Y"),
        time_str=booking.time.strftime("%H:%M"),
    )
    return send_transactional_email(
        to_email=patient.email,
        subject="Navbatingizga 5 daqiqa qoldi!",
        html_body=html,
    )