"""Navbat eslatmalarini yuboruvchi management command.

Ishga tushirish:
    python manage.py send_booking_reminders          # bir martalik
    python manage.py send_booking_reminders --loop   # doimiy (worker)
"""

import time

from django.core.management.base import BaseCommand

from apps.bookings.services.reminder_service import send_due_reminders


class Command(BaseCommand):
    help = "Navbatiga 5 daqiqa qolgan bronlarga email eslatma yuboradi"

    def add_arguments(self, parser):
        parser.add_argument(
            "--loop",
            action="store_true",
            help="Har 60 soniyada chektsiz ishlash (Render worker uchun)",
        )

    def handle(self, *args, **options):
        if not options["loop"]:
            sent = send_due_reminders()
            self.stdout.write(self.style.SUCCESS(f"Yuborildi: {sent}"))
            return

        self.stdout.write("Navbat eslatma worker ishga tushdi (har 60s)")
        while True:
            try:
                sent = send_due_reminders()
                if sent:
                    self.stdout.write(f"Ish markasi: {sent} email yuborildi")
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(f"Xato: {exc}")
            time.sleep(60)