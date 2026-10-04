import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .config import ACTIVE_DIR, HISTORY_DIR, HYPHAE_DIR


def _active_dir(repo_root: Path) -> Path:
    return repo_root / HYPHAE_DIR / ACTIVE_DIR


def _history_dir(repo_root: Path) -> Path:
    return repo_root / HYPHAE_DIR / HISTORY_DIR


def read_thread(repo_root: Path, thread_name: str) -> dict | None:
    thread_file = _active_dir(repo_root) / f"{thread_name}.yaml"
    if not thread_file.exists():
        return None
    with open(thread_file, "r") as f:
        return yaml.safe_load(f)


def write_thread(repo_root: Path, thread_name: str, data: dict) -> None:
    active = _active_dir(repo_root)
    active.mkdir(parents=True, exist_ok=True)
    thread_file = active / f"{thread_name}.yaml"
    with open(thread_file, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def list_active_threads(repo_root: Path) -> list[dict]:
    active = _active_dir(repo_root)
    if not active.exists():
        return []

    threads = []
    for file in sorted(active.glob("*.yaml"), key=lambda f: f.stat().st_mtime, reverse=True):
        with open(file, "r") as f:
            data = yaml.safe_load(f)
        if data:
            threads.append(data)
    return threads


def move_to_history(repo_root: Path, thread_name: str, summary: str) -> None:
    active = _active_dir(repo_root)
    history = _history_dir(repo_root)
    history.mkdir(parents=True, exist_ok=True)

    source = active / f"{thread_name}.yaml"
    if not source.exists():
        return

    with open(source, "r") as f:
        data = yaml.safe_load(f)

    data["completed_at"] = datetime.now(timezone.utc).isoformat()
    if summary:
        data["completion_summary"] = summary

    dest = history / f"{thread_name}.yaml"
    with open(dest, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    source.unlink()
