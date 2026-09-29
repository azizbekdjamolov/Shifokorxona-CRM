from datetime import datetime

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from apps.bookings.models import Booking
from apps.doctors.models import Doctor, DoctorSchedule, Specialty
from apps.doctors.serializers import (
    DoctorSerializer,
    DoctorCreateSerializer,
    DoctorScheduleSerializer,
    SpecialtySerializer,
)
from apps.users.permissions import IsAdminUser, IsDoctorUser


class SpecialtyListView(generics.ListAPIView):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    permission_classes = [AllowAny]


class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.filter(is_active=True).select_related("user", "specialty")
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["specialty"]
    search_fields = ["user__first_name", "user__last_name", "specialty__name"]
    ordering_fields = ["average_rating", "price", "experience_years"]


class DoctorDetailView(generics.RetrieveAPIView):
    queryset = Doctor.objects.filter(is_active=True).select_related("user", "specialty")
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]


class DoctorAvailabilityView(APIView):
    """Shu kunga band bo'lgan vaqtlar ro'yxati.

    GET /api/doctors/{id}/availability/?date=YYYY-MM-DD
    hold/confirmed bronlar band hisoblanadi.
    """

    permission_classes = [AllowAny]

    def get(self, request, pk):
        date_str = request.query_params.get("date") or ""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return Response(
                {"date": ["date YYYY-MM-DD formatida kiritilsin"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.bookings.services.booking_lock import expire_stale_holds

        expire_stale_holds()
        booked = (
            Booking.objects.filter(
                doctor_id=pk,
                date=date,
                status__in=[Booking.Status.HOLD, Booking.Status.CONFIRMED],
            )
            .values_list("time", flat=True)
            .order_by("time")
        )
        return Response(
            {
                "date": date.isoformat(),
                "booked_times": [t.strftime("%H:%M") for t in booked],
            }
        )


class DoctorCreateView(generics.CreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorCreateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class DoctorUpdateView(generics.UpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorCreateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return DoctorSerializer
        return DoctorCreateSerializer


class DoctorManageView(generics.RetrieveUpdateAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsDoctorUser]

    def get_object(self):
        from django.shortcuts import get_object_or_404

        return get_object_or_404(Doctor.objects.select_related("user", "specialty"), user=self.request.user)


class DoctorScheduleView(generics.ListCreateAPIView):
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsAuthenticated, IsDoctorUser]

    def get_queryset(self):
        doctor = Doctor.objects.filter(user=self.request.user).first()
        if not doctor:
            return DoctorSchedule.objects.none()
        return DoctorSchedule.objects.filter(doctor=doctor)

    def perform_create(self, serializer):
        doctor, _ = Doctor.objects.get_or_create(
            user=self.request.user,
            defaults={
                "specialty": Specialty.objects.first(),
            },
        )
        serializer.save(doctor=doctor)


class DoctorScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsAuthenticated, IsDoctorUser]

    def get_queryset(self):
        doctor = Doctor.objects.filter(user=self.request.user).first()
        if not doctor:
            return DoctorSchedule.objects.none()
        return DoctorSchedule.objects.filter(doctor=doctor)


class AdminDoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.all().select_related("user", "specialty")
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        specialty = self.request.query_params.get("specialty")
        if specialty:
            queryset = queryset.filter(specialty_id=specialty)
        return queryset


class AdminDoctorToggleView(generics.RetrieveUpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        is_active = request.data.get("is_active")
        if is_active is not None:
            instance.is_active = bool(is_active)
            instance.save(update_fields=["is_active"])
        return Response(DoctorSerializer(instance).data)


class SpecialtyCreateView(generics.CreateAPIView):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class SpecialtyUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class SpecialtyDeleteView(generics.DestroyAPIView):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]