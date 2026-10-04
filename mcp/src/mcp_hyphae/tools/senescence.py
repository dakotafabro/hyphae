import json

from ..core.config import resolve_repo_root
from ..core.io import move_to_history, read_thread


def hyphae_senescence_impl(thread_name: str, summary: str = "") -> str:
    repo_root = resolve_repo_root()

    data = read_thread(repo_root, thread_name)
    if data is None:
        return json.dumps({"status": "not_found", "thread": thread_name}, indent=2)

    move_to_history(repo_root, thread_name, summary)

    result = {
        "status": "completed",
        "thread": thread_name,
        "moved_to": str(repo_root / ".hyphae" / "history" / f"{thread_name}.yaml"),
    }
    if summary:
        result["summary"] = summary

    return json.dumps(result, indent=2)
