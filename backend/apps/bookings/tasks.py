from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.bookings.models import Booking


@shared_task
def expire_hold_bookings():
    expired = Booking.objects.filter(
        status=Booking.Status.HOLD,
        hold_expires_at__lte=timezone.now(),
    ).select_related("doctor", "user")
    released = 0
    for booking in expired:
        from apps.bookings.services.booking_lock import release_hold

        release_hold(booking.doctor_id, booking.date, booking.time)
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status"])
        released += 1
    return f"{released} ta hold bron bekor qilindi"


@shared_task
def clean_stale_holds():
    Booking.objects.filter(
        status=Booking.Status.HOLD,
        hold_expires_at__lte=timezone.now() - timedelta(days=1),
    ).delete()