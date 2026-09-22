from typing import Any

from django.conf import settings
from django.db import connection


def get_health_payload() -> dict[str, Any]:
    db_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # noqa: BLE001 - health check must never raise
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "error",
        "debug": bool(settings.DEBUG),
    }
