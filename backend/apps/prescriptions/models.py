from django.db import models


class Prescription(models.Model):
    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.SET_NULL,
        null=True,
        related_name="prescriptions",
    )
    doctor = models.ForeignKey(
        "doctors.Doctor", on_delete=models.CASCADE, related_name="prescriptions"
    )
    patient = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="prescriptions"
    )
    medicine_name = models.CharField(max_length=200)
    instruction = models.TextField()
    times_per_day = models.PositiveIntegerField(default=1)
    days = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to="medicines/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Retsept"
        verbose_name_plural = "Retseptlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.medicine_name} - {self.patient.get_full_name()} ({self.days} kun)"