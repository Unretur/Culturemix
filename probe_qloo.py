import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
key = ""
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if line.startswith("QLOO_API_KEY="):
        key = line.split("=", 1)[1].strip()
if not key:
    sys.exit("QLOO_API_KEY is missing from .env")

BASE = "https://hackathon.api.qloo.com"
CALLS = [
    ("artist: Daft Punk", "/search", {"query": "Daft Punk", "types": "urn:entity:artist"}),
    ("place: Mumbai", "/search", {"query": "Mumbai", "types": "urn:entity:place"}),
]

out = {}
for label, path, params in CALLS:
    r = requests.get(BASE + path, params=params, headers={"X-Api-Key": key}, timeout=15)
    print(f"\n{label}: HTTP {r.status_code}")
    try:
        body = r.json()
    except ValueError:
        body = {"raw": r.text[:500]}
    out[label] = {"status": r.status_code, "body": body}
    if isinstance(body, dict):
        print("  top-level keys:", list(body.keys()))
        for k, v in body.items():
            if isinstance(v, list) and v:
                first = v[0]
                shape = list(first.keys()) if isinstance(first, dict) else type(first).__name__
                print(f"  '{k}' has {len(v)} items; first item fields: {shape}")
                break

target = ROOT.parent / "qloo_probe_output.json"
target.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nFull response saved to {target} (outside the repo, so it won't be committed)")
