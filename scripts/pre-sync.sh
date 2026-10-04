#!/usr/bin/env bash
set -euo pipefail

hyphae_root="${HYPHAE_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
hyphae_dir="$hyphae_root/.hyphae"
active_dir="$hyphae_dir/active"

machine="${AGENT_MACHINE:-$(cat ~/.agent-machine 2>/dev/null || hostname)}"
timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

repos=()
if [ -n "${HYPHAE_REPOS:-}" ]; then
  IFS=':' read -ra repos <<< "$HYPHAE_REPOS"
else
  repos=("$hyphae_root")
fi

if [ -n "${HYPHAE_EXTRA_REPOS:-}" ]; then
  IFS=':' read -ra extras <<< "$HYPHAE_EXTRA_REPOS"
  repos+=("${extras[@]}")
fi

printf '🌿 [hyphae] capturing environment state before sync...\n' 1>&2

mkdir -p "$hyphae_dir"

fruit_file="$hyphae_dir/fruit.yaml"

cat > "$fruit_file" << EOF
type: fruit
timestamp: $timestamp
machine: $machine
session_id: ${SPORE_SESSION_ID:-$(openssl rand -hex 4 2>/dev/null || printf '%04x' $$)}
repos:
EOF

for repo in "${repos[@]}"; do
  if [ ! -d "$repo/.git" ]; then
    continue
  fi

  branch=$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  last_commit=$(git -C "$repo" log --oneline -1 2>/dev/null || echo "unknown")
  dirty_files=$(git -C "$repo" status --porcelain 2>/dev/null || echo "")
  clean="true"
  if [ -n "$dirty_files" ]; then
    clean="false"
  fi

  cat >> "$fruit_file" << EOF
  - path: $repo
    branch: $branch
    last_commit: "$last_commit"
    clean: $clean
EOF

  if [ "$clean" = "false" ]; then
    printf '    dirty_files:\n' >> "$fruit_file"
    echo "$dirty_files" | head -10 | while IFS= read -r line; do
      file="${line:3}"
      printf '      - "%s"\n' "$file" >> "$fruit_file"
    done
  fi
done

thread_count=0
if [ -d "$active_dir" ]; then
  thread_count=$(find "$active_dir" -name "*.yaml" -type f 2>/dev/null | wc -l | tr -d ' ')
fi

cat >> "$fruit_file" << EOF
threads_active: $thread_count
EOF

if [ -d "$active_dir" ] && [ "$thread_count" -gt 0 ]; then
  printf 'threads:\n' >> "$fruit_file"
  for thread_file in "$active_dir"/*.yaml; do
    [ -f "$thread_file" ] || continue
    name=$(basename "$thread_file" .yaml)
    printf '  - %s\n' "$name" >> "$fruit_file"
  done
fi

printf '🌿 [hyphae] environment captured: %d repos, %d threads\n' "${#repos[@]}" "$thread_count" 1>&2
