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


def _free_history_path(history: Path, thread_name: str, completed_at: datetime) -> Path:
    dest = history / f"{thread_name}.yaml"
    if not dest.exists():
        return dest
    base = f"{thread_name}--closed-{completed_at.strftime('%Y%m%dT%H%M%SZ')}"
    dest, n = history / f"{base}.yaml", 2
    while dest.exists():
        dest, n = history / f"{base}-{n}.yaml", n + 1
    return dest


def move_to_history(repo_root: Path, thread_name: str, summary: str) -> Path | None:
    """Moves an active thread into history and returns the file it wrote, or None when the thread isn't active.

    A thread name can be closed more than once (a name reused after an earlier close), so an existing history
    file is never replaced: the later close is written as <name>--closed-<UTC time>.yaml, with thread_name unchanged.
    """
    active = _active_dir(repo_root)
    history = _history_dir(repo_root)
    history.mkdir(parents=True, exist_ok=True)

    source = active / f"{thread_name}.yaml"
    if not source.exists():
        return None

    with open(source, "r") as f:
        data = yaml.safe_load(f)

    completed_at = datetime.now(timezone.utc)
    data["completed_at"] = completed_at.isoformat()
    if summary:
        data["completion_summary"] = summary

    dest = _free_history_path(history, thread_name, completed_at)
    with open(dest, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    source.unlink()
    return dest
