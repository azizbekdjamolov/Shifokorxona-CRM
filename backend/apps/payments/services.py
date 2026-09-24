import hashlib
import time

from django.conf import settings

from apps.payments.models import Payment


def create_payment(user, booking, provider):
    payment = Payment(
        user=user,
        booking=booking,
        amount=booking.doctor.price,
        provider=provider,
    )
    payment.save()
    return payment


def get_or_create_pending_payment(user, booking, provider):
    existing = Payment.objects.filter(
        user=user, booking=booking, provider=provider, status=Payment.Status.PENDING
    ).first()
    if existing:
        return existing, False
    return create_payment(user, booking, provider), True


def mark_paid(payment, transaction_id="", commit=True):
    payment.status = Payment.Status.PAID
    if transaction_id:
        payment.transaction_id = transaction_id
    if commit:
        payment.save(update_fields=["status", "transaction_id", "updated_at"])
    return payment


def cancel_payment(payment, commit=True):
    if payment.status in (Payment.Status.PAID,):
        return payment
    payment.status = Payment.Status.CANCELLED
    if commit:
        payment.save(update_fields=["status", "updated_at"])
    return payment


def mark_failed(payment, commit=True):
    payment.status = Payment.Status.FAILED
    if commit:
        payment.save(update_fields=["status", "updated_at"])
    return payment


def payment_to_tiyin(payment):
    return int(payment.amount * 100)


# ------------------------- Payme -------------------------
PAYME_ORDER_NOT_FOUND = -31050
PAYME_INCORRECT_AMOUNT = -31001
PAYME_TRANSACTION_NOT_FOUND = -31003
PAYME_METHOD_NOT_ALLOWED = -31008
PAYME_REQ_UNAUTHORIZED = -32504


def payme_error(request_id, code, message):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def payme_authorized(request):
    import base64

    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header.replace("Bearer ", "").strip()
    expected = base64.b64encode(
        settings.PAYME_MERCHANT_KEY.encode()
    ).decode()
    return token == expected


def payme_check_authorization(request_id, request):
    if not settings.PAYME_MERCHANT_KEY:
        return payme_error(request_id, PAYME_REQ_UNAUTHORIZED, "Provider is not configured")
    if not payme_authorized(request):
        return payme_error(request_id, PAYME_REQ_UNAUTHORIZED, "Forbidden auth header")
    return None


def payme_get_payment(order_id):
    return Payment.objects.filter(pk=order_id).first()


def handle_payme_method(request_id, method, params):
    if method == "CheckPerformTransaction":
        payment = payme_get_payment(params.get("account", {}).get("order_id"))
        if not payment:
            return payme_error(request_id, PAYME_ORDER_NOT_FOUND, "Order not found")
        if payment.status in (Payment.Status.PAID,):
            return payme_error(request_id, PAYME_TRANSACTION_NOT_FOUND, "Order already paid")
        if int(params.get("amount") or 0) != payment_to_tiyin(payment):
            return payme_error(request_id, PAYME_INCORRECT_AMOUNT, "Incorrect amount")
        return {"jsonrpc": "2.0", "id": request_id, "result": {"allow": True}}

    if method == "CreateTransaction":
        payment = payme_get_payment(params.get("account", {}).get("order_id"))
        if not payment:
            return payme_error(request_id, PAYME_ORDER_NOT_FOUND, "Order not found")
        if payment.status == Payment.Status.PAID:
            return payme_error(request_id, PAYME_TRANSACTION_NOT_FOUND, "Order already paid")
        payme_id = str(params.get("id"))
        payment.transaction_id = payme_id
        payment.save(update_fields=["transaction_id", "updated_at"])
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "create_time": payme_now_ms(),
                "transaction": payme_id,
                "state": 1,
            },
        }

    if method == "PerformTransaction":
        payme_id = str(params.get("id"))
        payment = Payment.objects.filter(transaction_id=payme_id).first()
        if not payment:
            return payme_error(request_id, PAYME_TRANSACTION_NOT_FOUND, "Transaction not found")
        mark_paid(payment, transaction_id=payme_id)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "perform_time": payme_now_ms(),
                "transaction": payme_id,
                "state": 2,
            },
        }

    if method == "CheckTransaction":
        payme_id = str(params.get("id"))
        payment = Payment.objects.filter(transaction_id=payme_id).first()
        if not payment:
            return payme_error(request_id, PAYME_TRANSACTION_NOT_FOUND, "Transaction not found")
        state = 2 if payment.status == Payment.Status.PAID else (
            -1 if payment.status == Payment.Status.CANCELLED else 1
        )
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "create_time": payme_now_ms(),
                "perform_time": 0,
                "cancel_time": 0,
                "transaction": payme_id,
                "state": state,
                "reason": params.get("reason") or 0,
            },
        }

    if method == "CancelTransaction":
        payme_id = str(params.get("id"))
        payment = Payment.objects.filter(transaction_id=payme_id).first()
        if not payment:
            return payme_error(request_id, PAYME_TRANSACTION_NOT_FOUND, "Transaction not found")
        if payment.status == Payment.Status.PAID:
            return payme_error(request_id, PAYME_TRANSACTION_NOT_FOUND, "Already paid, cannot cancel")
        cancel_payment(payment)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "cancel_time": payme_now_ms(),
                "transaction": payme_id,
                "state": -1,
                "reason": params.get("reason") or 1,
            },
        }

    return payme_error(request_id, -32400, "Method not found")


def payme_now_ms():
    return int(time.time() * 1000)


def payme_clickable():
    return bool(settings.PAYME_MERCHANT_KEY)


# ------------------------- Click -------------------------
CLICK_SIGN_ERROR = -1
CLICK_AMOUNT_ERROR = -2
CLICK_ACCOUNT_ERROR = -5
CLICK_TRANSACTION_NOT_FOUND = -6
CLICK_REQUEST_ERROR = -8


def click_md5(*values):
    raw = "".join(values)
    return hashlib.md5(raw.encode()).hexdigest()


def click_sign_string_params():
    service_id = settings.CLICK_SERVICE_ID
    secret_key = settings.CLICK_SECRET_KEY
    return str(service_id), secret_key


def click_get_payment(merchant_trans_id):
    return Payment.objects.filter(pk=merchant_trans_id).first()


def click_prepare_sign_valid(params):
    click_trans_id = str(params.get("click_trans_id", ""))
    _, secret_key = click_sign_string_params()
    service_id = str(params.get("service_id", ""))
    merchant_trans_id = str(params.get("merchant_trans_id", ""))
    return params.get("sign_string") == click_md5(
        click_trans_id, service_id, secret_key, merchant_trans_id
    )


def click_complete_sign_valid(params):
    click_trans_id = str(params.get("click_trans_id", ""))
    _, secret_key = click_sign_string_params()
    service_id = str(params.get("service_id", ""))
    merchant_trans_id = str(params.get("merchant_trans_id", ""))
    amount = str(params.get("amount", ""))
    action = str(params.get("action", ""))
    sign_time = str(params.get("sign_time", ""))
    return params.get("sign_string") == click_md5(
        click_trans_id, service_id, secret_key, merchant_trans_id, amount, action, sign_time
    )


def click_clicked():
    return bool(settings.CLICK_SERVICE_ID and settings.CLICK_SECRET_KEY)


def click_response(payment, error, error_note, action=0, merchant_prepare_id=None):
    return {
        "click_trans_id": -1,
        "merchant_trans_id": payment.id if payment else "",
        "merchant_prepare_id": merchant_prepare_id,
        "merchant_confirm_id": merchant_prepare_id,
        "error": error,
        "error_note": error_note,
    }