from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthCheckView.as_view(), name="health"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/users/", include("apps.users.urls")),
    path("api/doctors/", include("apps.doctors.urls")),
    path("api/bookings/", include("apps.bookings.urls")),
    path("api/prescriptions/", include("apps.prescriptions.urls")),
    path("api/reviews/", include("apps.reviews.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/chats/", include("apps.chats.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Production'da ham media fayllar (doctor fotto, retsept rasmlari) servis qilinadi.
if not settings.DEBUG:
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]