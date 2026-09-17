from django.urls import path

from apps.prescriptions.views import (
    MyPrescriptionsView,
    CreatePrescriptionView,
    DoctorPrescriptionsView,
    PatientHistoryView,
)

urlpatterns = [
    path("my/", MyPrescriptionsView.as_view(), name="my_prescriptions"),
    path("create/", CreatePrescriptionView.as_view(), name="create_prescription"),
    path("doctor/", DoctorPrescriptionsView.as_view(), name="doctor_prescriptions"),
    path("doctor/history/", PatientHistoryView.as_view(), name="patient_history"),
]