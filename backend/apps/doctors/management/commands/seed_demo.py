"""Professional demo-malumot to'ldirish: 1 admin + 10 shifokor.

Idempotent — qayta ishga tushirish dublikat yaratmaydi.
Parollar tasodifiy generatsiya qilinadi va faqat stdout'ga chiqariladi
(hech qaerga saqlanmaydi, commit'ga tushmaydi).
``--fixed-password`` berilsa — hamma demo hisoblarga bir xil parol o'rnatiladi.

Render startCommand'da deploy vaqtida avtomatik ishlaydi:
    python manage.py seed_demo --noinput
"""

import random
import secrets
import string

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.doctors.models import Doctor, DoctorSchedule, Specialty

User = get_user_model()

DEMO_SPECIALTIES = [
    ("Terapevt", "terapevt", "Umumiy kasalliklar bilan ishlaydi"),
    ("Kardiolog", "kardiolog", "Yurak-qon tomir kasalliklari"),
    ("Nevropatolog", "nevropatolog", "Asab tizimi kasalliklari"),
    ("Pediatr", "pediatr", "Bolalar kasalliklari"),
    ("Ortoped", "ortoped", "Suyak-bolakbam apparati"),
    ("Stomatolog", "stomatolog", "Tish va og'iz bo'shlig'i"),
    ("LOR", "lor", "Quloq, burun, tomoq"),
    ("Oftalmolog", "oftalmolog", "Ko'z kasalliklari"),
    ("Dermatolog", "dermatolog", "Teri kasalliklari"),
    ("Ginekolog", "ginekolog", "Ayollar salomatligi"),
]

DOCTOR_NAMES = [
    ("Aziz", "Karimov"), ("Malika", "Rahimova"), ("Jasur", "Toshpo'latov"),
    ("Dilnoza", "Yusupova"), ("Bekzod", "Nazarov"), ("Gulnora", "Saidova"),
    ("Umid", "Islomov"), ("Nilufar", "A'zamova"), ("Sardor", "Umarov"),
    ("Zarina", "Qodirova"),
]

DOCTOR_PRICES = [80_000, 100_000, 120_000, 150_000, 200_000]


def _make_password(length: int = 14, fixed: str | None = None) -> str:
    if fixed:
        return fixed
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        pwd = "".join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in pwd) and any(c.isupper() for c in pwd)
                and any(c.isdigit() for c in pwd)):
            return pwd


def _ensure_specialties() -> list[Specialty]:
    specs = []
    for name, slug, desc in DEMO_SPECIALTIES:
        spec, _ = Specialty.objects.get_or_create(slug=slug, defaults={
            "name": name, "description": desc,
        })
        specs.append(spec)
    return specs


class Command(BaseCommand):
    help = "1 admin + 10 shifokor demo ma'lumotlarini yaratadi (idempotent)"

    def add_arguments(self, parser):
        parser.add_argument("--admin-email", default="admin@shifokorxona.uz")
        parser.add_argument(
            "--fixed-password",
            help="Barcha demo hisoblarga shu parolni o'rnatish (demo uchun).",
        )
        parser.add_argument("--noinput", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        email = options["admin_email"].strip().lower()
        fixed = options["fixed_password"]
        specs = _ensure_specialties()
        credentials: list[str] = []

        if not User.objects.filter(email=email).exists():
            pwd = _make_password(fixed=fixed)
            User.objects.create_superuser(
                username=email, email=email, password=pwd,
                first_name="Tizim", last_name="Administratori",
                role=User.Role.ADMIN, is_email_verified=True,
            )
            credentials.append(f"ADMIN  -> {email}  password: {pwd}")

        existing_doctor_emails = set(
            Doctor.objects.select_related("user").values_list("user__email", flat=True)
        )

        for idx, (first, last) in enumerate(DOCTOR_NAMES, start=1):
            doc_email = f"doctor{idx}@shifokorxona.uz"
            if doc_email in existing_doctor_emails:
                continue
            pwd = _make_password(fixed=fixed)
            user = User.objects.create_user(
                username=doc_email, email=doc_email, password=pwd,
                first_name=first, last_name=last,
                role=User.Role.DOCTOR, is_email_verified=True,
            )
            spec = specs[(idx - 1) % len(specs)]
            Doctor.objects.create(
                user=user,
                specialty=spec,
                bio=f"{spec.name} bo'yicha tajribali shifokor.",
                experience_years=random.randint(3, 22),
                price=random.choice(DOCTOR_PRICES),
                average_rating=round(random.uniform(4.0, 5.0), 2),
            )
            for weekday in DoctorSchedule.Weekday:
                DoctorSchedule.objects.get_or_create(
                    doctor=user.doctor_profile, weekday=weekday,
                    defaults={
                        "start_time": "09:00",
                        "end_time": "17:00",
                        "is_working": weekday < 5,
                    },
                )
            credentials.append(f"DOCTOR{idx} -> {doc_email}  password: {pwd}")

        if credentials:
            self.stdout.write(self.style.SUCCESS("\n=== Demo hisoblar ==="))
            for line in credentials:
                self.stdout.write(self.style.SUCCESS(line))
            self.stdout.write(self.style.WARNING(
                "\nIMPORTANT: parollar saqlanmaydi. Bu chiqishni darhol saqlab qo'ying."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                "Barcha demo hisoblar allaqachon mavjud."
            ))