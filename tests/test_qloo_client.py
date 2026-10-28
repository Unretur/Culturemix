import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import qloo_client  # noqa: E402
from qloo_client import QlooError, mock_search  # noqa: E402


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("QLOO_API_KEY", raising=False)
    with pytest.raises(QlooError, match="not set"):
        qloo_client.get_api_key()


def test_mock_is_labeled_mock():
    result = mock_search("Daft Punk", "urn:entity:artist")
    assert result["source"] == "MOCK"
