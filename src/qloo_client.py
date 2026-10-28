"""Qloo hackathon API client.

Live calls use the X-Api-Key header against the hackathon base URL.
Endpoint paths and parameters are UNVERIFIED until a live request is
inspected. Update them after the first successful call.
"""
import os

import requests

BASE_URL = "https://hackathon.api.qloo.com"
DEFAULT_TIMEOUT = 10


class QlooError(Exception):
    """Any failure talking to Qloo. The UI shows the message."""


def get_api_key() -> str:
    key = os.environ.get("QLOO_API_KEY", "").strip()
    if not key:
        raise QlooError("QLOO_API_KEY is not set")
    return key


def live_search(query: str, entity_type: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Call the search endpoint. Returns the parsed JSON body."""
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

    if response.status_code == 401 or response.status_code == 403:
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
    """Development-only stand-in. Always labeled MOCK. Never a Qloo result."""
    return {
        "source": "MOCK",
        "results": [{"name": f"[mock] {query}", "type": entity_type}],
    }
