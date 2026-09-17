from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.serializers import PasswordField
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class EmailTokenObtainPairSerializer(serializers.Serializer):
    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = serializers.CharField(required=False, default="")
        self.fields["username"] = serializers.CharField(required=False, default="")
        self.fields["password"] = PasswordField()

    def validate(self, attrs):
        data = {}
        email = attrs.get("email") or attrs.get("username") or ""
        email = email.strip().lower()
        if not email:
            raise serializers.ValidationError({"email": "Email kiritilishi shart"})
        user = User.objects.filter(email__iexact=email).first()
        if not user or not user.check_password(attrs.get("password", "")):
            raise serializers.ValidationError("Email yoki parol noto'g'ri")
        if not user.is_active:
            raise serializers.ValidationError("Foydalanuvchi faol emas")
        refresh = RefreshToken.for_user(user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        update_last_login(None, user)
        return data