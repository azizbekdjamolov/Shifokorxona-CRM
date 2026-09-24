from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.users.services.otp_service import generate_otp, send_otp_email

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "email", "password", "confirm_password"]
        extra_kwargs = {"email": {"required": True}}

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value.lower()).exists():
            raise serializers.ValidationError("Bu email allaqachon ro'yxatdan o'tgan")
        return value.lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Parollar bir xil emas"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(
            username=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone=validated_data.get("phone", ""),
            email=validated_data["email"],
            password=validated_data["password"],
        )
        otp = generate_otp(user, "email_verify")
        if settings.REGISTRATION_REQUIRE_EMAIL_VERIFY:
            send_otp_email(otp)
        return user


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        from apps.users.services.otp_service import verify_otp

        user = User.objects.filter(email__iexact=attrs["email"]).first()
        if not user:
            raise serializers.ValidationError({"email": "Foydalanuvchi topilmadi"})
        if not verify_otp(user, attrs["code"]):
            raise serializers.ValidationError({"code": "Noto'g'ri yoki muddati o'tgan kod"})
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "role",
            "is_email_verified",
            "telegram_chat_id",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email


class UserUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "current_password",
            "password",
            "confirm_password",
        ]

    def validate(self, attrs):
        current = attrs.get("current_password")
        password = attrs.get("password")
        confirm = attrs.get("confirm_password")
        if password or confirm or current:
            if not current:
                raise serializers.ValidationError({"current_password": "Joriy parolni kiriting"})
            if not self.instance.check_password(current):
                raise serializers.ValidationError({"current_password": "Joriy parol noto'g'ri"})
            if password != confirm:
                raise serializers.ValidationError({"confirm_password": "Parollar bir xil emas"})
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        validated_data.pop("current_password", None)
        validated_data.pop("confirm_password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance