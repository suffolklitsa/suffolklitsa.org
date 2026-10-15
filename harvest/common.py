"""Shared fetch/parse helpers for the LITSA resource harvest.

Every harvested record carries its source URL and the date it was verified, so a
stale page looks stale instead of confidently wrong.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), "cache")
CONTENT = os.path.join(os.path.dirname(HERE), "content")
UA = {"User-Agent": "Mozilla/5.0 (compatible; LITSA-resource-harvest/1.0)"}

# Boxes that are page furniture on every LibGuides page, not content.
FURNITURE = {"Legend", "Contact the Research Desk", "Related Guides",
             "Moakley Law Library", "How to Use This Guide"}
# Tag clouds, print links, and intra-guide pagination masquerade as resources.
NOISE = re.compile(r"srch\.php|javascript:|mailto:|libapps|libanswers\.com/widget")


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def text(html: str) -> str:
    """Strip tags and collapse whitespace, resolving the entities LibGuides emits."""
    t = re.sub(r"<[^>]+>", " ", html)
    for a, b in (("&amp;", "&"), ("&nbsp;", " "), ("&rsquo;", "’"),
                 ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'")):
        t = t.replace(a, b)
    return " ".join(t.split())


def fetch(url: str, key: str, ttl_days: int = 7) -> str:
    """Fetch with an on-disk cache so reruns are cheap and the harvest is idempotent."""
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, key + ".html")
    if os.path.exists(p) and os.path.getsize(p) > 4000:
        if (time.time() - os.path.getmtime(p)) < ttl_days * 86400:
            return open(p, encoding="utf-8").read()
    h = urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=40).read().decode("utf-8", "ignore")
    open(p, "w", encoding="utf-8").write(h)
    time.sleep(0.35)
    return h


def boxes(html: str):
    """Yield (box_title, [(link_text, url), ...]) for each real content box."""
    for m in re.finditer(
            r"<h2[^>]*s-lib-box-title[^>]*>(.*?)</h2>(.*?)(?=<h2[^>]*s-lib-box-title|\Z)",
            html, re.S):
        title = text(m.group(1))
        if title in FURNITURE:
            continue
        links = []
        for u, a in re.findall(r"<a[^>]+href=\"([^\"]+)\"[^>]*>(.*?)</a>", m.group(2), re.S):
            label = text(a)
            u = u.replace("&amp;", "&")
            if not label or u.startswith("#") or NOISE.search(u):
                continue
            if label.startswith(("<<", "Next:", "Print")) or label in ("Report a problem.",):
                continue
            # LibGuides appends this to every external link.
            label = label.replace("This link opens in a new window", "").strip()
            links.append((label, u))
        if links:
            yield title, links


def access_of(url: str) -> str:
    """Classify how much friction stands between a student and the resource."""
    u = url.lower()
    if "ezproxysuf" in u:
        return "proxy"
    if "library.law.suffolk.edu" in u:
        return "print"
    if "westlaw.com" in u or "lexis.com" in u or "westacademic" in u:
        return "platform"
    if "cali.org" in u:
        return "code"
    return "open"


def write(name: str, payload) -> None:
    os.makedirs(CONTENT, exist_ok=True)
    p = os.path.join(CONTENT, name)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False, sort_keys=False)
        fh.write("\n")
    n = len(payload.get("items", payload)) if isinstance(payload, dict) else len(payload)
    print("  wrote %-26s %5d records  %7d bytes" % (name, n, os.path.getsize(p)))
