import json
import os
import uuid
from datetime import datetime, timezone

from ..core.config import get_machine, resolve_repo_root
from ..core.io import write_thread


def hyphae_sporulate_impl(
    thread_name: str,
    task: str,
    decisions: str = "",
    open_questions: str = "",
    next_steps: str = "",
    relevant_files: str = "",
    context: str = "",
    handoff_effort: str = "",
) -> str:
    repo_root = resolve_repo_root()
    machine = get_machine()
    session_id = os.environ.get("SPORE_SESSION_ID", str(uuid.uuid4())[:8])
    timestamp = datetime.now(timezone.utc).isoformat()

    data = {
        "thread_name": thread_name,
        "task": task,
        "decisions": decisions,
        "open_questions": open_questions,
        "next_steps": next_steps,
        "relevant_files": relevant_files,
        "context": context,
        "handoff_effort": handoff_effort,
        "timestamp": timestamp,
        "machine": machine,
        "session_id": session_id,
    }

    write_thread(repo_root, thread_name, data)

    result = {
        "status": "sporulated",
        "thread": thread_name,
        "machine": machine,
        "timestamp": timestamp,
        "path": str(repo_root / ".hyphae" / "active" / f"{thread_name}.yaml"),
    }
    return json.dumps(result, indent=2)
