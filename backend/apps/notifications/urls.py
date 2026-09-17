from django.urls import path

from apps.notifications.views import (
    TelegramLinkCodeView,
    TelegramLinkConfirmView,
    TelegramUnlinkView,
)

urlpatterns = [
    path("telegram/link-code/", TelegramLinkCodeView.as_view(), name="telegram_link_code"),
    path("telegram/confirm/", TelegramLinkConfirmView.as_view(), name="telegram_link_confirm"),
    path("telegram/unlink/", TelegramUnlinkView.as_view(), name="telegram_unlink"),
]