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
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)

    class Meta:
        model = Booking
        fields = ["doctor", "date", "time", "first_name", "last_name", "phone"]

    def validate(self, attrs):
        doctor = attrs["doctor"]
        date = attrs["date"]
        time = attrs["time"]

        from apps.bookings.services.booking_lock import is_slot_available

        if date < timezone.localdate():
            raise serializers.ValidationError({"date": "O'tgan sanaga bron qilib bo'lmaydi"})

        # Shifokor ish jadvaliga mos kelishini tekshiramiz.
        # Jadval umuman bo'lmasa — default 07:00-21:00.
        # Jadval bo'lsa — faqat ish soatlari; dam olish kuniga bron qilib bo'lmaydi.
        from datetime import time as time_type

        schedules = list(doctor.schedule.filter(weekday=date.weekday()))
        has_schedule = doctor.schedule.exists()
        if has_schedule:
            working = [s for s in schedules if s.is_working]
            if not working:
                raise serializers.ValidationError(
                    {"time": "Shifokor bu kuni ishlamaydi"}
                )
            slot = working[0]
            if not (slot.start_time <= time < slot.end_time):
                raise serializers.ValidationError(
                    {"time": "Shifokor ish vaqtidan tashqari vaqt tanlangesiz"}
                )
        elif not (time_type(7, 0) <= time < time_type(21, 0)):
            raise serializers.ValidationError(
                {"time": "Qabul 07:00 dan 21:00 gacha"}
            )

        if not is_slot_available(doctor.id, date, time):
            raise serializers.ValidationError({"time": "Bu vaqt allaqachon band"})
        return attrs

    def create(self, validated_data):
        from apps.bookings.services.booking_lock import create_booking_with_hold

        user = self.context["request"].user
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")
        phone = validated_data.pop("phone", "")

        if first_name or last_name or phone:
            update_fields = []
            if first_name and first_name != user.first_name:
                user.first_name = first_name
                update_fields.append("first_name")
            if last_name and last_name != user.last_name:
                user.last_name = last_name
                update_fields.append("last_name")
            if phone and phone != user.phone:
                user.phone = phone
                update_fields.append("phone")
            if update_fields:
                user.save(update_fields=update_fields)

        doctor = validated_data["doctor"]
        date = validated_data["date"]
        time = validated_data["time"]
        booking, error = create_booking_with_hold(
            user=user,
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