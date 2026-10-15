#!/usr/bin/env bash
# Weekly refresh of the /watch/ page. Runs from cron; nobody watches it run.
#
# Deliberately does the whole job end to end, including the deploy. A harvest
# that updates a JSON file nobody publishes is the same as no harvest, and
# splitting it into two jobs just gives us two things that can silently stop.
#
# Exit codes matter to cron mail: 0 clean, 1 something worth reading about.
set -uo pipefail

SITE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG=$SITE/cache/watch-refresh.log
STAMP=$(date -u '+%Y-%m-%d %H:%M UTC')
cd "$SITE" || exit 1
mkdir -p "$(dirname "$LOG")"

say() { echo "[$STAMP] $*" | tee -a "$LOG"; }

fail=0
say "=== refresh start"

# Deploy whatever is on GitHub main, including merged pull requests.
if git pull --ff-only -q >>"$LOG" 2>&1; then say "git pull ok"; else say "git pull failed (building the local copy)"; fail=1; fi

# Sources first. Either can fail without taking the other down; the page keeps
# showing whatever last succeeded, and its own last-refreshed date goes stale.
if python3 harvest/harvest_litigation.py >>"$LOG" 2>&1; then
  say "litigation ok"
else
  say "litigation FAILED (page keeps prior items, date will show it)"; fail=1
fi

if python3 harvest/harvest_press.py >>"$LOG" 2>&1; then
  say "press ok"
else
  say "press reported a dead link"; fail=1
fi

# The /compete/ catalogue: dead links and changed organizer pages, for a person to read.
# It never edits the catalogue itself. Report: cache/competitions-check.md
if python3 harvest/check_competitions.py >>"$LOG" 2>&1; then
  say "competitions: quiet week"
else
  say "competitions: something to read in cache/competitions-check.md"; fail=1
fi

if ! python3 build.py >>"$LOG" 2>&1; then
  say "BUILD FAILED — not deploying, site stays as it was"
  exit 1
fi
say "build ok"

# Only publish when the build produced the page we expect.
if [ ! -s build/watch/index.html ]; then
  say "watch page missing from build — not deploying"
  exit 1
fi

if npx --yes wrangler@latest pages deploy build \
     --project-name suffolklitsa --commit-dirty=true >>"$LOG" 2>&1; then
  say "deploy ok"
else
  say "DEPLOY FAILED"; fail=1
fi

# Save what the harvest changed back to GitHub so the repository matches the live site.
if ! git diff --quiet -- content; then
  if git add content && git commit -qm "content: scheduled refresh" && git push -q >>"$LOG" 2>&1; then
    say "content pushed"
  else
    say "content push FAILED"; fail=1
  fi
fi

# Keep the log from growing without bound.
tail -n 2000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"

say "=== refresh done (fail=$fail)"
exit "$fail"
