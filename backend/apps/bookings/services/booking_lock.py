from datetime import date

from django.conf import settings
from django.core.cache import cache


def _lock_key(doctor_id, booking_date, booking_time):
    return f"booking_hold:{doctor_id}:{booking_date}:{booking_time}"


def create_hold(doctor_id, booking_date, booking_time, hold_minutes=None):
    hold_minutes = hold_minutes or settings.BOOKING_HOLD_MINUTES
    key = _lock_key(doctor_id, booking_date, booking_time)
    added = cache.add(key, "1", timeout=hold_minutes * 60)
    return added


def release_hold(doctor_id, booking_date, booking_time):
    cache.delete(_lock_key(doctor_id, booking_date, booking_time))


def is_slot_held(doctor_id, booking_date, booking_time):
    return cache.get(_lock_key(doctor_id, booking_date, booking_time)) is not None


def is_slot_available(doctor_id, booking_date, booking_time):
    if is_slot_held(doctor_id, booking_date, booking_time):
        return False
    from apps.bookings.models import Booking

    return not Booking.objects.filter(
        doctor_id=doctor_id,
        date=booking_date,
        time=booking_time,
        status__in=[Booking.Status.HOLD, Booking.Status.CONFIRMED],
    ).exists()