from rest_framework import serializers

from apps.chats.models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source="sender.id", read_only=True)
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "sender_id", "sender_name", "text", "is_read", "created_at"]
        read_only_fields = ["id", "conversation", "sender", "created_at", "is_read"]


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["text"]

    def create(self, validated_data):
        request = self.context["request"]
        conversation = self.context["conversation"]
        return Message.objects.create(
            conversation=conversation,
            sender=request.user,
            text=validated_data["text"],
        )


class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    doctor_user_id = serializers.IntegerField(source="doctor.user.id", read_only=True)
    doctor_name = serializers.CharField(source="doctor.user.get_full_name", read_only=True)
    specialty_name = serializers.CharField(source="doctor.specialty.name", read_only=True)
    patient_user_id = serializers.IntegerField(source="patient.id", read_only=True)
    patient_name = serializers.CharField(source="patient.get_full_name", read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "doctor",
            "doctor_user_id",
            "doctor_name",
            "specialty_name",
            "patient",
            "patient_user_id",
            "patient_name",
            "last_message",
            "unread_count",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if not msg:
            return None
        return {
            "id": msg.id,
            "text": msg.text,
            "sender_id": msg.sender_id,
            "sender_name": msg.sender.get_full_name(),
            "created_at": msg.created_at,
        }

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0
        return obj.messages.filter(is_read=False).exclude(sender=request.user).count()


class ConversationCreateSerializer(serializers.Serializer):
    doctor = serializers.IntegerField()

    def validate_doctor(self, value):
        from django.shortcuts import get_object_or_404

        from apps.doctors.models import Doctor

        return get_object_or_404(Doctor.objects.filter(is_active=True), pk=value)