from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    class Moderation(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        APPROVED = "approved", "Tasdiqlangan"
        REJECTED = "rejected", "Rad etilgan"

    booking = models.OneToOneField(
        "bookings.Booking", on_delete=models.CASCADE, related_name="review"
    )
    doctor = models.ForeignKey(
        "doctors.Doctor", on_delete=models.CASCADE, related_name="reviews"
    )
    patient = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=Moderation.choices, default=Moderation.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rating}⭐ - {self.doctor} - {self.patient.get_full_name()}"

    def update_doctor_rating(self):
        from django.db.models import Avg

        avg = (
            Review.objects.filter(
                doctor=self.doctor, status=Review.Moderation.APPROVED
            ).aggregate(value=Avg("rating"))["value"]
            or 0
        )
        self.doctor.average_rating = round(avg, 2)
        self.doctor.save(update_fields=["average_rating"])