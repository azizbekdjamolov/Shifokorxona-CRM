"""Bitta demo shifokorga ma'lum parol o'rnatadi.

Render'da bir martalik ishga tushiriladi:
    python manage.py set_doctor_password doctor1@shifokorxona.uz 'MyPass123!'
"""

import sys

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Shifokor yoki istalgan user parolini yangilaydi"

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("password")

    @transaction.atomic
    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        password = options["password"]
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            self.stderr.write(self.style.ERROR(f"User topilmadi: {email}"))
            sys.exit(1)
        user.set_password(password)
        user.save(update_fields=["password"])
        self.stdout.write(self.style.SUCCESS(f"Parol yangilandi: {email}"))