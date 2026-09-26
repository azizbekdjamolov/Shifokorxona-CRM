"""Shifoxona AI uchun vision-capable generativ model xizmati.

Provider-agnostik: 
- AI_PROVIDER=gemini  -> native Gemini generateContent (AQ. Auth kalitlar bilan ishlaydi)
- AI_PROVIDER=openai  -> OpenAI-kompatibil /chat/completions (OpenRouter, Groq va b.)
API kalit faqat muhit o'zgaruvchisidan o'qiladi.
"""

import base64
import io
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger("apps")


class AIProviderError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


def _post_json(url, payload, headers=None, retries=4):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers=headers or {})
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", errors="replace")[:800]
            # Free tier "high demand" (503 UNAVAILABLE) vaqtincha — qayta urinamiz.
            if err.code == 503 and attempt < retries:
                import time

                time.sleep(3 * attempt)
                continue
            logger.error("AI HTTP %s: %s", err.code, detail)
            raise AIProviderError(
                f"AI model xatolik qaytardi ({err.code})", status_code=err.code
            ) from err
        except urllib.error.URLError as err:
            logger.error("AI tarmoq xatosi: %s", err.reason)
            raise AIProviderError("AI modelga ulanishda xatolik") from err
    raise AIProviderError("AI model vaqtincha band (503)", status_code=503)


def _encode_image(file_field):
    """ImageField/InMemoryUploadedFile nomini faylga aylantirib base64 qaytaradi."""
    if not file_field:
        return None
    try:
        mime = file_field.content_type or "image/jpeg"
    except AttributeError:
        mime = "image/jpeg"
    file_field.seek(0)
    raw = file_field.read()
    return mime, base64.b64encode(raw).decode("ascii")


def _gemini_system_payload(system_prompt):
    return [{"parts": [{"text": system_prompt}]}]


def call_gemini_native(model, system_prompt, messages, image_bytes=None):
    """Gemini native generateContent API.

    AQ. Auth kalit x-goog-api-key header yoki ?key= query orqali uzatiladi
    (OpenAI-compatibil Bearer \u2192 native bilan ishlamaydi).
    """
    api_key = settings.AI_API_KEY
    url = f"{settings.AI_BASE_URL}/models/{model}:generateContent"
    contents = []
    if image_bytes:
        mime, b64 = image_bytes
        text_part = {"text": messages[0]["text"]} if messages else {"text": ""}
        contents.append(
            {
                "role": "user",
                "parts": [
                    text_part,
                    {
                        "inline_data": {
                            "mime_type": mime,
                            "data": b64,
                        }
                    },
                ],
            }
        )
        messages = messages[1:]
    for msg in messages:
        contents.append(
            {"role": msg["role"], "parts": [{"text": msg["text"]}]}
        )
    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 2048,
        },
    }
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    data = _post_json(url, payload, headers=headers)
    try:
        candidates = data.get("candidates") or []
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        return "".join(p.get("text", "") for p in parts).strip()
    except (IndexError, KeyError, TypeError):
        logger.error("Gemini javob format kutilmagan: %s", str(data)[:500])
        raise AIProviderError("AI model javobini o'qib bo'lmadi")


def call_openai_compatible(model, system_prompt, messages, image_bytes=None):
    """OpenAI-kompatibil /chat/completions (OpenRouter, Groq, boshqa)."""
    api_key = settings.AI_API_KEY
    mime, b64 = image_bytes or (None, None)
    openai_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        openai_messages.append({"role": msg["role"], "content": msg["text"]})
    if b64:
        data_url = f"data:{mime};base64,{b64}"
        # Ovoxirgi user xabariga rasmni biriktiramiz.
        openai_messages[-1]["content"] = [
            {"type": "text", "text": openai_messages[-1]["content"] or ""},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]
    url = f"{settings.AI_BASE_URL}/chat/completions"
    payload = {
        "model": model,
        "messages": openai_messages,
        "temperature": 0.4,
        "max_tokens": 2048,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = _post_json(url, payload, headers=headers)
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (IndexError, KeyError, TypeError):
        logger.error("OpenAI javob format kutilmagan: %s", str(data)[:500])
        raise AIProviderError("AI model javobini o'qib bo'lmaydi")


def generate_ai_response(system_prompt, messages, image_field=None):
    """System prompt + xabarlar tarixi + (ixtiyoriy) rasm asosida javob qaytaradi."""
    image_bytes = _encode_image(image_field) if image_field else None
    model = settings.AI_MODEL
    if settings.AI_PROVIDER.lower() == "openai":
        return call_openai_compatible(model, system_prompt, messages, image_bytes)
    return call_gemini_native(model, system_prompt, messages, image_bytes)


def read_ai_image_base64(image_field):
    """Rasmni base64 qilib qaytaradi (sinov/test maqsadlari uchun)."""
    if not image_field:
        return None
    image_field.seek(0)
    return base64.b64encode(image_field.read()).decode("ascii")