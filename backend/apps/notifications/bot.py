import asyncio
import secrets

from django.conf import settings
from django.core.cache import cache

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

LINK_CODE_TTL = 600
link_prefix = "telegram_link_code"


def generate_link_code():
    return secrets.token_hex(4).upper()


def store_link_code(user_email):
    code = generate_link_code()
    cache.set(f"{link_prefix}:{code}", user_email, timeout=LINK_CODE_TTL)
    return code


def get_link_owner(code):
    return cache.get(f"{link_prefix}:{code}")


def clear_link_code(code):
    cache.delete(f"{link_prefix}:{code}")


def get_bot():
    if not settings.TELEGRAM_BOT_TOKEN:
        return None
    return Bot(token=settings.TELEGRAM_BOT_TOKEN)


def send_telegram_message(chat_id, text):
    bot = get_bot()
    if bot is None or not chat_id:
        return False
    try:
        asyncio.run(bot.send_message(chat_id=chat_id, text=text))
        return True
    except Exception:
        return False


async def _start_handler(message: Message):
    await message.answer(
        "Shifokorxona CRM botiga xush kelibsiz!\n\n"
        "Telegram akkountingizni saytga ulash uchun"
        "saytdan olingan kodni ushbu chatga yuboring."
    )


async def _code_handler(message: Message):
    code = message.text.strip().upper()
    owner = get_link_owner(code)
    if owner:
        cache.set(f"{link_prefix}:{code}", f"{owner}:{message.chat.id}", timeout=LINK_CODE_TTL)
        await message.answer("Kod qabul qilindi. Saytdagi panelda tasdiqlash tugmasini bosing.")
    else:
        await message.answer("Noto'g'ri yoki muddati o'tgan kod.")


def start_polling():
    bot = get_bot()
    if bot is None:
        return
    dp = Dispatcher()
    dp.message.register(_start_handler, CommandStart())
    dp.message.register(_code_handler)
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    start_polling()