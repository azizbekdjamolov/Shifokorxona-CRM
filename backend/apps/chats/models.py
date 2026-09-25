from django.conf import settings
from django.db import models


class Conversation(models.Model):
    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Suhbat"
        verbose_name_plural = "Suhbatlar"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "patient"],
                name="unique_conversation_doctor_patient",
            )
        ]

    def __str__(self):
        return f"{self.doctor} <-> {self.patient}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender} -> {self.conversation}: {self.text[:40]}"