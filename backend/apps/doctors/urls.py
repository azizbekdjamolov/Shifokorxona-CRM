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
)

urlpatterns = [
    path("specialties/", SpecialtyListView.as_view(), name="specialties"),
    path("", DoctorListView.as_view(), name="doctors"),
    path("create/", DoctorCreateView.as_view(), name="doctor_create"),
    path("me/", DoctorManageView.as_view(), name="doctor_me"),
    path("me/schedule/", DoctorScheduleView.as_view(), name="doctor_schedule"),
    path("me/schedule/<int:pk>/", DoctorScheduleDetailView.as_view(), name="doctor_schedule_detail"),
    path("<int:pk>/", DoctorDetailView.as_view(), name="doctor_detail"),
    path("<int:pk>/update/", DoctorUpdateView.as_view(), name="doctor_update"),
]