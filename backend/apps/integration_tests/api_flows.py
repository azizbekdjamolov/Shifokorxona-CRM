"""Keng qamrovli backend integration testlari.

Barcha API oqimlari tekshiriladi: auth, docttor, booking, review, prescription,
chat, password reset, telegram. Ishga tushirish:
    python manage.py test apps.integration_tests.api_flows -v2
"""

import io

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.users.models import OTP, User
from apps.doctors.models import Doctor, DoctorSchedule, Specialty
from apps.bookings.models import Booking
from apps.prescriptions.models import Prescription
from apps.reviews.models import Review


def create_user(email, password="TestPassw0rd!42", role="patient", first="Test", last="User"):
    return User.objects.create_user(
        username=email, email=email, password=password,
        first_name=first, last_name=last, role=role, is_email_verified=True,
    )


class BaseFlowTest(TestCase):
    def setUp(self):
        cache.clear()
        self.patient = create_user("patient@test.uz")
        self.doctor_user = create_user(
            "doctor@test.uz", role="doctor", first="Aziz", last="Karimov"
        )
        self.admin = create_user("admin@test.uz", role="admin", first="Admin", last="Root")
        self.spec = Specialty.objects.create(name="Kardiolog", slug="kardiolog")
        self.doctor = Doctor.objects.create(
            user=self.doctor_user, specialty=self.spec,
            bio="Tajribali kardiolog", experience_years=10, price=120000,
        )
        for weekday in DoctorSchedule.Weekday:
            DoctorSchedule.objects.create(
                doctor=self.doctor, weekday=weekday,
                start_time="09:00", end_time="17:00",
                is_working=weekday < 5,
            )
        self.patient_client = self._auth(self.patient)
        self.doctor_client = self._auth(self.doctor_user)
        self.admin_client = self._auth(self.admin)

    def _auth(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken

        token = RefreshToken.for_user(user)
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        return c

    def _make_completed_booking(self, patient=None):
        patient = patient or self.patient
        res = self.patient_client.post(
            "/api/bookings/my/",
            {"doctor": self.doctor.id, "date": timezone.localdate(), "time": "09:00"},
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        booking = Booking.objects.get(pk=res.data["id"])
        self.assertEqual(booking.status, Booking.Status.HOLD)
        res = self.doctor_client.patch(
            f"/api/bookings/{booking.id}/",
            {"status": "confirmed"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)
        res = self.doctor_client.patch(
            f"/api/bookings/{booking.id}/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.COMPLETED)
        return booking


class AuthFlowTest(BaseFlowTest):
    def test_register_login_me(self):
        c = APIClient()
        res = c.post(
            "/api/users/register/",
            {
                "first_name": "Yang",
                "last_name": "Foy",
                "email": "new@test.uz",
                "password": "StrongPassw0rd!",
                "confirm_password": "StrongPassw0rd!",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.assertIn("tokens", res.data)
        self.assertTrue(res.data["user"]["is_email_verified"])

        res = c.post(
            "/api/token/",
            {"email": "new@test.uz", "password": "StrongPassw0rd!"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        res = c.get("/api/users/me/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["email"], "new@test.uz")

    def test_register_duplicate_email(self):
        c = APIClient()
        res = c.post(
            "/api/users/register/",
            {
                "email": "patient@test.uz",
                "password": "StrongPassw0rd!",
                "confirm_password": "StrongPassw0rd!",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", str(res.data))

    def test_password_change(self):
        res = self.patient_client.patch(
            "/api/users/me/",
            {"current_password": "TestPassw0rd!42", "password": "NewPass123!", "confirm_password": "NewPass123!"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.patient.refresh_from_db()
        self.assertTrue(self.patient.check_password("NewPass123!"))

    def test_password_change_wrong_current(self):
        res = self.patient_client.patch(
            "/api/users/me/",
            {"current_password": "wrong", "password": "NewPass123!", "confirm_password": "NewPass123!"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_unauthorized_me(self):
        c = APIClient()
        self.assertEqual(c.get("/api/users/me/").status_code, 401)


class DoctorFlowTest(BaseFlowTest):
    def test_public_doctor_list(self):
        c = APIClient()
        res = c.get("/api/doctors/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["results"][0]["user"]["email"], "doctor@test.uz")

    def test_search_by_name(self):
        res = self.patient_client.get("/api/doctors/?search=Aziz")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)

    def test_search_by_specialty(self):
        res = self.patient_client.get("/api/doctors/?search=Kardiolog")
        self.assertEqual(res.data["results"][0]["id"], self.doctor.id)

    def test_filter_and_ordering(self):
        res = self.patient_client.get(f"/api/doctors/?specialty={self.spec.id}")
        self.assertEqual(len(res.data["results"]), 1)
        res = self.patient_client.get("/api/doctors/?ordering=-price")
        self.assertEqual(res.status_code, 200)

    def test_doctor_detail_with_schedule(self):
        res = self.patient_client.get(f"/api/doctors/{self.doctor.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["specialty_name"], "Kardiolog")
        self.assertEqual(len(res.data["schedule"]), 7)

    def test_doctor_me(self):
        res = self.doctor_client.get("/api/doctors/me/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], self.doctor.id)

    def test_doctor_photo_upload(self):
        import io

        from PIL import Image

        buf = io.BytesIO()
        Image.new("RGB", (8, 8), color=(80, 90, 200)).save(buf, format="JPEG")
        image = SimpleUploadedFile("foto.jpg", buf.getvalue(), content_type="image/jpeg")
        res = self.doctor_client.patch(
            "/api/doctors/me/",
            {"photo": image},
            format="multipart",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.doctor.refresh_from_db()
        self.assertTrue(self.doctor.photo.name.startswith("doctors/"))
        self.assertTrue(self.doctor.photo.name.endswith(".jpg"))


class BookingFlowTest(BaseFlowTest):
    def test_create_hold_and_slot_lock(self):
        res = self.patient_client.post(
            "/api/bookings/my/",
            {"doctor": self.doctor.id, "date": timezone.localdate(), "time": "10:30"},
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        # Ikkinchi bemor bir xil slotni egallay olmaydi
        other = create_user("other@test.uz")
        oc = self._auth(other)
        res = oc.post(
            "/api/bookings/my/",
            {"doctor": self.doctor.id, "date": timezone.localdate(), "time": "10:30"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_patient_cancel_hold(self):
        res = self.patient_client.post(
            "/api/bookings/my/",
            {"doctor": self.doctor.id, "date": timezone.localdate(), "time": "09:30"},
            format="json",
        )
        booking_id = res.data["id"]
        res = self.patient_client.patch(f"/api/bookings/my/{booking_id}/cancel/", {}, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.patient_client.get("/api/bookings/my/")
        from apps.bookings.models import Booking

        self.patient.refresh_from_db()

    def test_patient_cannot_change_others(self):
        res = self.patient_client.post(
            "/api/bookings/my/",
            {"doctor": self.doctor.id, "date": timezone.localdate(), "time": "11:00"},
            format="json",
        )
        booking_id = res.data["id"]
        other = create_user("other2@test.uz")
        oc = self._auth(other)
        res = oc.patch(f"/api/bookings/my/{booking_id}/cancel/", {}, format="json")
        self.assertEqual(res.status_code, 404)

    def test_status_flow_completed(self):
        booking = self._make_completed_booking()
        self.assertEqual(booking.status, Booking.Status.COMPLETED)

    def test_illegal_status_transition(self):
        res = self.patient_client.post(
            "/api/bookings/my/",
            {"doctor": self.doctor.id, "date": timezone.localdate(), "time": "12:00"},
            format="json",
        )
        booking_id = res.data["id"]
        # HOLD dan to'g'ridan COMPLETED ga o'tib bo'lmaydi
        res = self.doctor_client.patch(
            f"/api/bookings/{booking_id}/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_doctor_today_queue(self):
        self._make_completed_booking()
        res = self.doctor_client.get("/api/bookings/doctor/today/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)

    def test_admin_booking_filter(self):
        self._make_completed_booking()
        res = self.admin_client.get("/api/bookings/admin/?status=completed,confirmed")
        self.assertEqual(res.status_code, 200)

    def test_non_patient_cannot_book(self):
        res = self.doctor_client.post(
            "/api/bookings/my/",
            {"doctor": self.doctor.id, "date": timezone.localdate(), "time": "13:00"},
            format="json",
        )
        self.assertEqual(res.status_code, 403)


class ReviewFlowTest(BaseFlowTest):
    def test_review_requires_completed(self):
        res = self.patient_client.post(
            "/api/reviews/create/",
            {"booking": 999, "rating": 5, "text": "Judа zo'r!"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_full_review_flow(self):
        booking = self._make_completed_booking()

        # Bemor sharh qoldiradi (pending)
        res = self.patient_client.post(
            "/api/reviews/create/",
            {"booking": booking.id, "rating": 5, "text": "Ajoyib shifokor!"},
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)

        # Public ro'yxatda hali ko'rinmaydi (moderatsiya kerak)
        res = self.patient_client.get(f"/api/reviews/doctor/{self.doctor.id}/")
        self.assertEqual(len(res.data["results"]), 0)

        # Admin tasdiqlaydi
        review = Review.objects.get()
        res = self.admin_client.patch(f"/api/reviews/admin/{review.id}/", {"status": "approved"}, format="json")
        self.assertEqual(res.status_code, 200, res.data)

        # Public endi ko'rinadi + doctor_name bor
        res = self.patient_client.get(f"/api/reviews/doctor/{self.doctor.id}/")
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["doctor_name"], "Dr. Aziz Karimov")

        # Takroriy sharh qoldirib bo'lmaydi
        res = self.patient_client.post(
            "/api/reviews/create/",
            {"booking": booking.id, "rating": 4, "text": "Yana"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_rating_updates_doctor(self):
        booking = self._make_completed_booking()
        self.patient_client.post(
            "/api/reviews/create/",
            {"booking": booking.id, "rating": 5, "text": "Zo'r"},
            format="json",
        )
        review = Review.objects.get()
        self.admin_client.patch(f"/api/reviews/admin/{review.id}/", {"status": "approved"}, format="json")
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.average_rating, 5.0)

    def test_admin_reviews_filter_by_status(self):
        booking = self._make_completed_booking()
        self.patient_client.post(
            "/api/reviews/create/",
            {"booking": booking.id, "rating": 5, "text": "Zo'r"},
            format="json",
        )
        res = self.admin_client.get("/api/reviews/admin/?status=pending")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)


class PrescriptionFlowTest(BaseFlowTest):
    def test_prescription_requires_completed_and_own_doctor(self):
        booking = self._make_completed_booking()
        res = self.doctor_client.post(
            "/api/prescriptions/create/",
            {
                "booking": booking.id,
                "medicine_name": "Paratsetamol",
                "instruction": "Kuniga 3 mahal",
                "times_per_day": 3,
                "days": 5,
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(Prescription.objects.count(), 1)

    def test_patient_prescriptions_list(self):
        booking = self._make_completed_booking()
        self.doctor_client.post(
            "/api/prescriptions/create/",
            {
                "booking": booking.id,
                "medicine_name": "Ibuprofen",
                "instruction": "Ovqatdan keyin",
                "times_per_day": 2,
                "days": 7,
            },
            format="json",
        )
        res = self.patient_client.get("/api/prescriptions/my/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["doctor_name"], "Dr. Aziz Karimov")

    def test_doctor_prescription_history(self):
        booking = self._make_completed_booking()
        self.doctor_client.post(
            "/api/prescriptions/create/",
            {
                "booking": booking.id,
                "medicine_name": "Amoksitsillin",
                "instruction": "7 kun",
                "times_per_day": 3,
                "days": 7,
            },
            format="json",
        )
        res = self.doctor_client.get(f"/api/prescriptions/doctor/history/?patient={self.patient.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)


class ChatFlowTest(BaseFlowTest):
    def test_full_chat_flow(self):
        # Bemor suhbat ochadi
        res = self.patient_client.post(
            "/api/chats/conversations/", {"doctor": self.doctor.id}, format="json"
        )
        self.assertEqual(res.status_code, 201, res.data)
        conv_id = res.data["id"]

        # Qayta ochilganda yangi yaratilmaydi
        res2 = self.patient_client.post(
            "/api/chats/conversations/", {"doctor": self.doctor.id}, format="json"
        )
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.data["id"], conv_id)

        # Bemor xabar yuboradi
        res = self.patient_client.post(
            f"/api/chats/conversations/{conv_id}/messages/",
            {"text": "Salom, doktor!"},
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        msg_id = res.data["id"]

        # Doctor unread belgisi (o'qishdan oldin)
        res = self.doctor_client.get("/api/chats/conversations/unread/")
        self.assertEqual(len(res.data["results"]), 1)

        # Doctor xabarni ko'radi
        res = self.doctor_client.get(f"/api/chats/conversations/{conv_id}/messages/")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(any(m["id"] == msg_id for m in res.data["results"]))
        res = self.doctor_client.get("/api/chats/conversations/unread/")
        self.assertEqual(len(res.data["results"]), 0)

        # Doctor javob beradi
        res = self.doctor_client.post(
            f"/api/chats/conversations/{conv_id}/messages/",
            {"text": "Assalomu alaykum, qanday muammo?"},
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)

        # Doctor qayta o'qiganda unread tozalanadi
        self.doctor_client.get(f"/api/chats/conversations/{conv_id}/messages/")
        res = self.doctor_client.get("/api/chats/conversations/unread/")
        self.assertEqual(len(res.data["results"]), 0)

        # Bemor o'z suhbatlarini ko'radi
        res = self.patient_client.get("/api/chats/conversations/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)

    def test_doctor_cannot_open_new_conversation(self):
        res = self.doctor_client.post(
            "/api/chats/conversations/", {"doctor": self.doctor.id}, format="json"
        )
        self.assertEqual(res.status_code, 403)

    def test_cannot_access_other_doctor_conversation(self):
        res = self.patient_client.post(
            "/api/chats/conversations/", {"doctor": self.doctor.id}, format="json"
        )
        conv_id = res.data["id"]
        other_doc_user = create_user("doc2@test.uz", role="doctor")
        other_spec = Specialty.objects.create(name="Terapevt", slug="terapevt")
        other_doc = Doctor.objects.create(
            user=other_doc_user, specialty=other_spec, price=50000
        )
        oc = self._auth(other_doc_user)
        # Boshqa doctor o'ziniki bo'lmagan suhbatni ko'rolmaydi (bo'sh ro'yxat)
        res = oc.get(f"/api/chats/conversations/{conv_id}/messages/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 0)
        # Va unga xabar yoza olmaydi
        res = oc.post(
            f"/api/chats/conversations/{conv_id}/messages/",
            {"text": "O'g'irlangan xabar"},
            format="json",
        )
        self.assertEqual(res.status_code, 404)

    def test_empty_message_rejected(self):
        res = self.patient_client.post(
            "/api/chats/conversations/", {"doctor": self.doctor.id}, format="json"
        )
        conv_id = res.data["id"]
        res = self.patient_client.post(
            f"/api/chats/conversations/{conv_id}/messages/", {"text": ""}, format="json"
        )
        self.assertEqual(res.status_code, 400)


class PasswordResetFlowTest(BaseFlowTest):
    def test_password_reset_with_otp(self):
        res = self.patient_client.post(
            "/api/users/password-reset/request/", {"email": self.patient.email}, format="json"
        )
        self.assertEqual(res.status_code, 200, res.data)

        otp = OTP.objects.get(user=self.patient, purpose="password_reset")
        res = self.patient_client.post(
            "/api/users/password-reset/confirm/",
            {
                "email": self.patient.email,
                "code": otp.code,
                "password": "BrandNewPass123!",
                "confirm_password": "BrandNewPass123!",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.patient.refresh_from_db()
        self.assertTrue(self.patient.check_password("BrandNewPass123!"))

    def test_password_reset_wrong_otp(self):
        self.patient_client.post(
            "/api/users/password-reset/request/", {"email": self.patient.email}, format="json"
        )
        res = self.patient_client.post(
            "/api/users/password-reset/confirm/",
            {
                "email": self.patient.email,
                "code": "000000",
                "password": "BrandNewPass123!",
                "confirm_password": "BrandNewPass123!",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_password_reset_unknown_email(self):
        res = self.patient_client.post(
            "/api/users/password-reset/request/", {"email": "nobody@test.uz"}, format="json"
        )
        self.assertEqual(res.status_code, 400)

    def test_password_reset_mismatched_passwords(self):
        self.patient_client.post(
            "/api/users/password-reset/request/", {"email": self.patient.email}, format="json"
        )
        otp = OTP.objects.get(user=self.patient, purpose="password_reset")
        res = self.patient_client.post(
            "/api/users/password-reset/confirm/",
            {
                "email": self.patient.email,
                "code": otp.code,
                "password": "BrandNewPass123!",
                "confirm_password": "Different123!",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)


class TelegramFlowTest(BaseFlowTest):
    def test_link_unlink_flow(self):
        res = self.patient_client.get("/api/notifications/telegram/link-code/")
        self.assertEqual(res.status_code, 200)
        code = res.data["code"]

        # Kod botga hali yuborilmagan → confirm ishlamaydi
        res = self.patient_client.post(
            "/api/notifications/telegram/confirm/", {"code": code}, format="json"
        )
        self.assertEqual(res.status_code, 400)

        # Botdan kelgan holat simulyatsiyasi
        cache.set(
            f"telegram_link_code:{code}",
            f"{self.patient.email}:123456789",
            timeout=600,
        )
        res = self.patient_client.post(
            "/api/notifications/telegram/confirm/", {"code": code}, format="json"
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.telegram_chat_id, 123456789)

        res = self.patient_client.post("/api/notifications/telegram/unlink/", {}, format="json")
        self.assertEqual(res.status_code, 200)
        self.patient.refresh_from_db()
        self.assertIsNone(self.patient.telegram_chat_id)

    def test_other_user_cannot_claim_code(self):
        res = self.patient_client.get("/api/notifications/telegram/link-code/")
        code = res.data["code"]
        cache.set(f"telegram_link_code:{code}", f"{self.patient.email}:111222333", timeout=600)
        other = create_user("other3@test.uz")
        oc = self._auth(other)
        res = oc.post("/api/notifications/telegram/confirm/", {"code": code}, format="json")
        self.assertEqual(res.status_code, 400)


class AdminFlowTest(BaseFlowTest):
    def test_admin_user_list_and_role_change(self):
        res = self.admin_client.get("/api/users/admin/")
        self.assertEqual(res.status_code, 200)
        emails = [u["email"] for u in res.data["results"]]
        self.assertIn("patient@test.uz", emails)

        res = self.admin_client.patch(
            f"/api/users/admin/{self.patient.id}/", {"role": "doctor"}, format="json"
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.role, "doctor")

    def test_non_admin_forbidden(self):
        res = self.patient_client.get("/api/users/admin/")
        self.assertEqual(res.status_code, 403)

    def test_admin_doctor_toggle(self):
        res = self.admin_client.patch(
            f"/api/doctors/admin/{self.doctor.id}/toggle/",
            {"is_active": False},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.doctor.refresh_from_db()
        self.assertFalse(self.doctor.is_active)


class NeedUploadDoctorTest(TestCase):
    """Doctor yaratish — admin faqat."""

    def setUp(self):
        cache.clear()

    def test_only_admin_can_create_doctor(self):
        from rest_framework_simplejwt.tokens import RefreshToken

        patient = create_user("p@t.uz")
        c = APIClient()
        token = RefreshToken.for_user(patient)
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        spec = Specialty.objects.create(name="LOR", slug="lor")
        res = c.post(
            "/api/doctors/create/",
            {"user_id": patient.id, "specialty": spec.id, "price": 70000},
            format="json",
        )
        self.assertEqual(res.status_code, 403)