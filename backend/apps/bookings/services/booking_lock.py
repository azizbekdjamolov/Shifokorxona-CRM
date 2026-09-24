import logging

from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.utils import timezone

logger = logging.getLogger("apps.bookings")


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


def expire_hold_booking(booking):
    release_hold(booking.doctor_id, booking.date, booking.time)
    booking.status = booking.Status.CANCELLED
    booking.save(update_fields=["status"])


def expire_stale_holds():
    from apps.bookings.models import Booking

    stale = Booking.objects.filter(
        status=Booking.Status.HOLD,
        hold_expires_at__lte=timezone.now(),
    )
    count = 0
    for booking in stale:
        expire_hold_booking(booking)
        count += 1
    return count


def is_slot_available(doctor_id, booking_date, booking_time):
    expire_stale_holds()
    if is_slot_held(doctor_id, booking_date, booking_time):
        return False
    from apps.bookings.models import Booking

    return not Booking.objects.filter(
        doctor_id=doctor_id,
        date=booking_date,
        time=booking_time,
        status__in=[Booking.Status.HOLD, Booking.Status.CONFIRMED],
    ).exists()


@transaction.atomic
def create_booking_with_hold(user, doctor, date, time):
    """Bronni atomik yaratadi. DB-diagnostik noyob indeks double-booking ga qarshi
    kafolat beradi — bir vaqtning o'zida kelgan parallel so'rovlar ham buzilmaydi.

    Race holatda (2 ta parallel bron) IntegrityError ushlanib, xushomadli 400
    qaytariladi (500 o'rniga).
    """
    from apps.bookings.models import Booking

    hold_minutes = settings.BOOKING_HOLD_MINUTES
    key = _lock_key(doctor.id, date, time)

    # Eski muddati o'tgan HOLD bronlarni tozalaymiz
    expire_stale_holds()

    # Faol (HOLD/CONFIRMED) bron borligini tekshiramiz
    existing = Booking.objects.filter(
        doctor=doctor,
        date=date,
        time=time,
        status__in=[Booking.Status.HOLD, Booking.Status.CONFIRMED],
    ).exists()
    if existing:
        return None, {"time": "Bu vaqt allaqachon band"}

    try:
        booking = Booking.objects.create(
            doctor=doctor,
            date=date,
            time=time,
            user=user,
            status=Booking.Status.HOLD,
            hold_expires_at=timezone.now() + timezone.timedelta(minutes=hold_minutes),
        )
    except IntegrityError:
        return None, {"time": "Bu vaqt allaqachon band"}

    cache.set(key, "1", timeout=hold_minutes * 60)
    return booking, None