"""Budget and schedule validation. Pure Python, no network calls."""
from dataclasses import dataclass


@dataclass
class LineItem:
    name: str
    cost: float
    # "estimate" until a real vendor quote exists. Never presented as a real price.
    source: str = "estimate"


@dataclass
class BudgetCheck:
    total: float
    budget: float
    within_budget: bool
    remaining: float


def check_budget(items: list[LineItem], budget: float) -> BudgetCheck:
    if budget < 0:
        raise ValueError("budget must be non-negative")
    total = sum(item.cost for item in items)
    return BudgetCheck(
        total=total,
        budget=budget,
        within_budget=total <= budget,
        remaining=budget - total,
    )
