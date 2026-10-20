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

# Deploy whatever is on GitHub main (production), including merged pull requests.
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

# Project pages (course planner and others), from their release tags. A failed project keeps its last
# good copy and doesn't stop the deploy.
if [ -f harvest/build_projects.py ]; then
  if python3 harvest/build_projects.py --channel production --out build >>"$LOG" 2>&1; then say "projects ok"; else say "a project build failed (kept its last good copy)"; fail=1; fi
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

# Staging: keep the staging branch current with main (content refreshes and releases land on main),
# then build it and deploy it as a Cloudflare Pages preview at staging.suffolklitsa.pages.dev.
# A merge conflict skips staging for this run and says so; production is already deployed above.
STAGE=$SITE/cache/staging
if git fetch -q origin main staging >>"$LOG" 2>&1; then
  if [ ! -e "$STAGE/.git" ]; then git worktree add -q -B staging "$STAGE" origin/staging >>"$LOG" 2>&1; fi
  if ( cd "$STAGE" && git reset -q --hard origin/staging && git merge -q --no-edit origin/main ) >>"$LOG" 2>&1; then
    ( cd "$STAGE" && { git diff --quiet origin/staging HEAD || git push -q origin staging; } ) >>"$LOG" 2>&1 && say "staging synced with main" || { say "staging push FAILED"; fail=1; }
    if ( cd "$STAGE" && python3 build.py && { [ ! -f harvest/build_projects.py ] || python3 harvest/build_projects.py --channel staging --out build || echo "a staging project build failed"; } && npx --yes wrangler@latest pages deploy build \
           --project-name suffolklitsa --branch staging --commit-dirty=true ) >>"$LOG" 2>&1; then
      say "staging deploy ok"
    else
      say "staging build or deploy FAILED"; fail=1
    fi
  else
    ( cd "$STAGE" && git merge --abort ) >>"$LOG" 2>&1
    say "staging conflicts with main; resolve by hand (merge main into staging), staging not deployed"; fail=1
  fi
else
  say "staging fetch failed"; fail=1
fi

tail -n 2000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
say "=== events refresh done (fail=$fail)"
exit "$fail"
