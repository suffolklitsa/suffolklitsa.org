"""This week in AI, privacy, cyber and legal tech: headlines for /watch/, from outlets' own feeds.

Each item is the outlet's own headline, date and one-line description from its RSS feed, linked
to the story. Nothing is summarized or rewritten by a model, so nothing on the page can say more
than the source did. Broad outlets pass only items that match our topics; outlets that cover
nothing else (LawSites, Artificial Lawyer, EFF, the Future of Privacy Forum) pass everything.

Keeps the last 10 days, at most four items per outlet, newest first, 18 in all. A feed that fails
keeps its previous items. Writes content/news.json; refresh_events.sh runs this twice a day.
"""
from __future__ import annotations

import collections
import datetime as dt
import email.utils
import html
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("NEWS_OUT") or os.path.join(os.path.dirname(HERE), "content", "news.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; LITSA-news/1.0; suffolklitsa.org)"}

# name: (feed, filter?)  filter=False means every item is on topic
FEEDS = {
    "LawSites": ("https://www.lawnext.com/feed", False),
    "Artificial Lawyer": ("https://www.artificiallawyer.com/feed/", False),
    "EFF": ("https://www.eff.org/rss/updates.xml", False),
    "Future of Privacy Forum": ("https://fpf.org/feed/", False),
    "The Record": ("https://therecord.media/feed", False),
    "Krebs on Security": ("https://krebsonsecurity.com/feed/", False),
    "CyberScoop": ("https://cyberscoop.com/feed/", False),
    "BleepingComputer": ("https://www.bleepingcomputer.com/feed/", True),
    "Dark Reading": ("https://www.darkreading.com/rss.xml", True),
    "Lawfare": ("https://www.lawfaremedia.org/feeds/articles", True),
    "FTC": ("https://www.ftc.gov/feeds/press-release.xml", True),
    "The Verge": ("https://www.theverge.com/rss/policy/index.xml", True),
    "TechCrunch": ("https://techcrunch.com/category/artificial-intelligence/feed/", True),
    "Above the Law": ("https://abovethelaw.com/feed/", True),
}
TAGS = {
    "AI": r"\bAI\b|artificial intelligence|machine learning|chatbot|LLM|generative|OpenAI|Anthropic|deepfake",
    "Privacy": r"privacy|personal data|data broker|biometric|surveillance|GDPR|CCPA|tracking|consent",
    "Cyber": r"breach|hack|ransomware|cyber|malware|phishing|vulnerabilit|exploit|stolen data|leak",
    "IP": r"copyright|patent|trademark|fair use|trade secret",
    "Legal tech": r"legal tech|law firm|lawyer|attorney|court|e-?discovery|legaltech|practice management",
}
# Broad outlets must hit one of these (law-firm gossip on Above the Law does not count), plus LAW.
TECH = ("AI", "Privacy", "Cyber", "IP")
LEGAL_TECH_STRICT = r"legal tech|legaltech|e-?discovery|practice management|legal AI|law firm software|CLM\b"
SKIP = r"^\[(virtual event|webinar|sponsored)|morning docket|see also$|webinar|sponsored|^The Innovators|on Tour\b"
# For filtered outlets, an item must touch law or policy as well as the technology.
LAW = (r"\b(laws?|legal|courts?|judges?|lawsuits?|sues?|sued|suing|regulat\w*|FTC|SEC|rules?|bills?|act|policy|"
       r"enforcement|settle\w*|fined|fines?|attorneys?|lawyers?|legislat\w*|bans?|banned|charged|indict\w*|"
       r"pleads?|guilty|sentenc\w*|breach\w*|ransomware|hack\w*|privacy|antitrust)\b")
DEFAULT_TAG = {"LawSites": "Legal tech", "Artificial Lawyer": "Legal tech", "EFF": "Privacy",
               "Future of Privacy Forum": "Privacy", "The Record": "Cyber", "Krebs on Security": "Cyber",
               "CyberScoop": "Cyber"}


def clean(text: str, limit: int) -> str:
    text = re.sub(r"<!\[CDATA\[|\]\]>", "", text or "")
    text = html.unescape(re.sub(r"<[^>]+>", " ", html.unescape(text)))  # some feeds escape their HTML
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s*\[(…|\.\.\.|&hellip;)\]\s*$", "…", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = re.sub(r"\s*(The post .* appeared first on .*|Continue reading.*|Read more.*)$", "", text)
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return text


def parse_date(raw: str) -> dt.datetime | None:
    raw = (raw or "").strip()
    try:
        return email.utils.parsedate_to_datetime(raw).astimezone(dt.timezone.utc)
    except Exception:
        pass
    try:
        return dt.datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except Exception:
        return None


