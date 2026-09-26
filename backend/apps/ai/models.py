from django.conf import settings
from django.db import models


class AIConversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI suhbat"
        verbose_name_plural = "AI suhbatlar"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"AI suhbat - {self.user}"


class AIMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Foydalanuvchi"
        ASSISTANT = "assistant", "AI yordamchi"

    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    text = models.TextField(blank=True)
    # Rasm fayl shaklida media saqlanadi — bazaga base64 string emas.
    image = models.ImageField(upload_to="ai/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "AI xabar"
        verbose_name_plural = "AI xabarlar"
        ordering = ["created_at"]

    def __str__(self):
        prefix = self.text[:40] if self.text else "(rasm)"
        return f"{self.get_role_display()}: {prefix}"