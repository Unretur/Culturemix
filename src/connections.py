"""Links between Qloo entities, based only on the tags Qloo returned."""
from itertools import combinations


def _tagset(tags_text: str) -> set[str]:
    return {t.strip().lower() for t in tags_text.split(",") if t.strip()}


def shared_tag_links(evidence: list[dict]) -> list[dict]:
    """Pairs of live Qloo rows that share at least one tag. Mock rows have no tags, so they never link."""
    rows = [e for e in evidence if e.get("source") == "qloo"]
    links = []
    for a, b in combinations(rows, 2):
        shared = sorted(_tagset(a.get("tags", "")) & _tagset(b.get("tags", "")))
        if shared:
            links.append({"a": a["name"], "b": b["name"], "shared": shared})
    return links