from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["specialty"]
    search_fields = ["user__first_name", "user__last_name", "specialty__name"]


class DoctorDetailView(generics.RetrieveAPIView):
    queryset = Doctor.objects.filter(is_active=True).select_related("user", "specialty")
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]


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


class DoctorManageView(generics.RetrieveUpdateView):
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