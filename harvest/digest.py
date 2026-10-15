#!/usr/bin/env python3
"""What changed since the last newsletter.

The reason the watch page is worth keeping is that it turns the newsletter from
a blank page into an edit. Run this with the date of the last issue and it
prints what has landed since, grouped the way an issue would want it.

    python3 harvest/digest.py 2026-08-30
    python3 harvest/digest.py 2026-08-30 --json

Nothing here is automatic prose. It hands over the raw material with links and
dates intact, and a person writes the issue.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(os.path.dirname(HERE), "content")


def load(name):
    try:
        with open(os.path.join(CONTENT, f"{name}.json")) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("since", nargs="?", help="YYYY-MM-DD, default 30 days ago")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    since = a.since or (date.today() - timedelta(days=30)).isoformat()

    lit = load("litigation")
    press = load("press")

    # first_seen, not the filing date: an opinion from March that surfaced last
    # week is news to our readers even though the court is done with it.
    cases = sorted((c for c in lit.get("items", [])
                    if (c.get("first_seen") or "") >= since),
                   key=lambda c: c.get("date") or "", reverse=True)
    lanes = {l["id"]: l["label"] for l in lit.get("lanes", [])}
    coverage = sorted((p for p in press.get("items", [])
                       if (p.get("date") or "") >= since),
                      key=lambda p: p["date"], reverse=True)

    if a.json:
        print(json.dumps({"since": since, "cases": cases,
                          "coverage": coverage}, indent=1))
        return 0

    print(f"Digest since {since}\n" + "=" * 52)
    if not cases and not coverage:
        print("\nNothing new. Either it was a quiet month or the refresh is "
              "not running; check content/litigation.json last_success.")
        return 0

    if coverage:
        print(f"\nCOVERAGE ({len(coverage)})")
        for p in coverage:
            print(f"\n  {p['date']}  {p['outlet']}")
            print(f"  {p['title']}")
            print(f"  {p['note']}")
            print(f"  {p['url']}")

    if cases:
        print(f"\nCOURTS ({len(cases)} new to us)")
        for lane_id, label in lanes.items():
            rows = [c for c in cases if c.get("lane") == lane_id]
            if not rows:
                continue
            print(f"\n  -- {label}")
            for c in rows:
                print(f"\n  {c['date']}  {c['case']}")
                print(f"  {c['court']}")
                print(f"  {c['why']}")
                print(f"  {c['url']}")

    print(f"\n{'=' * 52}\nCourt list last refreshed: "
          f"{lit.get('last_success', 'unknown')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
