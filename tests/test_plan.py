import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm import LLMError  # noqa: E402
from planner import PlanError, build_plan, cost_items  # noqa: E402
from qloo_client import normalize_search  # noqa: E402

EVIDENCE = [{"name": "Nucleya", "type": "artist", "source": "mock"}]
BRIEF = {"city": "Mumbai", "budget": 1_000_000, "interest": "independent music"}


def plan_json(**overrides):
    data = {
        "concept": "Pop-up listening night",
        "schedule": [{"time": "18:00", "activity": "Live set"}],
        "recommendations": [
            {"name": "Nucleya", "type": "artist", "reason": "matches interest", "source": "mock"}
        ],
        "assumptions": ["venue is available"],
    }
    data.update(overrides)
    return json.dumps(data)


def test_valid_plan_is_within_budget():
    result = build_plan(BRIEF, EVIDENCE, lambda p: plan_json())
    assert result["budget"].within_budget is True


def test_invented_name_marked_qloo_is_rejected():
    bad = plan_json(recommendations=[{"name": "Made Up Band", "type": "artist", "reason": "x", "source": "qloo"}])
    with pytest.raises(PlanError):
        build_plan(BRIEF, EVIDENCE, lambda p: bad)


def test_hypothesis_is_allowed_without_evidence():
    ok = plan_json(recommendations=[{"name": "Street food stall", "type": "food", "reason": "idea", "source": "hypothesis"}])
    build_plan(BRIEF, EVIDENCE, lambda p: ok)


def test_non_json_reply_is_rejected():
    with pytest.raises(LLMError):
        build_plan(BRIEF, EVIDENCE, lambda p: "sorry, no json here")


def test_costs_are_labelled_estimates():
    assert all(i.source == "estimate" for i in cost_items())


def test_normalize_search_labels_mock_source():
    out = normalize_search({"results": [{"name": "A", "types": ["urn:entity:artist"]}]}, live=False)
    assert out[0]["name"] == "A"
    assert out[0]["type"] == "artist"
    assert out[0]["source"] == "mock"