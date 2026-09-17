from apps.bookings.services.booking_lock import expire_stale_holds


def expire_hold_bookings():
    return expire_stale_holds()