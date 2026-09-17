from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.doctors.models import Doctor, DoctorSchedule, Specialty
from apps.users.serializers import UserSerializer

User = get_user_model()


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ["id", "name", "slug", "description", "icon"]


class DoctorScheduleSerializer(serializers.ModelSerializer):
    weekday_name = serializers.CharField(source="get_weekday_display", read_only=True)

    class Meta:
        model = DoctorSchedule
        fields = ["id", "doctor", "weekday", "weekday_name", "start_time", "end_time", "is_working"]
        read_only_fields = ["doctor"]


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specialty_name = serializers.CharField(source="specialty.name", read_only=True)
    schedule = DoctorScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = [
            "id",
            "user",
            "specialty",
            "specialty_name",
            "bio",
            "experience_years",
            "price",
            "photo",
            "average_rating",
            "is_active",
            "schedule",
        ]


class DoctorCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Doctor
        fields = [
            "user_id",
            "specialty",
            "bio",
            "experience_years",
            "price",
            "photo",
            "is_active",
        ]

    def validate_user_id(self, value):
        user = User.objects.filter(pk=value).first()
        if not user:
            raise serializers.ValidationError("Foydalanuvchi topilmadi")
        if Doctor.objects.filter(user_id=value).exists():
            raise serializers.ValidationError("Bu foydalanuvchi allaqachon shifokor profili bor")
        return value

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        user = User.objects.get(pk=user_id)
        user.role = User.Role.DOCTOR
        user.save(update_fields=["role"])
        return Doctor.objects.create(user_id=user_id, **validated_data)