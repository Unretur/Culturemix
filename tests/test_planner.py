import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from planner import LineItem, check_budget  # noqa: E402


def test_within_budget():
    items = [LineItem("Venue", 300_000), LineItem("Artists", 400_000)]
    result = check_budget(items, 1_000_000)
    assert result.total == 700_000
    assert result.within_budget is True
    assert result.remaining == 300_000


def test_over_budget():
    items = [LineItem("Venue", 600_000), LineItem("Artists", 500_000)]
    result = check_budget(items, 1_000_000)
    assert result.within_budget is False
    assert result.remaining == -100_000


def test_exact_budget_is_within():
    result = check_budget([LineItem("All", 1_000_000)], 1_000_000)
    assert result.within_budget is True


def test_negative_budget_rejected():
    with pytest.raises(ValueError):
        check_budget([], -1)
