#!/usr/bin/env python3
"""Litigation monitor: courts deciding things about technology.

Runs unattended on a schedule. Nobody reads dockets by hand.

    python3 harvest/harvest_litigation.py            # full run
    python3 harvest/harvest_litigation.py --dry      # fetch + classify, write nothing
    python3 harvest/harvest_litigation.py --no-llm   # fetch only, park as pending

## How it stays alive

CourtListener's search API needs no key, so the fetch half cannot break on a
credential rotation. Only classification needs OPENAI_API_KEY, and if that is
missing or failing the candidates land in `pending` rather than being dropped,
so a key problem costs us a week of curation and never loses a case.

Every record carries `first_seen`, and the file carries `last_run`,
`last_success` and a `health` block. The page prints the last-success date. If
the cron dies, the date on the public page goes stale on its own, which is the
alarm. There is no separate monitoring to forget about.

Growth is bounded: `PUBLISH_PER_LANE` most recent per lane are published, the
rest stay in the file as archive. The page never grows without limit and the
JSON never needs pruning by hand.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(os.path.dirname(HERE), "content")
OUT = os.path.join(CONTENT, "litigation.json")

CL = "https://www.courtlistener.com/api/rest/v4/search/"
UA = "LITSA-litigation-monitor/1.0 (suffolklitsa.org; student org, low volume)"

# Recency window. Anything older is already in the file from an earlier run.
LOOKBACK_DAYS = 400
PUBLISH_PER_LANE = 8
MAX_PER_QUERY = 30

# The lanes are the editorial judgment. Each is a slice of law-meets-technology
# a Suffolk student would plausibly care about, and each maps to one query.
LANES = [
    ("practice", "AI in legal practice",
     '"artificial intelligence" OR "generative AI" OR ChatGPT '
     'AND (sanction OR "Rule 11" OR fabricated OR nonexistent)'),
    ("copyright", "Training data and copyright",
     '("generative AI" OR "large language model" OR "machine learning") '
     'AND (copyright OR "fair use" OR infringement)'),
    ("evidence", "AI and evidence",
     '("artificial intelligence" OR deepfake OR "machine generated") '
     'AND (authentication OR admissibility OR "expert testimony" OR Daubert)'),
    ("automated", "Automated decisions",
     '("algorithmic" OR "automated decision" OR "risk assessment tool") '
     'AND (due process OR discrimination OR transparency)'),
    ("privacy", "Privacy and biometrics",
     '("biometric" OR "facial recognition" OR "Illinois Biometric Information") '
     'AND (privacy OR consent OR class)'),
    ("employment", "Hiring and employment screening",
     '("artificial intelligence" OR algorithm) AND (hiring OR "employment '
     'discrimination" OR applicant)'),
]

LANE_IDS = [l[0] for l in LANES]

CLASSIFY_SYSTEM = (
    "You screen court opinions for a law school student organization that "
    "follows legal technology. You are the only filter between a keyword "
    "search and a public page, so be strict.\n\n"
    "Keep an opinion only if the court actually engages with technology as a "
    "legal question: how AI evidence is treated, whether an AI-assisted filing "
    "breached a duty, what copyright does to training data, how an automated "
    "system interacts with due process, and so on.\n\n"
    "Reject anything where the technology word is incidental: a party happens "
    "to be a software company, a witness mentions a phone, a brief cites a "
    "case whose name contains 'AI'. Reject when the excerpt is too thin to "
    "tell what the court did. Rejecting is cheap; a wrong entry on a public "
    "page is not.\n\n"
    "Assign the lane that matches what the opinion is ABOUT, not the words it "
    "contains. A sanctions ruling over fabricated citations is 'practice' even "
    "if it also mentions hiring or evidence. Lanes:\n"
    + "\n".join(f"  {i} - {l}" for i, l, _ in LANES) + "\n\n"
    "Reply with a JSON array, one object per input, same order, each with: "
    '{"i": <index>, "keep": true|false, "lane": "<lane id>", "why": "<one '
    'plain sentence naming what the court did, no adjectives>"}\n\n'
    "The why must name the legal question the court reached, not that "
    "technology appeared. \"The court noted the use of AI\" and \"discussed it "
    "in the context of the case\" are both failures; say what the court "
    "decided, sanctioned, admitted, or refused. If the excerpt does not let "
    "you write that sentence, set keep to false."
)


def log(msg):
    print(f"[{datetime.now(timezone.utc):%H:%M:%S}] {msg}", flush=True)


def get_json(url, tries=3):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={"Accept": "application/json", "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except Exception as e:
            if attempt == tries - 1:
                raise
            time.sleep(3 * (attempt + 1))
    return None


# A reason that says technology merely appeared tells a reader nothing, and on
# a public page it reads as padding. Cheaper to drop than to explain.
VACUOUS = re.compile(
    r"^the court (noted|mentioned|acknowledged|observed)\b"
    r"|noted the (use|misuse|presence|existence)|in the context of the case"
    r"|mentions? (the )?(use of )?(artificial intelligence|AI)"
    r"|involves? technology|relates? to technology", re.I)


def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"</?mark>", "", s or "")).strip()


def excerpt(row, limit=700):
    """Match-centred text. highlight=on wraps hits in <mark>, so we cut around
    them; that is where the technology discussion is, not the opinion's head."""
    parts = []
    for op in (row.get("opinions") or [])[:2]:
        sn = op.get("snippet") or ""
        for m in re.finditer(r"<mark>", sn):
            lo = max(0, m.start() - 220)
            parts.append(clean(sn[lo:m.start() + 320]))
            if len(parts) >= 3:
                break
    if not parts:  # no highlight came back; fall back to the opening
        for op in (row.get("opinions") or [])[:1]:
            parts.append(clean(op.get("snippet") or "")[:400])
    out = " … ".join(p for p in parts if p)
    return out[:limit]


