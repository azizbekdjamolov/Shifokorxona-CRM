from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response

from apps.bookings.models import Booking
from apps.bookings.serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    BookingStatusSerializer,
)
from apps.users.permissions import IsPatientUser, IsDoctorUser, IsAdminUser


class MyBookingsView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsPatientUser]

    def get_queryset(self):
        return (
            Booking.objects.filter(user=self.request.user)
            .select_related("doctor", "doctor__user", "doctor__specialty")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BookingCreateSerializer
        return BookingSerializer


class DoctorBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsDoctorUser]

    def get_queryset(self):
        return (
            Booking.objects.filter(doctor__user=self.request.user)
            .select_related("user", "doctor", "doctor__user", "doctor__specialty")
        )


class DoctorTodayQueueView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsDoctorUser]

    def get_queryset(self):
        today = timezone.now().date()
        return (
            Booking.objects.filter(doctor__user=self.request.user, date=today)
            .exclude(status=Booking.Status.CANCELLED)
            .select_related("user", "doctor", "doctor__user", "doctor__specialty")
            .order_by("time")
        )


class BookingUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = BookingStatusSerializer
    queryset = Booking.objects.all()
    permission_classes = [IsDoctorUser]


class PatientBookingCancelView(generics.UpdateAPIView):
    serializer_class = BookingStatusSerializer
    permission_classes = [IsPatientUser]

    def get_object(self):
        from django.shortcuts import get_object_or_404

        return get_object_or_404(
            Booking,
            user=self.request.user,
            pk=self.kwargs["pk"],
            status__in=[Booking.Status.HOLD, Booking.Status.CONFIRMED],
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status not in [Booking.Status.HOLD, Booking.Status.CONFIRMED]:
            return Response(
                {"detail": "Bu bronni bekor qilib bo'lmaydi"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.status = Booking.Status.CANCELLED
        instance.save()
        return Response({"detail": "Bron bekor qilindi"}, status=status.HTTP_200_OK)


class AdminBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Booking.objects.select_related("user", "doctor", "doctor__user")
        qs = self.request.query_params.get("status")
        if qs:
            statuses = qs.split(",")
            queryset = queryset.filter(status__in=statuses)
        return queryset