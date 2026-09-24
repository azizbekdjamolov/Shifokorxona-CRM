from rest_framework import serializers
from django.utils import timezone

from apps.bookings.models import Booking
from apps.doctors.serializers import DoctorSerializer
from apps.bookings.services.booking_lock import release_hold


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

        from apps.bookings.services.booking_lock import is_slot_available

        if date < timezone.localdate():
            raise serializers.ValidationError({"date": "O'tgan sanaga bron qilib bo'lmaydi"})

        if not is_slot_available(doctor.id, date, time):
            raise serializers.ValidationError({"time": "Bu vaqt allaqachon band"})
        return attrs

    def create(self, validated_data):
        from apps.bookings.services.booking_lock import create_booking_with_hold

        doctor = validated_data["doctor"]
        date = validated_data["date"]
        time = validated_data["time"]
        booking, error = create_booking_with_hold(
            user=self.context["request"].user,
            doctor=doctor,
            date=date,
            time=time,
        )
        if error:
            raise serializers.ValidationError(error)
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
        if (
            booking.status == Booking.Status.HOLD
            and value == Booking.Status.CONFIRMED
            and booking.is_hold_expired
        ):
            raise serializers.ValidationError(
                "Vaqtinchalik bandlik (5 daqiqa) muddati o'tgan — "
                "bronni bekor qilib, qayta bron qiling"
            )
        return value

    def update(self, instance, validated_data):
        instance.status = validated_data["status"]
        if instance.status == Booking.Status.CONFIRMED:
            instance.hold_expires_at = None
            release_hold(
                instance.doctor_id,
                instance.date,
                instance.time,
            )
        elif instance.status == Booking.Status.CANCELLED:
            release_hold(
                instance.doctor_id,
                instance.date,
                instance.time,
            )
        instance.save()
        return instance