import os
import threading
import time

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()


def _booking_reminder_loop():
    """Har 60 soniyada navbatiga 5 daqiqa qolgan bronlarga email yuboradi.

    Render free planda alohida worker/cron yaratib bo'lmaydi, shuning uchun
    gunicorn (--workers 1) bilan birga daemon thread ishga tushadi.
    """
    from apps.bookings.services.reminder_service import send_due_reminders

    while True:
        try:
            send_due_reminders()
        except Exception:  # noqa: BLE001
            pass
        time.sleep(60)


threading.Thread(
    target=_booking_reminder_loop,
    name="booking-reminder-loop",
    daemon=True,
).start()