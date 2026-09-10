import json
import os
import httpx


def ask_gemini(prompt: str) -> dict:
    """
    Sends a prompt to Gemini and returns a Python dictionary.

    Requires:
    GEMINI_API_KEY=your_api_key
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it in Render Environment Variables."
        )

    # You can change this through Render without changing the code.
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model}:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            prompt
                            + "\n\nIMPORTANT: Return ONLY valid JSON. "
                              "Do not use markdown. Do not use ```json. "
                              "Do not add explanations before or after the JSON."
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.7,
            "max_output_tokens": 4096
        }
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                url,
                headers=headers,
                json=payload
            )

        # Give useful error messages
        if response.status_code == 429:
            raise RuntimeError(
                "Gemini rate limit reached. Please try again later."
            )

        if response.status_code == 401 or response.status_code == 403:
            raise RuntimeError(
                "Gemini API key is invalid or does not have permission."
            )

        if response.status_code == 404:
            raise RuntimeError(
                f"Gemini model '{model}' was not found or is unavailable."
            )

        response.raise_for_status()

        data = response.json()

        # Check if Gemini returned a valid candidate
        candidates = data.get("candidates", [])

        if not candidates:
            raise RuntimeError(
                f"Gemini returned no response: {json.dumps(data)}"
            )

        parts = candidates[0].get("content", {}).get("parts", [])

        if not parts:
            raise RuntimeError(
                f"Gemini response contains no text: {json.dumps(data)}"
            )

        text = parts[0].get("text", "").strip()

        if not text:
            raise RuntimeError("Gemini returned an empty response.")

        # Convert Gemini JSON text into Python dictionary
        return json.loads(text)

    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Gemini returned invalid JSON: {e}"
        )

    except httpx.TimeoutException:
        raise RuntimeError(
            "Gemini request timed out. Please try again."
        )

    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"Gemini API error {e.response.status_code}: {e.response.text}"
        )

    except httpx.RequestError as e:
        raise RuntimeError(
            f"Could not connect to Gemini API: {str(e)}"
        )