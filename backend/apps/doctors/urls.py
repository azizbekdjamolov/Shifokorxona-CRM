from django.urls import path

from apps.doctors.views import (
    SpecialtyListView,
    DoctorListView,
    DoctorDetailView,
    DoctorCreateView,
    DoctorUpdateView,
    DoctorManageView,
    DoctorScheduleView,
    DoctorScheduleDetailView,
    AdminDoctorListView,
    AdminDoctorToggleView,
    SpecialtyCreateView,
    SpecialtyUpdateView,
    SpecialtyDeleteView,
)

urlpatterns = [
    path("specialties/", SpecialtyListView.as_view(), name="specialties"),
    path("specialties/create/", SpecialtyCreateView.as_view(), name="specialty_create"),
    path("specialties/<int:pk>/", SpecialtyUpdateView.as_view(), name="specialty_update"),
    path("specialties/<int:pk>/delete/", SpecialtyDeleteView.as_view(), name="specialty_delete"),
    path("", DoctorListView.as_view(), name="doctors"),
    path("create/", DoctorCreateView.as_view(), name="doctor_create"),
    path("me/", DoctorManageView.as_view(), name="doctor_me"),
    path("me/schedule/", DoctorScheduleView.as_view(), name="doctor_schedule"),
    path("me/schedule/<int:pk>/", DoctorScheduleDetailView.as_view(), name="doctor_schedule_detail"),
    path("admin/", AdminDoctorListView.as_view(), name="admin_doctors"),
    path("admin/<int:pk>/toggle/", AdminDoctorToggleView.as_view(), name="admin_doctor_toggle"),
    path("<int:pk>/", DoctorDetailView.as_view(), name="doctor_detail"),
    path("<int:pk>/update/", DoctorUpdateView.as_view(), name="doctor_update"),
]