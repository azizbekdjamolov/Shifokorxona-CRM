from rest_framework import generics

from apps.prescriptions.models import Prescription
from apps.prescriptions.serializers import (
    PrescriptionSerializer,
    PrescriptionCreateSerializer,
)
from apps.users.permissions import IsDoctorUser, IsPatientUser


class MyPrescriptionsView(generics.ListAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsPatientUser]

    def get_queryset(self):
        return (
            Prescription.objects.filter(patient=self.request.user)
            .select_related("doctor", "doctor__user")
        )


class CreatePrescriptionView(generics.CreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionCreateSerializer
    permission_classes = [IsDoctorUser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PrescriptionCreateSerializer
        return PrescriptionSerializer


class DoctorPrescriptionsView(generics.ListAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsDoctorUser]

    def get_queryset(self):
        queryset = (
            Prescription.objects.filter(doctor__user=self.request.user)
            .select_related("doctor", "doctor__user", "patient")
        )
        patient_id = self.request.query_params.get("patient")
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


class PatientHistoryView(generics.ListAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsDoctorUser]

    def get_queryset(self):
        queryset = (
            Prescription.objects.filter(doctor__user=self.request.user)
            .select_related("doctor", "doctor__user", "patient")
            .order_by("-created_at")
        )
        patient_id = self.request.query_params.get("patient")
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset