from datetime import timedelta

from django.utils import timezone

from apps.notifications.bot import send_telegram_message
from apps.notifications.models import Notification
from apps.prescriptions.models import Prescription

WAKE_HOUR_START = 8
WAKE_HOUR_END = 22


def compute_dose_times(prescription):
    total_minutes = (WAKE_HOUR_END - WAKE_HOUR_START) * 60
    count = prescription.times_per_day
    if count <= 1:
        intervals = [0]
    else:
        step = total_minutes // count
        intervals = [min(i * step, total_minutes) for i in range(count)]
    times = []
    for minutes in intervals:
        hour = WAKE_HOUR_START + minutes // 60
        minute = minutes % 60
        times.append(f"{hour:02d}:{minute:02d}")
    return times


def _save_notification(user, message, type_, chat_id, is_sent):
    Notification.objects.create(
        user=user,
        type=type_,
        message=message,
        chat_id=chat_id,
        is_sent=is_sent,
        sent_at=timezone.now() if is_sent else None,
    )


def send_due_medication_reminders():
    now = timezone.now()
    today = now.date()
    current_key = now.strftime("%H:%M")
    sent_count = 0

    prescriptions = Prescription.objects.filter(
        created_at__date__lte=today,
    ).select_related("patient", "doctor")

    for prescription in prescriptions:
        start = prescription.created_at.date()
        course_end = start + timedelta(days=prescription.days)
        if not (start <= today < course_end):
            continue

        dose_times = compute_dose_times(prescription)
        if current_key not in dose_times:
            continue

        from django.core.cache import cache

        cache_key = f"rx_reminder:{prescription.id}:{today}:{current_key}"
        if cache.get(cache_key):
            continue
        cache.set(cache_key, "1", timeout=3600)

        chat_id = prescription.patient.telegram_chat_id
        message = (
            f"💊 Dori eslatmasi!\n\n"
            f"Preparat: {prescription.medicine_name}\n"
            f"Izoh: {prescription.instruction}\n"
            f"Shifokor: Dr. {prescription.doctor.user.get_full_name()}\n"
            f"Vaqt: {current_key}"
        )
        is_sent = send_telegram_message(chat_id, message)
        _save_notification(
            user=prescription.patient,
            message=message,
            type_=Notification.Type.MEDICATION_REMINDER,
            chat_id=chat_id,
            is_sent=is_sent,
        )
        if is_sent:
            sent_count += 1

    return f"{sent_count} ta dori eslatmasi yuborildi"