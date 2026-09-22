"""Professional demo-data seed — 1 admin + 10 shifokor, idempotent.

Ishlatish (backend venv'da):
    python manage.py seed_demo
    python manage.py seed_demo --fixed-password 'Shifokor@2026'

Oddiy holatda parollar random generatsiya qilinadi va terminalga chiqariladi
(yangiliklar uchun). ``--fixed-password`` berilsa — hamma demo hisoblarga bir xil
parol o'rnatiladi (demo/staging uchun qulay). Agar hisob allaqachon mavjud bo'lsa,
hech narsa qayta yaratilmaydi — xavfsiz va takror bajariladigan.
"""

import secrets
import string

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.doctors.models import Doctor, DoctorSchedule, Specialty
from apps.users.models import User

User = get_user_model()


def _random_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        candidate = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in candidate)
            and any(c.isupper() for c in candidate)
            and any(c.isdigit() for c in candidate)
        ):
            return candidate


DEMO_DOCTORS = [
    # (email prefix, first_name, last_name, specialty_slug, experience_years)
    ("doctor1", "Aziz", "Karimov", "kardiolog", 12),
    ("doctor2", "Malika", "Rahimova", "nevropatolog", 9),
    ("doctor3", "Jasur", "Toshpo'latov", "pediatr", 15),
    ("doctor4", "Dilnoza", "Yusupova", "terapevt", 11),
    ("doctor5", "Bekzod", "Nazarov", "ortoped", 7),
    ("doctor6", "Gulnoza", "Saidova", "stomatolog", 13),
    ("doctor7", "Umid", "Islomov", "otorinolaringolog", 6),
    ("doctor8", "Nilufar", "Xamidova", "oftalmolog", 10),
    ("doctor9", "Sardor", "Umarov", "dermatolog", 8),
    ("doctor10", "Zilola", "Qodirova", "ginekolog", 14),
]


class Command(BaseCommand):
    help = "Demo ma'lumotlar: 1 admin + 10 shifokor (idempotent, parollar terminalda)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixed-password",
            help="Barcha demo hisoblarga shu parolni o'rnatish (demo/staging uchun).",
        )
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            help="Mavjud demo hisoblarga ham parolni qayta o'rnatish (idempotent emas, ogoh bo'ling).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        from apps.users.services.otp_service import issue_tokens_for_user  # noqa: F401

        fixed_password = options.get("fixed_password")
        reset_mode = bool(options.get("reset_passwords") or fixed_password)
        created_credentials = []
        updated_credentials = []

        admin_email = "admin@shifokorxona.uz"
        admin_user = User.objects.filter(email__iexact=admin_email).first()
        if admin_user is None:
            password = fixed_password or _random_password()
            User.objects.create_superuser(
                username=admin_email,
                email=admin_email,
                password=password,
                role=User.Role.ADMIN,
                is_email_verified=True,
                first_name="Tizim",
                last_name="Administratori",
            )
            created_credentials.append((admin_email, password))
        elif reset_mode:
            password = fixed_password or _random_password()
            admin_user.set_password(password)
            admin_user.save(update_fields=["password"])
            updated_credentials.append((admin_email, password))

        specialties = {s.slug: s for s in Specialty.objects.all()}

        for prefix, first, last, spec_slug, exp in DEMO_DOCTORS:
            email = f"{prefix}@shifokorxona.uz"
            user = User.objects.filter(email__iexact=email).first()
            if user is None:
                password = fixed_password or _random_password()
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    role=User.Role.DOCTOR,
                    is_email_verified=True,
                    first_name=first,
                    last_name=last,
                )
                Doctor.objects.create(
                    user=user,
                    specialty=specialties.get(spec_slug),
                    is_active=True,
                    experience_years=exp,
                    price=100_000,
                )
                for weekday in DoctorSchedule.Weekday:
                    DoctorSchedule.objects.get_or_create(
                        doctor=user.doctor_profile,
                        weekday=weekday,
                        defaults={"start_time": "09:00", "end_time": "17:00", "is_working": weekday < 5},
                    )
                created_credentials.append((email, password))
            elif reset_mode:
                password = fixed_password or _random_password()
                user.set_password(password)
                user.save(update_fields=["password"])
                updated_credentials.append((email, password))

        rows = created_credentials + updated_credentials
        if rows:
            self.stdout.write(
                self.style.SUCCESS("Demo hisoblar parollari (terminalga bir marta chiqariladi):")
            )
            for email, password in rows:
                self.stdout.write(self.style.SUCCESS(f"✓ {email}  →  parol: {password}"))
        else:
            self.stdout.write(
                self.style.WARNING("Barcha demo hisoblar allaqachon mavjud va parollar saqlanib qoldi.")
            )