def fetch_lane(lane_id, query, cutoff):
    url = CL + "?" + urllib.parse.urlencode({
        "q": query, "type": "o", "order_by": "dateFiled desc",
        "highlight": "on", "filed_after": cutoff})
    d = get_json(url)
    rows = (d or {}).get("results", [])[:MAX_PER_QUERY]
    out = []
    for r in rows:
        cid = r.get("cluster_id")
        if not cid:
            continue
        out.append({
            "id": str(cid),
            "lane": lane_id,
            "case": clean(r.get("caseName")),
            "court": clean(r.get("court")),
            "court_id": r.get("court_id"),
            "date": r.get("dateFiled"),
            "docket": clean(r.get("docketNumber")),
            "status": r.get("status"),
            "url": "https://www.courtlistener.com" + (r.get("absolute_url") or ""),
            "excerpt": excerpt(r),
        })
    return out, (d or {}).get("count", 0)


def openai_key():
    k = os.environ.get("OPENAI_API_KEY")
    if k:
        return k
    # the cron does not need its own copy of the key
    for path in ("/srv/dev/docketmath/.env", os.path.expanduser("~/.env")):
        try:
            for line in open(path):
                if line.startswith("OPENAI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
        except OSError:
            pass
    return None


def classify(batch, key, model="gpt-4o-mini"):
    """Returns {index: (keep, why)}. Raises so the caller can park as pending."""
    lines = []
    for i, c in enumerate(batch):
        lines.append(f"[{i}] {c['case']} ({c['court']}, {c['date']})\n"
                     f"    excerpt: {c['excerpt']}")
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": CLASSIFY_SYSTEM},
            {"role": "user", "content": "\n\n".join(lines)},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.load(r)
    txt = d["choices"][0]["message"]["content"]
    parsed = json.loads(txt)
    rows = parsed if isinstance(parsed, list) else next(
        (v for v in parsed.values() if isinstance(v, list)), [])
    out = {}
    for row in rows:
        try:
            i = int(row["i"])
        except (KeyError, TypeError, ValueError):
            continue
        why = clean(row.get("why"))[:220]
        lane = row.get("lane") if row.get("lane") in LANE_IDS else None
        # a keep with no reason is not a keep; the page would show a bare case
        keep = (bool(row.get("keep")) and len(why) > 25 and lane is not None
                and not VACUOUS.search(why))
        out[i] = (keep, why, lane)
    return out


def load_existing():
    try:
        with open(OUT) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"items": [], "pending": [], "health": {}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--no-llm", action="store_true")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    cutoff = (now.timestamp() - LOOKBACK_DAYS * 86400)
    cutoff = datetime.fromtimestamp(cutoff, timezone.utc).strftime("%Y-%m-%d")

    prev = load_existing()
    known = {it["id"]: it for it in prev.get("items", [])}
    pending = {it["id"]: it for it in prev.get("pending", [])}
    judged = set(prev.get("judged", [])) | set(known)

    errors, fetched, counts = [], [], {}
    for lane_id, _label, query in LANES:
        try:
            rows, total = fetch_lane(lane_id, query, cutoff)
            counts[lane_id] = total
            fetched.extend(rows)
            log(f"{lane_id}: {len(rows)} candidates of {total} matching")
        except Exception as e:
            errors.append(f"{lane_id}: {e}")
            log(f"{lane_id}: FETCH FAILED {e}")
        time.sleep(1.5)

    # dedupe, keeping the first lane that claimed it
    fresh, seen = [], set()
    for r in fetched:
        if r["id"] in seen or r["id"] in judged:
            continue
        seen.add(r["id"])
        fresh.append(r)
    log(f"{len(fresh)} new candidates, {len(known)} already known")

    key = None if args.no_llm else openai_key()
    kept, parked = [], []
    if fresh and key:
        for i in range(0, len(fresh), 8):
            chunk = fresh[i:i + 8]
            try:
                verdicts = classify(chunk, key)
            except Exception as e:
                errors.append(f"classify: {e}")
                log(f"classify FAILED, parking {len(chunk)} as pending: {e}")
                parked.extend(chunk)
                continue
            for j, c in enumerate(chunk):
                keep, why, lane = verdicts.get(j, (False, "", None))
                judged.add(c["id"])  # remember the noes, not just the yeses
                if keep:
                    c["why"] = why
                    c["lane"] = lane  # subject, not whichever query matched
                    c["first_seen"] = now.strftime("%Y-%m-%d")
                    c.pop("excerpt", None)
                    kept.append(c)
            time.sleep(1)
        log(f"classifier kept {len(kept)} of {len(fresh)}")
    elif fresh:
        parked.extend(fresh)
        log(f"no key or --no-llm: parked {len(fresh)} as pending")

    items = list(known.values()) + kept
    items.sort(key=lambda x: (x.get("date") or ""), reverse=True)

    # bounded growth: publish the most recent per lane, keep the rest as archive
    published, per_lane = [], {}
    for it in items:
        n = per_lane.get(it["lane"], 0)
        if n < PUBLISH_PER_LANE:
            per_lane[it["lane"]] = n + 1
            published.append(it["id"])

    for p in parked:
        p["first_seen"] = now.strftime("%Y-%m-%d")
        pending[p["id"]] = p

    # Pending means "not yet judged". Once the screener has ruled either way,
    # it comes off the list.
    for cid in list(pending):
        if cid in judged:
            del pending[cid]

    degraded = bool(parked)
    ok = not errors and not degraded
    doc = {
        "lanes": [{"id": i, "label": l} for i, l, _ in LANES],
        "items": items,
        "published": published,
        "judged": sorted(judged),
        "pending": list(pending.values()),
        "last_run": now.strftime("%Y-%m-%d %H:%M UTC"),
        "last_success": (now.strftime("%Y-%m-%d %H:%M UTC") if ok
                         else prev.get("last_success")),
        "health": {
            "ok": ok,
            "degraded": degraded,
            "errors": errors + (
                ["classification unavailable; candidates parked as pending"]
                if degraded and not errors else []),
            "candidates_seen": len(fetched),
            "new_this_run": len(fresh),
            "kept_this_run": len(kept),
            "pending": len(pending),
            "total_items": len(items),
            "judged_ever": len(judged),
            "source_counts": counts,
        },
    }

    if args.dry:
        log("--dry: not writing")
        print(json.dumps(doc["health"], indent=2))
        return 0

    os.makedirs(CONTENT, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
    log(f"wrote {OUT}  items={len(items)} published={len(published)} "
        f"pending={len(pending)} ok={ok}"
        + ("  DEGRADED: nothing classified this run" if degraded else ""))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
