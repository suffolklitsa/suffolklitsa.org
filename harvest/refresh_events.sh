#!/usr/bin/env bash
# Twice-daily refresh of /events/ and the headlines on /watch/. Runs from cron; nobody watches it run.
#
# Same shape as refresh_watch.sh: harvest, build, deploy, all in one job. Past events drop off
# at build time, so even a day when every source fails still publishes a page with nothing stale.
# Exit codes matter to cron mail: 0 clean, 1 something worth reading about.
set -uo pipefail

SITE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG=$SITE/cache/events-refresh.log
STAMP=$(date -u '+%Y-%m-%d %H:%M UTC')
cd "$SITE" || exit 1
mkdir -p "$(dirname "$LOG")"

say() { echo "[$STAMP] $*" | tee -a "$LOG"; }

fail=0
say "=== events refresh start"

# Deploy whatever is on GitHub main, including merged pull requests.
if git pull --ff-only -q >>"$LOG" 2>&1; then say "git pull ok"; else say "git pull failed (building the local copy)"; fail=1; fi

if python3 harvest/harvest_events.py >>"$LOG" 2>&1; then
  say "harvest ok"
else
  say "a source failed (kept its last good events)"; fail=1
fi

if python3 harvest/harvest_news.py >>"$LOG" 2>&1; then
  say "news ok"
else
  say "a news feed failed (kept its last good headlines)"; fail=1
fi

if ! python3 build.py >>"$LOG" 2>&1; then
  say "BUILD FAILED — not deploying, site stays as it was"
  exit 1
fi

if [ ! -s build/events/index.html ]; then
  say "events page missing from build — not deploying"
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

tail -n 2000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
say "=== events refresh done (fail=$fail)"
exit "$fail"
