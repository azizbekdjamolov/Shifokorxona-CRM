from django.urls import path

from apps.chats.views import (
    ConversationListView,
    ConversationDetailView,
    ConversationMessagesView,
    UnreadMessagesView,
)

urlpatterns = [
    path("conversations/", ConversationListView.as_view(), name="conversations"),
    path("conversations/unread/", UnreadMessagesView.as_view(), name="unread_conversations"),
    path("conversations/<int:pk>/", ConversationDetailView.as_view(), name="conversation_detail"),
    path("conversations/<int:pk>/messages/", ConversationMessagesView.as_view(), name="conversation_messages"),
]