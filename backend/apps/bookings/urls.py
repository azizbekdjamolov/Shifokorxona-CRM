from django.urls import path

from apps.bookings.views import (
    MyBookingsView,
    DoctorBookingsView,
    DoctorTodayQueueView,
    BookingUpdateView,
    PatientBookingCancelView,
    AdminBookingsView,
)

urlpatterns = [
    path("my/", MyBookingsView.as_view(), name="my_bookings"),
    path("my/<int:pk>/cancel/", PatientBookingCancelView.as_view(), name="booking_cancel"),
    path("doctor/", DoctorBookingsView.as_view(), name="doctor_bookings"),
    path("doctor/today/", DoctorTodayQueueView.as_view(), name="doctor_today_queue"),
    path("admin/", AdminBookingsView.as_view(), name="admin_bookings"),
    path("<int:pk>/", BookingUpdateView.as_view(), name="booking_update"),
]