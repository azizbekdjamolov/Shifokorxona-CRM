from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = "Admin (superuser) yaratadi: create_admin <email> <password>"

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("password")

    def handle(self, *args, **options):
        email = options["email"].lower()
        password = options["password"]
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