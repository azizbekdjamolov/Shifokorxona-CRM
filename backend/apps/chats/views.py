from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.chats.models import Conversation, Message
from apps.chats.serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageCreateSerializer,
    MessageSerializer,
)


class ConversationListView(generics.ListCreateAPIView):
    """Bemor suhbatlarini ko'radi; doctor o'zining suhbatlarini ko'radi."""

    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "doctor":
            return Conversation.objects.filter(doctor__user=user).select_related("doctor", "doctor__user", "doctor__specialty", "patient")
        return Conversation.objects.filter(patient=user).select_related("doctor", "doctor__user", "doctor__specialty", "patient")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ConversationCreateSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.role != "patient":
            return Response(
                {"detail": "Faqat bemor yangi suhbat boshlllashi mumkin"},
                status=status.HTTP_403_FORBIDDEN,
            )
        doctor = serializer.validated_data["doctor"]
        conversation, created = Conversation.objects.get_or_create(
            doctor=doctor,
            patient=request.user,
            defaults={"doctor": doctor, "patient": request.user},
        )
        out = ConversationSerializer(conversation, context={"request": request}).data
        return Response(out, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "doctor":
            return Conversation.objects.filter(doctor__user=user)
        return Conversation.objects.filter(patient=user)


class ConversationMessagesView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation = self._get_conversation()
        if conversation:
            conversation.messages.filter(is_read=False).exclude(sender=self.request.user).update(is_read=True)
        return Message.objects.filter(conversation=self.kwargs["pk"])

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MessageCreateSerializer
        return MessageSerializer

    def create(self, request, *args, **kwargs):
        conversation = self._get_conversation()
        if not conversation:
            return Response({"detail": "Suhbat topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        message_serializer = MessageCreateSerializer(
            data=request.data,
            context={"request": request, "conversation": conversation},
        )
        message_serializer.is_valid(raise_exception=True)
        message = message_serializer.save()
        conversation.save(update_fields=["updated_at"])
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

    def _get_conversation(self):
        user = self.request.user
        try:
            if user.role == "doctor":
                return Conversation.objects.get(pk=self.kwargs["pk"], doctor__user=user)
            return Conversation.objects.get(pk=self.kwargs["pk"], patient=user)
        except Conversation.DoesNotExist:
            return None


class UnreadMessagesView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "doctor":
            qs = Conversation.objects.filter(doctor__user=user)
        else:
            qs = Conversation.objects.filter(patient=user)
        ids = []
        for c in qs.select_related("doctor", "patient"):
            if c.messages.filter(is_read=False).exclude(sender=user).exists():
                ids.append(c.id)
        return Conversation.objects.filter(id__in=ids)