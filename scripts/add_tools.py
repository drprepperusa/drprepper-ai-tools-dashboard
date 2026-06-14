#!/usr/bin/env python3
"""Merge new dashboard tool entries into data/tools.json.

Input format: JSON array of objects with the same fields used in data/tools.json.
The script deduplicates by postUrl, toolUrl, then name.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REQUIRED_FIELDS = [
    "name",
    "category",
    "priority",
    "summary",
    "drprepper",
    "aluma",
    "next",
    "toolUrl",
    "postUrl",
]
DEFAULTS = {
    "priority": "Watch",
    "aluma": "No direct fit identified yet.",
    "next": "Review and decide whether this belongs in an active workflow.",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def key_for(entry: dict) -> str:
    for field in ("postUrl", "toolUrl", "name"):
        value = str(entry.get(field, "")).strip().lower()
        if value:
            return value
    return ""


def normalize(entry: dict) -> dict:
    item = dict(DEFAULTS)
    item.update({k: v for k, v in entry.items() if v not in (None, "")})
    now = datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds")
    item.setdefault("firstSeen", now)
    item["lastReviewed"] = now
    missing = [field for field in REQUIRED_FIELDS if not item.get(field)]
    if missing:
        raise SystemExit(f"Candidate {entry.get('name', '<unnamed>')} missing fields: {', '.join(missing)}")
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge candidate tool entries into data/tools.json")
    parser.add_argument("candidates", help="Path to JSON array of candidate entries")
    args = parser.parse_args()

    root = repo_root()
    data_path = root / "data" / "tools.json"
    current = json.loads(data_path.read_text()) if data_path.exists() else []
    candidates = json.loads(Path(args.candidates).read_text())
    if not isinstance(candidates, list):
        raise SystemExit("Candidates file must contain a JSON array")

    by_key = {key_for(item): item for item in current if key_for(item)}
    added = 0
    updated = 0
    for raw in candidates:
        item = normalize(raw)
        key = key_for(item)
        if key in by_key:
            existing = by_key[key]
            changed = False
            for field, value in item.items():
                if field == "firstSeen":
                    continue
                if value and existing.get(field) != value:
                    existing[field] = value
                    changed = True
            if changed:
                updated += 1
        else:
            current.append(item)
            by_key[key] = item
            added += 1

    current.sort(key=lambda t: (str(t.get("category", "")), str(t.get("name", ""))))
    data_path.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n")
    print(f"Merged candidates: {added} added, {updated} updated, {len(current)} total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
