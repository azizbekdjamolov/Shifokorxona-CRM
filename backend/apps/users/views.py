from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.users.permissions import IsSelfOrAdmin, IsAdminUser
from apps.users.serializers import (
    RegisterSerializer,
    VerifyOtpSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from apps.users.services.otp_service import issue_tokens_for_user

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if not settings.REGISTRATION_REQUIRE_EMAIL_VERIFY:
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])
            tokens = issue_tokens_for_user(user)
            return Response(
                {
                    "detail": "Ro'yxatdan o'tish muvaffaqiyatli",
                    "user": UserSerializer(user).data,
                    "tokens": tokens,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "detail": "Emailingizga tasdiqlash kodi yuborildi",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyOtpView(APIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOtpSerializer

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = issue_tokens_for_user(user)
        return Response(
            {
                "detail": "Email tasdiqlandi",
                "user": UserSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(instance).data)


class ResendOtpView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        from apps.users.services.otp_service import generate_otp, send_otp_email

        email = request.data.get("email")
        if not email:
            return Response({"email": "Email talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({"email": "Foydalanuvchi topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        otp = generate_otp(user, "email_verify")
        send_otp_email(otp)
        return Response({"detail": "Yangi kod yuborildi"}, status=status.HTTP_200_OK)


class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)
        return queryset


class AdminUserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        role = request.data.get("role")
        is_active = request.data.get("is_active")
        if role is not None:
            instance.role = role
        if is_active is not None:
            instance.is_active = bool(is_active)
        instance.save()
        return Response(UserSerializer(instance).data)