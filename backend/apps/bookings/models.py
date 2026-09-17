from django.db import models
from django.conf import settings
from django.utils import timezone


class Booking(models.Model):
    class Status(models.TextChoices):
        HOLD = "hold", "Vaqtinchalik band"
        CONFIRMED = "confirmed", "Tasdiqlangan"
        COMPLETED = "completed", "Yakunlangan"
        CANCELLED = "cancelled", "Bekor qilingan"

    STATUS_FLOW = {
        Status.HOLD: [Status.CONFIRMED, Status.CANCELLED],
        Status.CONFIRMED: [Status.COMPLETED, Status.CANCELLED],
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    doctor = models.ForeignKey(
        "doctors.Doctor", on_delete=models.CASCADE, related_name="bookings"
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.HOLD
    )
    hold_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bron"
        verbose_name_plural = "Bronlar"
        ordering = ["-date", "-time"]
        indexes = [
            models.Index(fields=["doctor", "date", "time"]),
            models.Index(fields=["status", "hold_expires_at"]),
        ]

    def __str__(self):
        return f"{self.user} -> {self.doctor} {self.date} {self.time}"

    @property
    def is_hold_expired(self):
        if self.status != self.Status.HOLD or not self.hold_expires_at:
            return False
        return self.hold_expires_at <= timezone.now()