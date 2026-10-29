"""Event planning: budget estimates, plan validation, and the grounded plan call."""
import json
from dataclasses import dataclass

from llm import parse_json_block


@dataclass
class LineItem:
    name: str
    cost: float
    source: str = "estimate"


@dataclass
class BudgetCheck:
    total: float
    budget: float
    within_budget: bool
    remaining: float


class PlanError(Exception):
    pass


def check_budget(items: list[LineItem], budget: float) -> BudgetCheck:
    if budget < 0:
        raise ValueError("budget must be non-negative")
    total = sum(item.cost for item in items)
    return BudgetCheck(total=total, budget=budget, within_budget=total <= budget, remaining=budget - total)


# Planning placeholders in INR. NOT vendor quotes. Replace with sourced figures
# before presenting any cost as realistic.
PLANNING_ESTIMATES_INR = {
    "Venue hire (one day)": 150_000,
    "Artist fee (one act)": 60_000,
    "Food and beverage": 120_000,
    "Production and sound": 80_000,
    "Marketing": 50_000,
}
CONTINGENCY_RATE = 0.10


def cost_items() -> list[LineItem]:
    items = [LineItem(name, float(cost)) for name, cost in PLANNING_ESTIMATES_INR.items()]
    subtotal = sum(i.cost for i in items)
    items.append(LineItem(f"Contingency ({int(CONTINGENCY_RATE * 100)}%)", round(subtotal * CONTINGENCY_RATE, 2)))
    return items


PROMPT = """You are designing a cultural event plan.

Event brief (JSON):
__BRIEF__

Cultural evidence (JSON list). Items with source "qloo" come from the Qloo API. Items with source "mock" are development placeholders.
__EVIDENCE__

Rules:
- A recommendation with source "qloo" or "mock" must use a name that appears in the evidence list.
- Any other suggestion must use source "hypothesis" and must not be presented as cultural data.
- Do not state prices, attendance figures, or partnerships.
- Reply with JSON only, no prose, with exactly these keys:
  "concept": string
  "schedule": list of {"time": string, "activity": string}
  "recommendations": list of {"name": string, "type": string, "reason": string, "source": "qloo" | "mock" | "hypothesis"}
  "assumptions": list of strings
"""

REQUIRED_KEYS = ("concept", "schedule", "recommendations", "assumptions")
ALLOWED_SOURCES = {"qloo", "mock", "hypothesis"}
GROUNDED_SOURCES = {"qloo", "mock"}


def validate_plan(data: dict, evidence: list[dict]) -> list[str]:
    problems = [f"missing '{k}'" for k in REQUIRED_KEYS if k not in data]
    if problems:
        return problems
    if not isinstance(data["schedule"], list) or not data["schedule"]:
        problems.append("schedule is empty")
    known = {e["name"] for e in evidence}
    for r in data["recommendations"]:
        if not isinstance(r, dict) or not r.get("name"):
            problems.append("recommendation without a name")
            continue
        source = r.get("source")
        if source not in ALLOWED_SOURCES:
            problems.append(f"recommendation '{r['name']}' has unknown source")
        elif source in GROUNDED_SOURCES and r["name"] not in known:
            problems.append(f"recommendation '{r['name']}' is not in the evidence list")
    return problems


def build_plan(brief: dict, evidence: list[dict], ask) -> dict:
    """ask is a function: prompt string -> model text. Injected so tests can fake it."""
    prompt = PROMPT.replace("__BRIEF__", json.dumps(brief, ensure_ascii=False)).replace(
        "__EVIDENCE__", json.dumps(evidence, ensure_ascii=False)
    )
    data = parse_json_block(ask(prompt))
    problems = validate_plan(data, evidence)
    if problems:
        raise PlanError("Plan failed checks: " + "; ".join(problems))
    items = cost_items()
    return {"plan": data, "costs": items, "budget": check_budget(items, brief["budget"])}