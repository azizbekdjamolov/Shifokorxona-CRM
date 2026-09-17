from django.urls import path

from apps.reviews.views import (
    DoctorReviewsView,
    CreateReviewView,
    MyReviewsView,
    AdminReviewsView,
    AdminReviewModerateView,
)

urlpatterns = [
    path("doctor/<int:doctor_id>/", DoctorReviewsView.as_view(), name="doctor_reviews"),
    path("create/", CreateReviewView.as_view(), name="create_review"),
    path("my/", MyReviewsView.as_view(), name="my_reviews"),
    path("admin/", AdminReviewsView.as_view(), name="admin_reviews"),
    path("admin/<int:pk>/", AdminReviewModerateView.as_view(), name="admin_review_moderate"),
]