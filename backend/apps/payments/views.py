import json

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404 as drf_get_object_or_404

from apps.payments.models import Payment
from apps.payments.serializers import PaymentCreateSerializer, PaymentSerializer
from apps.payments.services import (
    CLICK_AMOUNT_ERROR,
    CLICK_REQUEST_ERROR,
    CLICK_SIGN_ERROR,
    CLICK_TRANSACTION_NOT_FOUND,
    cancel_payment,
    click_clicked,
    click_complete_sign_valid,
    click_get_payment,
    click_prepare_sign_valid,
    click_response,
    get_or_create_pending_payment,
    handle_payme_method,
    mark_paid,
    payme_check_authorization,
)


class PaymentProvidersView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        providers = []
        if getattr(settings, "PAYMENT_MOCK", True):
            providers.append({"key": "mock", "label": "Mock (test)"})
        if settings.PAYME_MERCHANT_KEY:
            providers.append({"key": "payme", "label": "Payme"})
        if settings.CLICK_SERVICE_ID and settings.CLICK_SECRET_KEY:
            providers.append({"key": "click", "label": "Click"})
        return Response({"providers": providers})


class MyPaymentsView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related("booking", "booking__doctor")


class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.validated_data["booking"]
        if booking.user != request.user:
            return Response(
                {"detail": "Bu bron sizga tegishli emas"}, status=status.HTTP_403_FORBIDDEN
            )
        provider = serializer.validated_data["provider"]
        payment, created = get_or_create_pending_payment(request.user, booking, provider)
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = drf_get_object_or_404(Payment, pk=self.kwargs["pk"])
        if obj.user != self.request.user and self.request.user.role != "admin":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Bu to'lov sizga tegishli emas")
        return obj


class PaymentCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        payment = drf_get_object_or_404(Payment, pk=pk, user=request.user)
        if payment.status != Payment.Status.PENDING:
            return Response(
                {"detail": "Faqat kutilayotgan to'lovni bekor qilish mumkin"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cancel_payment(payment)
        return Response(PaymentSerializer(payment).data)


class MockPayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not getattr(settings, "PAYMENT_MOCK", True):
            return Response(
                {"detail": "Mock rejim o'chirilgan"}, status=status.HTTP_400_BAD_REQUEST
            )
        payment = drf_get_object_or_404(Payment, pk=pk, user=request.user)
        if payment.status != Payment.Status.PENDING:
            return Response(
                {"detail": "Faqat kutilayotgan to'lovni to'lash mumkin"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        mark_paid(payment, transaction_id=f"mock-{payment.id}")
        return Response(PaymentSerializer(payment).data)


@method_decorator(csrf_exempt, name="dispatch")
class PaymeWebhookView(APIView):
    """Payme merchant webhook'i — DRF JWT emas, Payme maxsus Bearer imzosini
    ishlatadi, shuning uchun DRF authentication o'chiriladi va imzo qo'lda
    payme_check_authorization orqali tekshiriladi."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            body = request.data
            if body is None:
                body = json.loads(request.body.decode("utf-8") or "{}")
        except (ValueError, AttributeError):
            return Response({"error": {"code": -32600, "message": "Invalid JSON"}})

        request_id = body.get("id")
        method = body.get("method")
        params = body.get("params", {})

        auth_error = payme_check_authorization(request_id, request)
        if auth_error:
            return Response(auth_error)
        result = handle_payme_method(request_id, method, params)
        return Response(result)


@method_decorator(csrf_exempt, name="dispatch")
class ClickWebhookView(APIView):
    """Click prepare/complete webhook'i — DRF auth o'chirilgan, imzo
    Click tomonidan yuborilgan sign_string orqali tekshiriladi."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            params = json.loads(request.body.decode("utf-8") or "{}")
        except (ValueError, AttributeError):
            params = {}

        click_trans_id = params.get("click_trans_id")
        service_id = params.get("service_id")
        merchant_trans_id = params.get("merchant_trans_id")
        amount = params.get("amount")
        action = params.get("action")
        error = params.get("error")

        if not click_clicked():
            return Response(
                click_response(None, CLICK_REQUEST_ERROR, "Click not configured")
            )

        if str(service_id) != str(settings.CLICK_SERVICE_ID):
            return Response(
                click_response(None, CLICK_REQUEST_ERROR, "Invalid service id")
            )

        payment = click_get_payment(merchant_trans_id)
        if not payment:
            return Response(
                click_response(None, CLICK_TRANSACTION_NOT_FOUND, "Transaction not found")
            )

        if str(action) == "0":
            if not click_prepare_sign_valid(params):
                return Response(click_response(payment, CLICK_SIGN_ERROR, "Sign check failed"))
            if payment.status in (Payment.Status.PAID,):
                return Response(
                    click_response(payment, CLICK_AMOUNT_ERROR, "Already paid")
                )
            return Response(
                click_response(
                    payment,
                    -2 if not params.get("error") else -1,
                    "To'lov to'lashga tayyor",
                    action=0,
                    merchant_prepare_id=payment.id,
                )
            )

        if str(action) in ("1", "2"):
            if not click_complete_sign_valid(params):
                return Response(click_response(payment, CLICK_SIGN_ERROR, "Sign check failed"))
            if int(amount) != payment_to_tiyin(payment):
                return Response(click_response(payment, CLICK_AMOUNT_ERROR, "Incorrect amount"))
            if str(action) == "1":
                mark_paid(payment, transaction_id=str(click_trans_id))
            else:
                cancel_payment(payment)
            return Response(
                click_response(
                    payment, 0, "Success", action=int(action), merchant_prepare_id=payment.id
                )
            )

        return Response(click_response(payment, CLICK_REQUEST_ERROR, "Invalid action"))


def payment_to_tiyin(payment):
    return int(payment.amount * 100)