from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification
from apps.notifications.bot import (
    store_link_code,
    get_link_owner,
    clear_link_code,
    send_telegram_message,
)


class TelegramLinkCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = store_link_code(request.user.email)
        return Response({"code": code})


class TelegramLinkConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = (request.data.get("code") or "").strip().upper()
        if not code:
            return Response({"code": "Kod talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)

        owner = get_link_owner(code)
        if not owner or ":" not in owner or not owner.startswith(request.user.email):
            return Response(
                {"detail": "Kod noto'g'ri yoki botga hali yuborilmagan"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chat_id = int(owner.split(":", 1)[1])
        request.user.telegram_chat_id = chat_id
        request.user.save(update_fields=["telegram_chat_id"])
        clear_link_code(code)

        message = "Telegram akkountingiz Shifokorxona CRM tizimiga muvaffaqiyatli ulandi."
        send_telegram_message(chat_id, message)
        Notification.objects.create(
            user=request.user,
            type=Notification.Type.TELEGRAM_LINK,
            message=message,
            chat_id=chat_id,
            is_sent=True,
            sent_at=timezone.now(),
        )

        return Response(
            {"detail": "Telegram akkounti ulandi", "telegram_chat_id": chat_id},
            status=status.HTTP_200_OK,
        )


class TelegramUnlinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat_id = request.user.telegram_chat_id
        request.user.telegram_chat_id = None
        request.user.save(update_fields=["telegram_chat_id"])
        if chat_id:
            send_telegram_message(chat_id, "Telegram akkountingiz tizimdan uzildi.")
        return Response({"detail": "Telegram akkounti uzildi"}, status=status.HTTP_200_OK)