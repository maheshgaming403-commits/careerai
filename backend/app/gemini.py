import json
import os
import httpx


def ask_gemini(prompt: str) -> dict:
    """Call Gemini with a JSON-mode prompt. Raises on failure so callers can fall back."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not configured")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-1.5-flash:generateContent?key=" + api_key
    )
    with httpx.Client(timeout=45) as client:
        resp = client.post(
            url,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"},
            },
        )
        if resp.status_code == 429:
            raise RuntimeError("Gemini rate limit hit")
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)
