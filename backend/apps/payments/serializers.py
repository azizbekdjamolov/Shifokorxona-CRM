from rest_framework import serializers

from apps.payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source="get_provider_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "booking",
            "amount",
            "provider",
            "provider_display",
            "status",
            "status_display",
            "transaction_id",
            "created_at",
            "updated_at",
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["booking", "provider"]

    def validate_provider(self, value):
        try:
            return Payment.Provider(value)
        except ValueError:
            raise serializers.ValidationError("Noto'g'ri to'lov provayderi")

    def validate_booking(self, booking):
        doctor = getattr(booking, "doctor", None)
        if not doctor or not doctor.price:
            raise serializers.ValidationError("Bu bron uchun narx belgilanmagan")
        return booking

    def validate(self, attrs):
        booking = attrs["booking"]
        if booking.status != booking.Status.CONFIRMED:
            raise serializers.ValidationError(
                {"booking": "Faqat tasdiqlangan bronlar uchun to'lov qabul qilinadi"}
            )
        return attrs