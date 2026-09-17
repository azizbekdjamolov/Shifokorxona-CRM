from rest_framework import serializers
from django.utils import timezone

from apps.bookings.models import Booking
from apps.doctors.serializers import DoctorSerializer


class BookingSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    patient_name = serializers.CharField(source="user.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "user",
            "patient_name",
            "doctor",
            "date",
            "time",
            "status",
            "status_display",
            "hold_expires_at",
            "is_hold_expired",
            "created_at",
        ]
        read_only_fields = ["user"]


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["doctor", "date", "time"]

    def validate(self, attrs):
        doctor = attrs["doctor"]
        date = attrs["date"]
        time = attrs["time"]

        if date < timezone.now().date():
            raise serializers.ValidationError({"date": "O'tgan sanaga bron qilib bo'lmaydi"})

        occupied = Booking.objects.filter(
            doctor=doctor,
            date=date,
            time=time,
            status__in=[Booking.Status.HOLD, Booking.Status.CONFIRMED],
        ).exclude(
            status=Booking.Status.HOLD,
            hold_expires_at__lte=timezone.now(),
        )
        if occupied.exists():
            raise serializers.ValidationError({"time": "Bu vaqt allaqachon band"})
        return attrs

    def create(self, validated_data):
        booking = Booking.objects.create(
            **validated_data,
            user=self.context["request"].user,
            status=Booking.Status.HOLD,
            hold_expires_at=timezone.now() + timezone.timedelta(minutes=5),
        )
        return booking


class BookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["status"]

    def validate_status(self, value):
        booking = self.instance
        allowed = Booking.STATUS_FLOW.get(booking.status, [])
        if value not in allowed:
            raise serializers.ValidationError(
                f"'{booking.status}' holatidan '{value}' holatiga o'tib bo'lmaydi"
            )
        return value

    def update(self, instance, validated_data):
        instance.status = validated_data["status"]
        if instance.status == Booking.Status.CONFIRMED:
            instance.hold_expires_at = None
        instance.save()
        return instance