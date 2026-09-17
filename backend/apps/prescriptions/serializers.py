from rest_framework import serializers

from apps.prescriptions.models import Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = [
            "id",
            "booking",
            "doctor",
            "doctor_name",
            "patient",
            "patient_name",
            "medicine_name",
            "instruction",
            "times_per_day",
            "days",
            "image",
            "created_at",
        ]
        read_only_fields = ["doctor", "patient", "created_at"]

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name() or obj.doctor.user.email}"

    def get_patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.email


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = [
            "booking",
            "medicine_name",
            "instruction",
            "times_per_day",
            "days",
            "image",
        ]

    def validate(self, attrs):
        doctor = self.context["request"].user.doctor_profile
        booking = attrs["booking"]
        if booking.doctor_id != doctor.id:
            raise serializers.ValidationError({"booking": "Bu bron boshqa shifokorga tegishli"})
        if booking.status != "completed":
            raise serializers.ValidationError({"booking": "Retsept faqat yakunlangan bron uchun yoziladi"})
        attrs["doctor"] = doctor
        attrs["patient"] = booking.user
        return attrs