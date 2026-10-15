#!/usr/bin/env python3
"""Re-harvest everything and report what changed.

Run this once a term, or whenever the catalog turns over. It re-fetches from
source, rebuilds the derived files, and prints a diff against what was there
before, so a human review is a few minutes of reading rather than an audit.

    python3 harvest/refresh.py            # re-fetch and diff
    python3 harvest/refresh.py --cached   # rebuild derived files only
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(os.path.dirname(HERE), "content")
CACHE = os.path.join(os.path.dirname(HERE), "cache")

STEPS = [
    ("databases", "harvest_databases.py"),
    ("guides", "harvest_guides.py"),
    ("courses", "harvest_courses.py"),
    ("concentrations", "harvest_concentrations.py"),
    ("faculty", "harvest_faculty.py"),
    ("services", "build_services.py"),
    ("descriptions", "apply_descriptions.py"),
    ("crosswalk", "build_crosswalk.py"),
    ("reconcile", "reconcile.py"),
    ("linkcheck", "linkcheck.py"),
]

# (file, key path to the list, field that identifies a record)
WATCH = [
    ("databases.json", ("items",), "title"),
    ("courses.json", ("items",), "title"),
    ("concentrations.json", ("items",), "name"),
]


def snapshot():
    out = {}
    for fname, path, key in WATCH:
        p = os.path.join(CONTENT, fname)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        for step in path:
            d = d[step]
        out[fname] = {x[key] for x in d}
    return out


def main():
    cached = "--cached" in sys.argv
    if not cached and os.path.isdir(CACHE):
        shutil.rmtree(CACHE)
        print("cache cleared, re-fetching from source")

    before = snapshot()
    for label, script in STEPS:
        print("\n== %s" % label)
        r = subprocess.run([sys.executable, os.path.join(HERE, script)],
                           cwd=HERE, capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode:
            sys.stderr.write(r.stderr)
            print("!! %s failed; stopping" % script)
            return 1
    after = snapshot()

    print("\n" + "=" * 62)
    print("CHANGES")
    print("=" * 62)
    changed = False
    for fname in sorted(after):
        old, new = before.get(fname, set()), after[fname]
        added, gone = sorted(new - old), sorted(old - new)
        if not (added or gone):
            print("  %-24s no change (%d records)" % (fname, len(new)))
            continue
        changed = True
        print("  %-24s +%d  -%d" % (fname, len(added), len(gone)))
        for a in added[:20]:
            print("      + %s" % a)
        for g in gone[:20]:
            print("      - %s" % g)

    lc = os.path.join(CONTENT, "linkcheck.json")
    if os.path.exists(lc):
        d = json.load(open(lc, encoding="utf-8"))
        print("\n  links: %s" % ", ".join("%s %d" % (k, v) for k, v in sorted(d["tally"].items())))
        if d["broken"]:
            print("  BROKEN (%d):" % len(d["broken"]))
            for b in d["broken"][:20]:
                print("      %s" % b[:110])

    print("\n  Descriptions in harvest/descriptions.py are hand-written and are NOT")
    print("  regenerated. Any database in the + list above needs a line adding there.")
    if changed:
        print("  Review the diff, then rebuild the site and commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
