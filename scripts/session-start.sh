#!/usr/bin/env bash
set -euo pipefail

cat > /dev/null || true

banner_dir="${XDG_CONFIG_HOME:-$HOME/.config}/goose/banner.d"
if [ -z "${HYPHAE_FORCE_BANNER:-}" ] && compgen -G "$banner_dir/*hyphae*" > /dev/null; then
  exit 0
fi

repo_root="${HYPHAE_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
hyphae_dir="$repo_root/.hyphae/active"

if [ ! -d "$hyphae_dir" ]; then
  exit 0
fi

thread_files=($(find "$hyphae_dir" -name "*.yaml" -type f 2>/dev/null | sort))
thread_count=${#thread_files[@]}

if [ "$thread_count" -eq 0 ]; then
  exit 0
fi

machine="${AGENT_MACHINE:-$(cat ~/.agent-machine 2>/dev/null || hostname)}"

other_machine_threads=0
for thread_file in "${thread_files[@]}"; do
  origin=$(grep "^machine:" "$thread_file" 2>/dev/null | awk '{print $2}' || echo "")
  if [ -n "$origin" ] && [ "$origin" != "$machine" ]; then
    other_machine_threads=$((other_machine_threads + 1))
  fi
done

printf '\n' 1>&2
printf '🍄 ─────────────────────────────────────────────────\n' 1>&2
printf '🍄  hyphae | %d active thread(s) | machine: %s\n' "$thread_count" "$machine" 1>&2
printf '🍄 ─────────────────────────────────────────────────\n' 1>&2

for thread_file in "${thread_files[@]}"; do
  name=$(grep "^thread_name:" "$thread_file" 2>/dev/null | sed 's/^thread_name: *//' | sed "s/^['\"]//;s/['\"]$//" || echo "unknown")
  task=$(grep "^task:" "$thread_file" 2>/dev/null | sed 's/^task: *//' | sed "s/^['\"]//;s/['\"]$//" || echo "")
  origin=$(grep "^machine:" "$thread_file" 2>/dev/null | awk '{print $2}' || echo "?")
  timestamp=$(grep "^timestamp:" "$thread_file" 2>/dev/null | sed "s/^timestamp: *//" | sed "s/^['\"]//;s/['\"]$//" || echo "")

  marker=""
  if [ -n "$origin" ] && [ "$origin" != "$machine" ]; then
    marker=" ← from $origin"
  fi

  task_short="${task:0:60}"
  if [ ${#task} -gt 60 ]; then
    task_short="${task_short}..."
  fi

  printf '🍄  • %s%s\n' "$name" "$marker" 1>&2
  if [ -n "$task_short" ]; then
    printf '🍄    %s\n' "$task_short" 1>&2
  fi
done

printf '🍄 ─────────────────────────────────────────────────\n' 1>&2

if [ "$other_machine_threads" -gt 0 ]; then
  printf '🍄  %d thread(s) from another machine → "germinate" to resume\n' "$other_machine_threads" 1>&2
else
  printf '🍄  say "primordia" for details or pick a thread to continue\n' 1>&2
fi

printf '\n' 1>&2
