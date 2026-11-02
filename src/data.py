"""Read the harvested content files. Side-effect free, cached per process."""
from __future__ import annotations

import copy
import functools
import json
import os
import re

CONTENT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content")


@functools.lru_cache(maxsize=None)
def load(name: str):
    with open(os.path.join(CONTENT, name + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def databases():
    return load("databases")["items"]


def studyaids():
    return {s["subject"]: s for s in load("studyaids")["subjects"]}


def treatises():
    return {s["subject"]: s for s in load("treatises")["subjects"]}


def subjects():
    return load("crosswalk")["subjects"]


def subject(slug):
    for s in subjects():
        if s["slug"] == slug:
            return s
    return None


def course_announcements():
    return load("course_announcements")["items"]


def _course_key(title):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", title.lower().replace("&", " and ")).split())


def courses():
    catalog = list(load("courses")["items"])
    known = {(_course_key(c["base_title"]), c["term"]) for c in catalog}
    for c in course_announcements():
        key = (_course_key(c["base_title"]), c["term"])
        if key not in known:
            catalog.append(c)
            known.add(key)
    return catalog


def course_map():
    return {c["title"]: c for c in load("crosswalk")["courses"]}


def cohorts():
    return load("sections")["cohorts"]


def concentrations():
    concentrations = copy.deepcopy(load("concentrations")["items"])
    for concentration in concentrations:
        if concentration["key"] != "legal-innovation-technology":
            continue
        existing = {_course_key(c["title"]): c for c in concentration["courses"]}
        for announcement in course_announcements():
            key = _course_key(announcement["base_title"])
            course = existing.get(key)
            if course is None:
                course = {"title": announcement["base_title"],
                          "credits": announcement["credits"],
                          "group": "Elective Course Requirements", "course_id": None,
                          "offered": [], "instructors": []}
                concentration["courses"].append(course)
                existing[key] = course
            course["offered"] = sorted(set(course.get("offered", [])) | {"spring"})
            course["instructors"] = course.get("instructors") or announcement["instructors"]
            course["announcement"] = announcement
        aliases = load("concentration_course_aliases")["items"]
        for course in concentration["courses"]:
            alias = aliases.get(course["title"])
            if alias:
                hits = [c for c in courses() if _course_key(c["base_title"]) ==
                        _course_key(alias["catalog_title"])]
                if hits:
                    course["offered"] = sorted({"fall" if "Fall" in h["term"] else "spring" for h in hits})
                    course["instructors"] = sorted({i for h in hits for i in h["instructors"]})
                    course["catalog_alias"] = alias
        records = concentration["courses"]
        concentration["reconciliation"] = {
            "listed": len(records),
            "offered_2026_27": sum(bool(c["offered"]) for c in records),
            "not_offered_2026_27": sum(not c["offered"] for c in records),
            "fall_only": [c["title"] for c in records if c["offered"] == ["fall"]],
            "spring_only": [c["title"] for c in records if c["offered"] == ["spring"]],
            "missing": [c["title"] for c in records if not c["offered"]],
        }
    return concentrations


def universal():
    return load("concentrations")["universal"]


def services():
    return load("services")


def faculty():
    return load("faculty")["items"]


def verified(name: str) -> str:
    return load(name).get("verified", "")


def esc(s) -> str:
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))