def items(xml: str):
    for block in re.findall(r"<item[\s>].*?</item>|<entry[\s>].*?</entry>", xml, re.S):
        title = re.search(r"<title[^>]*>(.*?)</title>", block, re.S)
        link = (re.search(r"<link[^>]*href=\"([^\"]+)\"", block)
                or re.search(r"<link[^>]*>(.*?)</link>", block, re.S))
        date = re.search(r"<(pubDate|published|updated|dc:date)[^>]*>(.*?)</\1>", block, re.S)
        desc = re.search(r"<(description|summary|content:encoded|content)[^>]*>(.*?)</\1>", block, re.S)
        yield (clean(title.group(1), 180) if title else "", clean(link.group(1), 400) if link else "",
               parse_date(date.group(2)) if date else None, clean(desc.group(2), 220) if desc else "")


def harvest(name: str, url: str, filtered: bool, since: dt.datetime, now: dt.datetime) -> list[dict]:
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
    out = []
    for title, link, when, desc in items(raw.decode("utf-8", "ignore")):
        if not (title and link.startswith("http") and when and when >= since):
            continue
        if when > now + dt.timedelta(days=1) or re.search(SKIP, title, re.I):
            continue  # event listings dated in the future, promos, daily link roundups
        blob = f"{title} {desc}"
        tags = [t for t, rx in TAGS.items() if re.search(rx, blob, re.I)]
        on_topic = any(t in TECH for t in tags) or re.search(LEGAL_TECH_STRICT, blob, re.I)
        if filtered and not (on_topic and re.search(LAW, blob, re.I)):
            continue
        if re.match(r"(special )?thanks to", desc, re.I):
            desc = ""  # an acknowledgments line is not a description
        tag = tags[0] if tags else DEFAULT_TAG.get(name, "Legal tech")
        out.append(dict(title=title, url=link, source=name, date=when.date().isoformat(),
                        ts=when.isoformat(), summary=desc, tag=tag))
    return sorted(out, key=lambda x: x["ts"], reverse=True)[:4]


COMMON = {"OpenAI", "Google", "Meta", "Microsoft", "Apple", "Amazon", "Congress", "Senate", "House", "Court",
          "Supreme", "Federal", "State", "North", "Korea", "China", "Russia", "Chinese", "Russian", "Trump",
          "European", "Union", "United", "States", "Commission", "Department", "Justice", "Anthropic", "Law"}


def story_names(title: str) -> set[str]:
    """Distinctive names in a headline (Bitget, Suno), used to spot one story told by two outlets."""
    words = re.findall(r"[A-Za-z][\w'’.-]*", title)[1:]
    return {w.strip(".'’") for w in words if w[0].isupper() and len(w) >= 4 and w.strip(".'’") not in COMMON}


def main() -> int:
    now = dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(days=10)
    prior = {}
    if os.path.exists(OUT):
        for it in json.load(open(OUT)).get("items", []):
            prior.setdefault(it["source"], []).append(it)
    got, status, failed = [], {}, 0
    for name, (url, filtered) in FEEDS.items():
        try:
            rows = harvest(name, url, filtered, since, now)
            status[name] = f"ok {len(rows)}"
        except Exception as ex:  # noqa: BLE001 (one outlet down is routine)
            rows = [r for r in prior.get(name, []) if r["ts"] >= since.isoformat()]
            status[name] = f"FAILED ({ex.__class__.__name__}); kept {len(rows)}"
            failed = 1
        got += rows
    # Every outlet gets its two newest in before anyone gets a third, so one busy day at one
    # outlet cannot fill the band; the page then shows them newest first.
    rank = collections.Counter()
    for it in sorted(got, key=lambda x: x["ts"], reverse=True):
        it["_rank"] = rank[it["source"]]
        rank[it["source"]] += 1
    seen, stories, keep = set(), [], []
    for it in sorted(sorted(got, key=lambda x: x["ts"], reverse=True), key=lambda x: min(x["_rank"], 2)):
        key = re.sub(r"[^a-z0-9]", "", it["title"].lower())[:50]
        names = story_names(it["title"])
        if key in seen or any(it["date"] == d and names & n for d, n in stories):
            continue  # same story from two outlets
        seen.add(key)
        stories.append((it["date"], names))
        keep.append({k: v for k, v in it.items() if k != "_rank"})
        if len(keep) == 18:
            break
    keep.sort(key=lambda x: x["ts"], reverse=True)
    json.dump({"fetched": dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"), "status": status,
               "items": keep}, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(status), len(keep), "items")
    return failed


if __name__ == "__main__":
    sys.exit(main())
