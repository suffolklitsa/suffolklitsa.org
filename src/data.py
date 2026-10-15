"""Read the harvested content files. Side-effect free, cached per process."""
from __future__ import annotations

import functools
import json
import os

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


def courses():
    return load("courses")["items"]


def course_map():
    return {c["title"]: c for c in load("crosswalk")["courses"]}


def cohorts():
    return load("sections")["cohorts"]


def concentrations():
    return load("concentrations")["items"]


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
