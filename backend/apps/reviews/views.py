from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.reviews.models import Review
from apps.reviews.serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewModerateSerializer,
)
from apps.users.permissions import IsPatientUser, IsAdminUser


class DoctorReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        from django.shortcuts import get_object_or_404

        from apps.doctors.models import Doctor

        doctor = get_object_or_404(Doctor, pk=self.kwargs["doctor_id"])
        return Review.objects.filter(
            doctor=doctor, status=Review.Moderation.APPROVED
        ).select_related("patient", "doctor")


class CreateReviewView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsPatientUser]


class MyReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsPatientUser]

    def get_queryset(self):
        return Review.objects.filter(patient=self.request.user).select_related("doctor", "doctor__user")


class AdminReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Review.objects.select_related("patient", "doctor", "doctor__user")
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset


class AdminReviewModerateView(generics.RetrieveUpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewModerateSerializer
    permission_classes = [IsAdminUser]