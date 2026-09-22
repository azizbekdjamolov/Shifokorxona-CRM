import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger("apps")


def api_exception_handler(exc, context):
    """DRF xatolarini bir xil formatga keltiradi va log qiladi."""
    response = exception_handler(exc, context)

    if response is None:
        logger.exception(
            "Unhandled API exception: %s | %s | %s",
            exc.__class__.__name__,
            context.get("request"),
            exc,
        )
        return Response(
            {
                "detail": "Kutilmagan xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.",
                "error_type": exc.__class__.__name__,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    data = response.data
    if isinstance(data, dict):
        keys = list(data.keys())
        if len(keys) == 1 and keys[0] == "detail":
            payload = data
        else:
            payload = {"errors": data}
    else:
        payload = {"detail": data}

    # Brute-force amaliyotlarini (OTP, login) ogohlantirish sifatida log qilish
    if response.status_code in (429, 401, 403):
        request = context.get("request")
        user = getattr(request, "user", None)
        path = getattr(request, "path", "?")
        logger.warning(
            "API %s %s | user=%s | code=%s",
            path,
            response.status_code,
            getattr(user, "email", "anon"),
            exc.__class__.__name__,
        )

    return Response(payload, status=response.status_code)