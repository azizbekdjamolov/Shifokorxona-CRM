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
    otp = (
        OTP.objects.filter(user=user, purpose=purpose, is_used=False)
        .exclude(expires_at__lte=timezone.now())
        .order_by("-created_at")
        .first()
    )
    if not otp:
        return False
    if otp.code == code:
        otp.is_used = True
        otp.save(update_fields=["is_used"])
        return True
    max_attempts = getattr(settings, "OTP_MAX_ATTEMPTS", 5)
    if otp.failed_attempts < max_attempts - 1:
        otp.failed_attempts += 1
        otp.save(update_fields=["failed_attempts"])
    else:
        otp.expires_at = timezone.now()
        otp.save(update_fields=["expires_at"])
    return False


def send_otp_email(otp, cta_url=""):
    from apps.users.services.email_service import build_otp_html, send_transactional_email

    minutes = getattr(settings, "OTP_EXPIRATION_MINUTES", 10)
    html_body = build_otp_html(code=otp.code, minutes=minutes, cta_url=cta_url)
    send_transactional_email(to_email=otp.user.email, subject="Tasdiqlash kodingiz", html_body=html_body)


def issue_tokens_for_user(user):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }