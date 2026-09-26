import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.models import AIMessage, AIConversation
from apps.ai.serializers import AIChatSerializer, AIMessageSerializer
from apps.ai.services.ai_client import AIProviderError, generate_ai_response
from apps.ai.services.crm_context import context_to_json
from apps.ai.services.prompts import build_system_prompt

logger = logging.getLogger("apps")


def _get_or_create_conversation(user):
    conversation, _ = AIConversation.objects.get_or_create(
        user=user,
        defaults={"user": user},
    )
    return conversation


class AIMessagesView(APIView):
    """Foydalanuvchining AI suhbat tarixini qaytaradi."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversation = _get_or_create_conversation(request.user)
        messages = conversation.messages.all()
        serializer = AIMessageSerializer(messages, many=True, context={"request": request})
        return Response(serializer.data)


class AIChatView(APIView):
    """Xabar (va ixtiyoriy rasm) qabul qiladi, vision modelga jo'natadi,
    javobni saqlab qaytaradi. AI API kalit faqat backendda."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AIChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data.get("message", "").strip()
        image = serializer.validated_data.get("image")
        language = serializer.validated_data.get("language", "uz")

        user_message = AIMessage.objects.create(
            conversation=_get_or_create_conversation(request.user),
            role=AIMessage.Role.USER,
            text=text,
            image=image,
        )

        if not settings_ai_key_available():
            reply_text = localized_error(language)
            role_to_save = "assistant"
        else:
            try:
                conversation = user_message.conversation
                history = list(
                    conversation.messages.exclude(pk=user_message.pk).order_by(
                        "-created_at"
                    )[: settings.AI_MAX_HISTORY_TURNS * 2]
                )
                history = list(reversed(history))
                messages_payload = []
                for m in history:
                    messages_payload.append({"role": m.role, "text": m.text})
                messages_payload.append({"role": "user", "text": text})

                crm_context = context_to_json(request.user, lang=language)
                system_prompt = build_system_prompt(
                    request.user, lang=language, crm_context=crm_context
                )
                model_payload = [
                    {"role": m["role"], "text": m["text"]} for m in messages_payload
                ]
                reply_text = generate_ai_response(
                    system_prompt, model_payload, image_field=image
                )
                role_to_save = "assistant"
            except AIProviderError as err:
                logger.error("AI xatolik: %s", err)
                reply_text = localized_error(
                    language,
                    detail=(
                        "AI model hozircha mavjud emas. Iltimos, keyinroq "
                        "urinib ko'ring."
                        if language == "uz"
                        else (
                            "AI сейчас недоступен. Попробуйте позже."
                            if language == "ru"
                            else "AI is unavailable right now. Please try again later."
                        )
                    ),
                )
                role_to_save = "system_error"

        assistant_message = None
        if role_to_save == "assistant":
            assistant_message = AIMessage.objects.create(
                conversation=user_message.conversation,
                role=AIMessage.Role.ASSISTANT,
                text=reply_text,
            )

        return Response(
            {
                "reply": reply_text,
                "user_message": AIMessageSerializer(
                    user_message, context={"request": request}
                ).data,
                "assistant_message": (
                    AIMessageSerializer(
                        assistant_message, context={"request": request}
                    ).data
                    if assistant_message
                    else None
                ),
            },
            status=status.HTTP_200_OK,
        )


def settings_ai_key_available():
    return bool(settings.AI_API_KEY)


def localized_error(language, detail=None):
    if detail:
        return detail
    if language == "ru":
        return (
            "AI xizmati hozircha sozlanmagan. Ilova administratoriga "
            "murojaat qiling."
        )
    if language == "en":
        return (
            "The AI service is not configured yet. Please contact the "
            "application administrator."
        )
    return (
        "AI xizmati hozircha sozlanmagan. Ilova administratoriga murojaat qiling."
    )