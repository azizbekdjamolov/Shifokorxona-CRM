from django.urls import path

from apps.payments.views import (
    ClickWebhookView,
    MockPayView,
    MyPaymentsView,
    PaymeWebhookView,
    PaymentCancelView,
    PaymentCreateView,
    PaymentDetailView,
    PaymentProvidersView,
)

urlpatterns = [
    path("", MyPaymentsView.as_view(), name="my_payments"),
    path("providers/", PaymentProvidersView.as_view(), name="payment_providers"),
    path("initiate/", PaymentCreateView.as_view(), name="payment_initiate"),
    path("webhook/payme/", PaymeWebhookView.as_view(), name="payme_webhook"),
    path("webhook/click/", ClickWebhookView.as_view(), name="click_webhook"),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment_detail"),
    path("<int:pk>/cancel/", PaymentCancelView.as_view(), name="payment_cancel"),
    path("<int:pk>/mock-pay/", MockPayView.as_view(), name="payment_mock_pay"),
]