from rest_framework import serializers

from apps.ai.models import AIMessage


class AIMessageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AIMessage
        fields = ["id", "role", "text", "image", "image_url", "created_at"]
        read_only_fields = ["id", "role", "text", "image", "created_at"]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class AIChatSerializer(serializers.Serializer):
    message = serializers.CharField(allow_blank=True, default="")
    image = serializers.ImageField(required=False, allow_null=True)
    language = serializers.ChoiceField(
        choices=["uz", "ru", "en"], default="uz", required=False
    )

    def validate(self, attrs):
        if not attrs.get("message", "").strip() and not attrs.get("image"):
            raise serializers.ValidationError("Xabar yoki rasm yuborishingiz kerak")
        return attrs