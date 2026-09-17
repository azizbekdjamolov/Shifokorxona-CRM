from django.urls import path

from apps.users.views import RegisterView, VerifyOtpView, MeView, ResendOtpView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", VerifyOtpView.as_view(), name="verify_otp"),
    path("resend-otp/", ResendOtpView.as_view(), name="resend_otp"),
    path("me/", MeView.as_view(), name="me"),
]