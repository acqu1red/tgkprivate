#!/usr/bin/env bash
set -o pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$REPO_DIR" || exit 1

# Ensure we are on main tracking origin/main
current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$current_branch" != "main" ]]; then
  git checkout main || true
fi

# Ensure remote is reachable before loop
git fetch origin >/dev/null 2>&1 || true

while true; do
  # Stage all changes, including new/deleted files
  git add -A

  # If there are staged changes, commit and push
  if ! git diff --cached --quiet --ignore-submodules --; then
    ts="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    git commit -m "chore(auto-commit): update ${ts}" >/dev/null 2>&1 || true

    # Try to pull rebase and then push to reduce conflicts
    git pull --rebase origin main >/dev/null 2>&1 || true
    git push origin main >/dev/null 2>&1 || true
  fi

  sleep 30
done

