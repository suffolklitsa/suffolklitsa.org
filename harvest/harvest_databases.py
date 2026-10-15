"""Harvest the Moakley A-Z database list with its facets.

The list page is JS-rendered, so we hit the underlying dblist feed directly.
The feed does not tag records inline; subject/type/vendor membership has to be
recovered by re-querying once per facet and intersecting on content id.
"""
from __future__ import annotations

import datetime
import json
import re
import time
import urllib.request

from common import CACHE, UA, text, write

TODAY = datetime.date.today().isoformat()
FEED = "https://lawguides.suffolk.edu/process/az/dblist?site_id=6982"
AZ_PAGE = "https://lawguides.suffolk.edu/az/databases"

# The library's own subject labels, remapped. Theirs mixes practice area with
# research task with format with audience, and misspells Environmental.
RELABEL = {
    "Enivronmental Law": "Environmental Law",
    "Secondary Sources: Exam Prep": "Exam Prep",
    "Secondary Sources: Study Aids": "Study Aids",
    "Secondary Sources: Bar Exam": "Bar Exam",
    "Secondary Sources: News": "News",
    "Secondary Sources: Films and Videos": "Film & Video",
    "Secondary Sources": "Secondary Sources",
    "Social Science: Psychology": "Psychology",
    "International Law: Human Rights": "Human Rights",
    "Multidisciplinary Resources": "Multidisciplinary",
    "Land Law and Zoning": "Land Use & Zoning",
    "Landlord / Tenant": "Landlord & Tenant",
    "Tax and Accounting": "Tax & Accounting",
    "Trade and Arbitration": "Trade & Arbitration",
}
# Audience-scoped, not useful to students browsing.
DROP_SUBJECT = {"Faculty Resources"}


def feed(params: str = ""):
    u = FEED + params
    return json.load(urllib.request.urlopen(
        urllib.request.Request(u, headers=UA), timeout=40))["data"]


def options(html: str):
    """(id, label, count) for each facet option, skipping the 'All' entry."""
    out = []
    for v, label in re.findall(r"<option[^>]*value=\"(\d+)\"[^>]*>(.*?)</option>", html, re.S):
        lab = text(label)
        m = re.search(r"\((\d+)\)\s*$", lab)
        n = int(m.group(1)) if m else 0
        out.append((v, re.sub(r"\s*\(\d+\)\s*$", "", lab).strip(), n))
    return out


def parse_results(html: str):
    """Pull id, title, url, description and access badges from the feed markup."""
    recs = []
    for blk in re.split(r"<div class=\"s-lg-az-result\s", html)[1:]:
        m = re.search(r"_st_content_id:\s*&#039;(\d+)&#039;", blk)
        a = re.search(r"<div class=\"s-lg-az-result-title\"[^>]*>\s*<a href=\"([^\"]+)\"[^>]*>(.*?)</a>",
                      blk, re.S)
        if not (m and a):
            continue
        url = a.group(1).replace("&amp;", "&")
        # The library double-prefixes the proxy on dozens of entries.
        url = re.sub(r"^(https://ezproxysuf\.flo\.org/login\?url=)+", r"\1", url)
        title = text(a.group(2))
        d = re.search(r"s-lg-az-result-description\"><p>(.*?)</p>", blk, re.S)
        badges = [text(x) for x in re.findall(r'alt="([^"]+)"\s+class="s-lg-icon"', blk)]
        recs.append({"id": m.group(1), "title": title, "url": url,
                     "vendor_description": text(d.group(1)) if d else "",
                     "badges": badges})
    return recs


def main():
    base = feed()
    recs = parse_results(base["html"])
    print("  databases: %d (feed count %s)" % (len(recs), base["count"]))
    by_id = {r["id"]: r for r in recs}
    for r in recs:
        r["subjects"], r["types"], r["vendors"] = [], [], []

    facets = [("subjects_html", "subject_id", "subjects"),
              ("az_types_html", "type_id", "types"),
              ("az_vendors_html", "vendor_id", "vendors")]
    for html_key, param, field in facets:
        opts = options(base[html_key])
        print("  %s: %d options" % (field, len(opts)))
        for fid, label, n in opts:
            if label in DROP_SUBJECT:
                continue
            label = RELABEL.get(label, label)
            try:
                got = parse_results(feed("&%s=%s" % (param, fid))["html"])
            except Exception as exc:
                print("    !! %s %s: %s" % (field, label, exc))
                continue
            for g in got:
                if g["id"] in by_id:
                    by_id[g["id"]][field].append(label)
            time.sleep(0.3)

    for r in recs:
        b = " ".join(r["badges"]).lower()
        if "open access" in b:
            r["access"] = "open"
        elif "individual username" in b:
            r["access"] = "account"
        elif "proxy" in b:
            r["access"] = "proxy"
        elif "westlaw" in b or "lexis" in b:
            r["access"] = "platform"
        elif "print" in b:
            r["access"] = "print"
        else:
            r["access"] = "unknown"
        # A proxy resource that also needs you to make your own account is the
        # real drop-off point, so it gets its own state rather than folding in.
        if "individual username" in b and "proxy" in b:
            r["access"] = "account"
        r["subjects"] = sorted(set(r["subjects"]))
        r["types"] = sorted(set(r["types"]))
        r["vendors"] = sorted(set(r["vendors"]))
        r["description"] = ""  # filled by hand in Phase 2
        r["verified"] = TODAY

    write("databases.json", {"source": AZ_PAGE, "verified": TODAY,
                             "count": len(recs), "items": recs})


if __name__ == "__main__":
    main()
