#!/usr/bin/env python3
"""Build LITSA project pages (the course planner and others) into the site's build/ folder.

    python3 harvest/build_projects.py --channel production --out build
    python3 harvest/build_projects.py --channel staging --out build

Projects are listed in projects.toml. For each one this clones or updates the repo under
cache/projects/<name>, checks out the right version, runs its build command, and copies its
output folder to build/<path>/.

- production uses the newest release tag (vX.Y.Z) on the project's main branch. A project
  with no release yet is skipped, so nothing unreleased reaches suffolklitsa.org.
- staging uses the project's staging branch.

A project whose build fails keeps its last good copy (cache/projects-built/<channel>/<name>),
and the rest of the site still deploys. Exit code 1 means at least one project needs attention.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def run(cmd: list[str] | str, cwd: Path, shell: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, shell=shell, capture_output=True, text=True, timeout=600)


def newest_tag(repo_dir: Path) -> str | None:
    tags = run(["git", "tag", "--merged", "origin/main"], repo_dir).stdout.split()
    versions = sorted((tuple(map(int, m.groups())), t) for t in tags if (m := TAG.match(t)))
    return versions[-1][1] if versions else None


def checkout(project: dict, channel: str, cache: Path) -> tuple[Path | None, str]:
    repo_dir = cache / project["name"]
    if not (repo_dir / ".git").exists():
        r = run(["git", "clone", "-q", project["repo"], str(repo_dir)], cache)
        if r.returncode:
            return None, f"clone failed: {r.stderr.strip()[:200]}"
    r = run(["git", "fetch", "-q", "--tags", "--force", "origin"], repo_dir)
    if r.returncode:
        return None, f"fetch failed: {r.stderr.strip()[:200]}"
    if channel == "production":
        ref = newest_tag(repo_dir)
        if not ref:
            return None, "no release tag yet; not published to production"
    else:
        ref = "origin/staging"
    r = run(["git", "checkout", "-q", "--detach", ref], repo_dir)
    if r.returncode:
        return None, f"checkout {ref} failed: {r.stderr.strip()[:200]}"
    run(["git", "clean", "-qfdx"], repo_dir)
    return repo_dir, ref


def build_one(project: dict, channel: str, out: Path, cache: Path) -> tuple[bool, str]:
    good = SITE / "cache" / "projects-built" / channel / project["name"]
    repo_dir, ref = checkout(project, channel, cache)
    message = ""
    if repo_dir:
        r = run(project["build"], repo_dir, shell=True)
        built = repo_dir / project["output"]
        if r.returncode == 0 and built.is_dir() and any(built.iterdir()):
            if good.exists():
                shutil.rmtree(good)
            shutil.copytree(built, good)
            message = f"built {ref}"
        else:
            message = f"build of {ref} failed: {(r.stderr or r.stdout).strip()[-300:]}"
    else:
        message = ref
    dest = out / project["path"]
    if good.exists():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(good, dest)
        ok = message.startswith("built") or "no release tag" in message
        return ok, message + ("" if message.startswith("built") else " (kept last good copy)")
    return "no release tag" in message, message


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build project pages into the site.")
    ap.add_argument("--channel", choices=["production", "staging"], required=True)
    ap.add_argument("--out", type=Path, default=SITE / "build")
    args = ap.parse_args(argv)
    with (SITE / "projects.toml").open("rb") as f:
        projects = tomllib.load(f).get("project", [])
    cache = SITE / "cache" / "projects" / args.channel
    cache.mkdir(parents=True, exist_ok=True)
    bad = 0
    for p in projects:
        ok, msg = build_one(p, args.channel, args.out, cache)
        print(f"{p['name']} -> /{p['path']}/: {msg}")
        bad += not ok
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
