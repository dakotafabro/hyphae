import json

from ..core.config import resolve_repo_root
from ..core.io import list_active_threads


def hyphae_primordia_impl() -> str:
    repo_root = resolve_repo_root()
    threads = list_active_threads(repo_root)

    if not threads:
        return json.dumps({"status": "empty", "threads": []}, indent=2)

    summaries = []
    for t in threads:
        task = t.get("task", "")
        summaries.append({
            "thread_name": t.get("thread_name", "unknown"),
            "task": task[:80] if task else "",
            "last_updated": t.get("timestamp", "unknown"),
            "machine": t.get("machine", "unknown"),
        })

    return json.dumps({"status": "active", "threads": summaries}, indent=2)
