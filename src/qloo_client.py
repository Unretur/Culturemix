import os
from pathlib import Path

import requests

BASE_URL = "https://hackathon.api.qloo.com"
DEFAULT_TIMEOUT = 10
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class QlooError(Exception):
    """Any failure talking to Qloo. The UI shows the message."""


def load_env_value(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if value:
        return value
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip()
    return ""


def get_api_key() -> str:
    key = load_env_value("QLOO_API_KEY")
    if not key:
        raise QlooError("QLOO_API_KEY is not set")
    return key


def live_search(query: str, entity_type: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    try:
        response = requests.get(
            f"{BASE_URL}/search",
            params={"query": query, "types": entity_type},
            headers={"X-Api-Key": get_api_key()},
            timeout=timeout,
        )
    except requests.Timeout as exc:
        raise QlooError("Qloo request timed out") from exc
    except requests.RequestException as exc:
        raise QlooError(f"Qloo request failed: {exc}") from exc

    if response.status_code in (401, 403):
        raise QlooError(f"Qloo rejected the key (HTTP {response.status_code})")
    if response.status_code == 429:
        raise QlooError("Qloo rate limit reached. Wait and try again.")
    if not response.ok:
        raise QlooError(f"Qloo returned HTTP {response.status_code}")

    try:
        return response.json()
    except ValueError as exc:
        raise QlooError("Qloo returned a non-JSON response") from exc


def mock_search(query: str, entity_type: str) -> dict:
    """Development-only stand-in. Always labelled MOCK. Never a Qloo result."""
    return {
        "source": "MOCK",
        "results": [{"name": f"[mock] {query}", "types": [entity_type]}],
    }


def normalize_search(payload: dict, live: bool) -> list[dict]:
    """Turn a Qloo search response into rows the UI and planner can use."""
    source = "qloo" if live else "mock"
    items = payload.get("results") or []
    out = []
    for item in items[:10]:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        types = item.get("types") or ["unknown"]
        tags = [t["name"] for t in item.get("tags", []) if isinstance(t, dict) and t.get("name")]
        out.append({
            "name": item["name"],
            "type": str(types[0]).split(":")[-1],
            "entity_id": item.get("entity_id", ""),
            "tags": ", ".join(tags[:5]),
            "source": source,
        })
    return out