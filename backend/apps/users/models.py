from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings

import random

from django.conf import settings


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "patient", "Bemor"
        DOCTOR = "doctor", "Shifokor"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.PATIENT
    )
    phone = models.CharField(max_length=20, blank=True)
    is_email_verified = models.BooleanField(default=False)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def __str__(self):
        return self.get_full_name() or self.username or self.email


class OTP(models.Model):
    class Purpose(models.TextChoices):
        EMAIL_VERIFY = "email_verify", "Email tasdiqlash"
        PASSWORD_RESET = "password_reset", "Parol tiklash"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps"
    )
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    is_used = models.BooleanField(default=False)
    failed_attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "OTP kod"
        verbose_name_plural = "OTP kodlar"
        indexes = [
            models.Index(fields=["purpose", "is_used", "expires_at"]),
        ]

    def is_valid(self):
        return (
            not self.is_used
            and self.expires_at > timezone.now()
            and self.failed_attempts < settings.OTP_MAX_ATTEMPTS
        )

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"{random.randint(0, 999999):06d}"
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(
                minutes=settings.OTP_EXPIRATION_MINUTES
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OTP {self.purpose} - {self.user.email}"