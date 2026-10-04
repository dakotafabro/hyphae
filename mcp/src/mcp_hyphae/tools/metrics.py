import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from ..core.config import ACTIVE_DIR, HISTORY_DIR, HYPHAE_DIR, get_machine, resolve_repo_root


def hyphae_metrics_impl() -> str:
    repo_root = resolve_repo_root()
    hyphae_dir = repo_root / HYPHAE_DIR
    active_dir = hyphae_dir / ACTIVE_DIR
    history_dir = hyphae_dir / HISTORY_DIR

    now = datetime.now(timezone.utc)
    current_machine = get_machine()

    active_threads = []
    if active_dir.exists():
        for f in active_dir.glob("*.yaml"):
            with open(f) as fh:
                data = yaml.safe_load(fh)
            if data:
                active_threads.append(data)

    completed_threads = []
    if history_dir.exists():
        for f in history_dir.glob("*.yaml"):
            with open(f) as fh:
                data = yaml.safe_load(fh)
            if data:
                completed_threads.append(data)

    total_created = len(active_threads) + len(completed_threads)

    lifespans = []
    for t in completed_threads:
        created = t.get("timestamp", "")
        completed = t.get("completed_at", "")
        if created and completed:
            try:
                start = datetime.fromisoformat(created)
                end = datetime.fromisoformat(completed)
                lifespan_hours = (end - start).total_seconds() / 3600
                lifespans.append(lifespan_hours)
            except (ValueError, TypeError):
                pass

    avg_lifespan_hours = sum(lifespans) / len(lifespans) if lifespans else 0

    longest_active = None
    longest_age_hours = 0
    for t in active_threads:
        ts = t.get("timestamp", "")
        if ts:
            try:
                start = datetime.fromisoformat(ts)
                age = (now - start).total_seconds() / 3600
                if age > longest_age_hours:
                    longest_age_hours = age
                    longest_active = t.get("thread_name", "unknown")
            except (ValueError, TypeError):
                pass

    work_to_personal = 0
    personal_to_work = 0
    transitions = []

    all_threads = active_threads + completed_threads
    all_threads.sort(key=lambda t: t.get("timestamp", ""))

    prev_machine = None
    for t in all_threads:
        machine = t.get("machine", "")
        if prev_machine and machine and machine != prev_machine:
            transitions.append({"from": prev_machine, "to": machine})
            if prev_machine == "work" and machine == "personal":
                work_to_personal += 1
            elif prev_machine == "personal" and machine == "work":
                personal_to_work += 1
        if machine:
            prev_machine = machine

    fruit_path = hyphae_dir / "fruit.yaml"
    last_fruit = None
    if fruit_path.exists():
        with open(fruit_path) as f:
            fruit_data = yaml.safe_load(f)
        if fruit_data:
            last_fruit = {
                "timestamp": fruit_data.get("timestamp", ""),
                "machine": fruit_data.get("machine", ""),
                "threads_at_fruit": fruit_data.get("thread_count", 0),
            }

    result = {
        "threads": {
            "total_created": total_created,
            "currently_active": len(active_threads),
            "completed": len(completed_threads),
            "avg_lifespan_hours": round(avg_lifespan_hours, 1),
            "longest_active": longest_active,
            "longest_active_age_hours": round(longest_age_hours, 1),
        },
        "transitions": {
            "total_cross_machine": work_to_personal + personal_to_work,
            "work_to_personal": work_to_personal,
            "personal_to_work": personal_to_work,
        },
        "current_machine": current_machine,
        "last_fruit": last_fruit,
    }

    return json.dumps(result, indent=2)
