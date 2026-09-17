import os

from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = "Admin (superuser) yaratadi: create_admin [email] [password]"

    def add_arguments(self, parser):
        parser.add_argument("email", nargs="?", default=os.environ.get("DJANGO_ADMIN_EMAIL"))
        parser.add_argument(
            "password", nargs="?", default=os.environ.get("DJANGO_ADMIN_PASSWORD")
        )

    def handle(self, *args, **options):
        email = (options["email"] or "").lower()
        password = options["password"] or ""
        if not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Email/password berilmagan (DJANGO_ADMIN_EMAIL/DJANGO_ADMIN_PASSWORD yoki argument)"
                )
            )
            return
        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write(self.style.WARNING(f"Admin allaqachon mavjud: {email}"))
            return
        User.objects.create_superuser(
            username=email,
            email=email,
            password=password,
            role=User.Role.ADMIN,
        )
        self.stdout.write(self.style.SUCCESS(f"Admin yaratildi: {email}"))