# Generated manually: payments app olib tashlanganidan keyin eski jadvalni o'chirish.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0004_booking_unique_active_booking_slot"),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS payments_payment;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]