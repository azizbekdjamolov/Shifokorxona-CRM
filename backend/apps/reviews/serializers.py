from rest_framework import serializers

from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.get_full_name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "booking",
            "doctor",
            "patient",
            "patient_name",
            "rating",
            "text",
            "status",
            "created_at",
        ]
        read_only_fields = ["doctor", "patient", "status"]


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["booking", "rating", "text"]

    def validate(self, attrs):
        booking = attrs["booking"]
        if Review.objects.filter(booking=booking).exists():
            raise serializers.ValidationError({"booking": "Bu bron uchun sharh allaqachon qoldirilgan"})
        if booking.user_id != self.context["request"].user.id:
            raise serializers.ValidationError({"booking": "Bu bron sizga tegishli emas"})
        if booking.status != "completed":
            raise serializers.ValidationError({"booking": "Sharh faqat yakunlangan bron uchun qoldiriladi"})
        return attrs

    def create(self, validated_data):
        booking = validated_data["booking"]
        review = Review.objects.create(
            **validated_data,
            doctor_id=booking.doctor_id,
            patient_id=booking.user_id,
        )
        return review


class ReviewModerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["status"]

    def validate_status(self, value):
        if value not in [Review.Moderation.APPROVED, Review.Moderation.REJECTED]:
            raise serializers.ValidationError("Faqat tasdiqlash yoki rad etish mumkin")
        return value

    def update(self, instance, validated_data):
        instance.status = validated_data["status"]
        instance.save()
        if instance.status == Review.Moderation.APPROVED:
            instance.update_doctor_rating()
        return instance