"""
Gemini API client for admin AI automations.

Uses only the Python standard library (urllib) so no extra dependency is
required. Every call is wrapped so that a missing/invalid key or a network
failure NEVER raises — it returns a structured result the caller can fall back
on. This keeps admin dashboards rendering even when the API is unavailable.
"""
import json
import urllib.error
import urllib.request

from django.conf import settings

GENERATE_CONTENT_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={key}"
)


def is_configured():
    """True when a Gemini API key is present in settings/env."""
    return bool(getattr(settings, "GEMINI_API_KEY", "") or "")


def _extract_text(payload):
    """Pull the first non-empty text part out of a generateContent response."""
    try:
        for candidate in payload.get("candidates", []):
            parts = candidate.get("content", {}).get("parts", [])
            for part in parts:
                text = (part.get("text") or "").strip()
                if text:
                    return text
    except AttributeError:
        pass
    return ""


def generate_text(prompt, system=None, temperature=0.4, max_output_tokens=1200):
    """
    Send a prompt to Gemini and return a result dict:
      {ok, text, source, model, error}

    - source is 'gemini' on a live success, otherwise 'unconfigured'/'fallback'.
    - This function never raises; callers should check result['ok'].
    """
    key = getattr(settings, "GEMINI_API_KEY", "") or ""
    model = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
    timeout = getattr(settings, "GEMINI_TIMEOUT", 20)

    if not key:
        return {"ok": False, "text": "", "source": "unconfigured",
                "model": model, "error": "GEMINI_API_KEY is not set."}

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
        },
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}

    url = GENERATE_CONTENT_URL.format(model=model, key=key)
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        text = _extract_text(body)
        if text:
            return {"ok": True, "text": text, "source": "gemini",
                    "model": model, "error": ""}
        return {"ok": False, "text": "", "source": "gemini",
                "model": model, "error": "Gemini returned an empty response."}
    except urllib.error.HTTPError as exc:  # 401/403/400 etc.
        detail = ""
        try:
            detail = exc.read().decode("utf-8", "ignore")[:200]
        except Exception:
            detail = str(exc)
        return {"ok": False, "text": "", "source": "gemini",
                "model": model, "error": f"HTTP {exc.code}: {detail}"}
    except Exception as exc:  # network/DNS/timeout/JSON
        return {"ok": False, "text": "", "source": "gemini",
                "model": model, "error": str(exc)[:200]}
