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
            user = User.objects.get(email__iexact=email)
            user.is_staff = True
            user.is_superuser = True
            user.role = User.Role.ADMIN
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Admin yangilandi: {email}"))
        else:
            User.objects.create_superuser(
                username=email,
                email=email,
                password=password,
                role=User.Role.ADMIN,
            )
            self.stdout.write(self.style.SUCCESS(f"Admin yaratildi: {email}"))