from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.users.models import OTP


def generate_otp(user, purpose=OTP.Purpose.EMAIL_VERIFY):
    OTP.objects.filter(user=user, purpose=purpose).delete()
    otp = OTP.objects.create(
        user=user,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES),
    )
    return otp


def verify_otp(user, code, purpose=OTP.Purpose.EMAIL_VERIFY):
    otp = OTP.objects.filter(user=user, purpose=purpose, code=code).order_by("-created_at").first()
    if otp and otp.is_valid():
        otp.is_used = True
        otp.save(update_fields=["is_used"])
        return True
    return False


def send_otp_email(otp):
    from django.core.mail import send_mail

    send_mail(
        subject="Shifokorxona CRM — tasdiqlash kodi",
        message=f"Emailingizni tasdiqlash uchun kod: {otp.code}. Kod {settings.OTP_EXPIRATION_MINUTES} daqiqa amal qiladi.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[otp.user.email],
        fail_silently=True,
    )


def issue_tokens_for_user(user):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }