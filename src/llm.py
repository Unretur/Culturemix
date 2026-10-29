"""Gemini wrapper. The model name lives here so it's changed in one place."""
import json
import os
import re
import time
from pathlib import Path

GEMINI_MODEL = "gemini-3-flash-preview"  # preview model; change here if Google retires it
MAX_RETRIES = 4


class LLMError(Exception):
    pass


def load_key(name: str) -> str:
    """Read a key from the environment, falling back to the .env file in the project root."""
    value = os.environ.get(name, "").strip()
    if value:
        return value
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip()
    return ""


def ask_gemini(prompt: str) -> str:
    key = load_key("GEMINI_API_KEY")
    if not key:
        raise LLMError("GEMINI_API_KEY is not set")
    from google import genai  # imported here so tests run without the package

    client = genai.Client(api_key=key)
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            return response.text or ""
        except Exception as exc:
            last_error = exc
            code = getattr(exc, "code", None)
            if code not in (429, 500, 503):
                raise LLMError(f"Gemini request failed: {exc}") from exc
            time.sleep(2 ** attempt * 2)
    raise LLMError(f"Gemini is busy after {MAX_RETRIES} tries. Wait a minute and try again. ({last_error})")


def parse_json_block(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise LLMError("Model did not return JSON")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise LLMError(f"Model returned invalid JSON: {exc}") from exc