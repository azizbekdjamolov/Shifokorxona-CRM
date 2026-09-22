"""Professional demo-malumot to'ldirish: 1 admin + 10 shifokor.

Idempotent — qayta ishga tushirish dublikat yaratmaydi.
Parollar tasodifiy generatsiya qilinadi va faqat stdout'ga chiqariladi
(hech qaerga saqlanmaydi, commit'ga tushmaydi).
Bosh-ishga tushirish (Render deploy'da bir marta):
    python manage.py seed_demo
"""

import random
import string

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

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
    ("Aziz", "Karimov"), ("Malika", "Rahimova"), ("Jasur", "Toshpulatov"),
    ("Dilnoza", "Yusupova"), ("Bekzod", "Nazarov"), ("Gulnora", "Saidova"),
    ("Umid", "Islomov"), ("Nilufar", "A'zamova"), ("Sardor", "Umarov"),
    ("Zarina", "Qodirova"),
]


def _random_password(length: int = 14) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        pwd = "".join(random.SystemRandom().choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in pwd) and any(c.isupper() for c in pwd)
                and any(c.isdigit() for c in pwd)):
            return pwd


def _ensure_specialties() -> dict[str, Specialty]:
    mapping: dict[str, Specialty] = {}
    for name, slug, desc in DEMO_SPECIALTIES:
        spec, _ = Specialty.objects.get_or_create(slug=slug, defaults={
            "name": name, "description": desc,
        })
        mapping[slug] = spec
    return mapping


class Command(BaseCommand):
    help = "1 admin + 10 shifokor demo ma'lumotlarini yaratadi (idempotent)"

    def add_arguments(self, parser):
        parser.add_argument("--admin-email", default="admin@shifokorxona.uz")
        parser.add_argument("--noinput", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        email = options["admin_email"].strip().lower()
        specs = _ensure_specialties()
        credentials: list[str] = []

        if not User.objects.filter(email=email).exists():
            admin_pwd = _random_password()
            admin = User.objects.create_superuser(
                username=email, email=email, password=admin_pwd,
                first_name="Tizim", last_name="Administratori",
                role=User.Role.ADMIN, is_email_verified=True,
            )
            credentials.append(f"ADMIN  -> {email}  password: {admin_pwd}")

        spec_list = list(specs.values())
        profiled_users = {
            p.user.user.email
            for p in Doctor.objects.select_related("user__user")
        }
        for idx, (first, last) in enumerate(DOCTOR_NAMES, start=1):
            doc_email = f"doctor{idx}@shifokorxona.uz"
            if doc_email in profiled_users:
                continue
            pwd = _random_password()
            user = User.objects.create_user(
                username=doc_email, email=doc_email, password=pwd,
                first_name=first, last_name=last,
                role=User.Role.DOCTOR, is_email_verified=True,
            )
            spec = spec_list[(idx - 1) % len(spec_list)]
            doctor = Doctor.objects.create(
                user=user,
                specialty=spec,
                bio=f"{spec.name} bo'yicha {random.randint(3, 19)} yillik tajribaga ega shifokor.",
                experience_years=random.randint(3, 22),
                price=random.choice([80_000, 100_000, 120_000, 150_000, 200_000]),
                average_rating=round(random.uniform(4. rent.0, 5.0), 2),
            )
            for weekday in (0, 1, 2, 3, 4):
                DoctorSchedule.objects.get_or_create(doctor=doctor, weekday=weekday,
                    defaults={"start_time": "09:00", "end_time": "17:00"})
            credentials.append(f"DOCTOR{idx} -> {doc_email}  password: {pwd}")

        self.stdout.write(self.style.SUCCESS("\n=== Demo hisoblar (faqat bir marta ko'rsatiladi) ==="))
        for line in credentials:
            self.stdout.write(self.style.SUCCESS(line))
        self.stdout.write(self.style.WARNING(
            "\nIMPORTANT: parollar saqlanmaydi. Bu chiqishni darhol saqlab qo'ying."
        ))
