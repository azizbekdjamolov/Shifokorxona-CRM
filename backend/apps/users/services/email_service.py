"""Professional email service — Brevo (Sendinblue) Transactional Email API v3.

Faqat HTML transactional xabarlarni (OTP, tasdiqlash) yuborish uchun ishlatiladi.
API kaliti env orqali beriladi (`BREVO_API_KEY`) va hech qachon repo'ga yozilmaydi.
"""

from __future__ import annotations

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

BREVO_ENDPOINT = getattr(settings, "BREVO_ENDPOINT", "https://api.brevo.com/v3/smtp/email")
SENDER_NAME = getattr(settings, "BREVO_SENDER_NAME", "Shifokorxona CRM")


def _brevo_available() -> bool:
    api_key = getattr(settings, "BREVO_API_KEY", "").strip()
    return bool(api_key)


def build_otp_html(code: str, minutes: int, cta_url: str = "") -> str:
    """Shifokorxona brendi bilan professional HTML email shabloni."""
    brand = SENDER_NAME
    return f"""<!doctype html>
<html lang="uz">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{code} — Tasdiqlash kodi</title>
  </head>
  <body style="margin:0;padding:0;background:#f4f6fb;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6fb;padding:24px 0;">
      <tr><td align="center">
        <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(15,23,42,.08);">
          <tr>
            <td style="background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 55%,#d946ef 100%);padding:28px 30px;text-align:center;">
              <span style="font-size:24px;font-weight:700;letter-spacing:.5px;color:#ffffff;">{brand}</span>
              <div style="font-size:13px;color:rgba(255,255,255,.85);margin-top:4px;">Shifokorlar bilan ishlash platformasi</div>
            </td>
          </tr>
          <tr><td style="padding:32px 34px;">
            <h1 style="margin:0 0 16px;font-size:19px;color:#0f172a;font-weight:600;">Tasdiqlash kodi</h1>
            <p style="margin:0 0 22px;font-size:14px;line-height:1.55;color:#334155;">
              Xurmatli foydalanuvchi! Quyidagi bir martalik kod yordamida hisobingizni tasdiqlang.
            </p>
            <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 auto 24px;background:#eef2ff;border:1px solid #c7d2fe;border-radius:10px;">
              <tr><td style="padding:14px 34px;">
                <span style="font-size:34px;font-weight:700;letter-spacing:8px;color:#4338ca;line-height:1;">{code}</span>
              </td></tr>
            </table>
            <p style="margin:0 0 6px;font-size:13px;color:#64748b;line-height:1.5;">
              Kod <strong>{minutes} daqiqa</strong> amal qiladi. Hech kimga bermang,
              adminlarimiz kodni hech qachon so'ramaydi.
            </p>
            {f'<p style="margin:16px 0 0;"><a href="{cta_url}" style="display:inline-block;background:#6366f1;color:#ffffff;text-decoration:none;padding:12px 26px;border-radius:8px;font-size:14px;font-weight:600;">Sahifaga o&apos;tish</a></p>' if cta_url else ""}
          </td></tr>
          <tr>
            <td style="background:#f8fafc;padding:18px 30px;text-align:center;">
              <span style="font-size:12px;color:#94a3b8;">© Shifokorxona CRM — Bu xabar avtomatik yuborildi, javob yozmang.</span>
            </td>
          </tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>"""


def send_transactional_email(to_email: str, subject: str, html_body: str) -> bool:
    """Brevo V3 orqali transactional HTML email yuboradi. Xatolikda False qaytaradi."""
    if not _brevo_available():
        logger.warning("BREVO_API_KEY o'rnatilmagan — email jo'natilmadi (%s)", to_email)
        return False

    payload = {
        "sender": {
            "name": SENDER_NAME,
            "email": getattr(settings, "EMAIL_HOST_USER", "noreply@example.com"),
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_body,
    }
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }
    try:
        resp = requests.post(
            BREVO_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        logger.info("Email yuborildi -> %s (subject: %s)", to_email, subject)
        return True
    except requests.RequestException as exc:
        logger.exception("Brevo email jo'natilmadi -> %s: %s", to_email, exc)
        return False
