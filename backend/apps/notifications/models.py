from django.db import models
from django.conf import settings


class Notification(models.Model):
    class Type(models.TextChoices):
        MEDICATION_REMINDER = "medication", "Dori eslatmasi"
        BOOKING_REMINDER = "booking", "Bron eslatmasi"
        TELEGRAM_LINK = "telegram_link", "Telegram ulanish"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=20, choices=Type.choices)
    message = models.TextField()
    chat_id = models.BigIntegerField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Bildirishnoma"
        verbose_name_plural = "Bildirishnomalar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_type_display()} -> {self.user} ({self.is_sent})"