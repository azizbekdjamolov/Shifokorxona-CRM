from django.urls import path

from apps.users.views import (
    RegisterView,
    VerifyOtpView,
    MeView,
    ResendOtpView,
    AdminUserListView,
    AdminUserUpdateView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", VerifyOtpView.as_view(), name="verify_otp"),
    path("resend-otp/", ResendOtpView.as_view(), name="resend_otp"),
    path("me/", MeView.as_view(), name="me"),
    path("admin/", AdminUserListView.as_view(), name="admin_users"),
    path("admin/<int:pk>/", AdminUserUpdateView.as_view(), name="admin_user_update"),
]