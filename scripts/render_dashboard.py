#!/usr/bin/env python3
"""Render the static DR Prepper AI Tools Ops Dashboard.

Source of truth: data/tools.json
Output: index.html
"""
from __future__ import annotations

import argparse
import json
import re
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
ALLOWED_PRIORITIES = {"High", "Medium", "Watch", "Lead"}
URL_RE = re.compile(r"^https?://", re.I)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_tools(path: Path) -> list[dict]:
    tools = json.loads(path.read_text())
    if not isinstance(tools, list):
        raise SystemExit(f"{path} must contain a JSON array")
    return tools


def validate_tools(tools: list[dict]) -> None:
    seen_keys: set[str] = set()
    errors: list[str] = []

    for idx, tool in enumerate(tools, start=1):
        label = tool.get("name") or f"entry #{idx}"
        for field in REQUIRED_FIELDS:
            if field not in tool or tool[field] in (None, ""):
                errors.append(f"{label}: missing required field {field!r}")
        priority = tool.get("priority")
        if priority and priority not in ALLOWED_PRIORITIES:
            errors.append(f"{label}: priority must be one of {sorted(ALLOWED_PRIORITIES)}, got {priority!r}")
        for field in ("toolUrl", "postUrl"):
            url = tool.get(field)
            if url and not URL_RE.match(str(url)):
                errors.append(f"{label}: {field} must start with http(s), got {url!r}")

        key = (tool.get("postUrl") or tool.get("toolUrl") or tool.get("name") or "").strip().lower()
        if key in seen_keys:
            errors.append(f"{label}: duplicate key/source URL {key!r}")
        seen_keys.add(key)

    if errors:
        raise SystemExit("Dashboard data validation failed:\n- " + "\n- ".join(errors))


def updated_label(now: datetime | None = None) -> str:
    now = now or datetime.now(ZoneInfo("America/Los_Angeles"))
    return now.strftime("%b %-d, %Y · %-I:%M %p %Z")


def render(tools: list[dict], template_path: Path, output_path: Path) -> None:
    validate_tools(tools)
    priority_order = {"High": 0, "Lead": 1, "Medium": 2, "Watch": 3}
    tools_sorted = sorted(
        tools,
        key=lambda t: (
            priority_order.get(str(t.get("priority", "")), 9),
            str(t.get("category", "")),
            str(t.get("name", "")),
        ),
    )
    categories = {t["category"] for t in tools_sorted}
    high_count = sum(1 for t in tools_sorted if t.get("priority") == "High")
    template = template_path.read_text()
    html = (
        template
        .replace("__TOOLS_JSON__", json.dumps(tools_sorted, ensure_ascii=False, indent=6))
        .replace("__ENTRY_COUNT__", str(len(tools_sorted)))
        .replace("__CATEGORY_COUNT__", str(len(categories)))
        .replace("__HIGH_COUNT__", str(high_count))
        .replace("__UPDATED_LABEL__", updated_label())
    )
    output_path.write_text(html)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the dashboard from data/tools.json")
    parser.add_argument("--check", action="store_true", help="validate and compare rendered output without writing")
    args = parser.parse_args()

    root = repo_root()
    data_path = root / "data" / "tools.json"
    template_path = root / "templates" / "index.template.html"
    output_path = root / "index.html"
    tools = load_tools(data_path)

    if args.check:
        validate_tools(tools)
        tmp_path = root / ".index.rendered.tmp.html"
        render(tools, template_path, tmp_path)
        current = output_path.read_text() if output_path.exists() else ""
        rendered = tmp_path.read_text()
        tmp_path.unlink(missing_ok=True)
        if current != rendered:
            raise SystemExit("index.html is not up to date; run scripts/render_dashboard.py")
        print(f"OK: {len(tools)} entries validated and index.html is current")
        return 0

    render(tools, template_path, output_path)
    print(f"Rendered {output_path} from {data_path} ({len(tools)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
