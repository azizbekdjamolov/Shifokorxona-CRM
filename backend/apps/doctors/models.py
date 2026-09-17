from django.db import models
from django.conf import settings


class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mutaxassislik"
        verbose_name_plural = "Mutaxassisliklar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )
    specialty = models.ForeignKey(
        Specialty, on_delete=models.SET_NULL, null=True, related_name="doctors"
    )
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    photo = models.ImageField(upload_to="doctors/", blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Shifokor"
        verbose_name_plural = "Shifokorlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.email}"


class DoctorSchedule(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Dushanba"
        TUESDAY = 1, "Seshanba"
        WEDNESDAY = 2, "Chorshanba"
        THURSDAY = 3, "Payshanba"
        FRIDAY = 4, "Juma"
        SATURDAY = 5, "Shanba"
        SUNDAY = 6, "Yakshanba"

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="schedule")
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_working = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ish jadvali"
        verbose_name_plural = "Ish jadvallari"
        unique_together = ("doctor", "weekday")
        ordering = ["weekday", "start_time"]

    def __str__(self):
        return f"{self.doctor} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"