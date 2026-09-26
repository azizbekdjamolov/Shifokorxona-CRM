from django.urls import path

from apps.ai.views import AIChatView, AIMessagesView

urlpatterns = [
    path("messages/", AIMessagesView.as_view(), name="ai_messages"),
    path("chat/", AIChatView.as_view(), name="ai_chat"),
]