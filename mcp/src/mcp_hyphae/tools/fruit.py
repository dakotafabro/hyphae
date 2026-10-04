import json
import os
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

from ..core.config import ACTIVE_DIR, HYPHAE_DIR, get_machine, resolve_repo_root
from ..core.io import list_active_threads, read_thread, write_thread


def managed_repos(repo_root: Path) -> list[Path]:
    configured = os.environ.get("HYPHAE_REPOS", "")
    paths = [Path(p.strip()).expanduser() for p in configured.split(":") if p.strip()]
    if not paths:
        paths = [repo_root]
    extra = os.environ.get("HYPHAE_EXTRA_REPOS", "")
    paths += [Path(p.strip()).expanduser() for p in extra.split(":") if p.strip()]
    return list(dict.fromkeys(paths))


def _get_repo_state(repo_path: Path) -> dict | None:
    if not repo_path.exists():
        return None

    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=repo_path, timeout=5,
        )
        last_commit = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            capture_output=True, text=True, cwd=repo_path, timeout=5,
        )
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=repo_path, timeout=5,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

    dirty_files = [
        line[3:] for line in dirty.stdout.strip().splitlines()
        if line.strip()
    ]

    return {
        "path": str(repo_path),
        "branch": branch.stdout.strip() if branch.returncode == 0 else "unknown",
        "last_commit": last_commit.stdout.strip() if last_commit.returncode == 0 else "unknown",
        "clean": len(dirty_files) == 0,
        "dirty_files": dirty_files[:20],
    }


def _create_patch(repo_path: Path, thread_name: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "diff"],
            capture_output=True, text=True, cwd=repo_path, timeout=10,
        )
        staged = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True, cwd=repo_path, timeout=10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

    combined = (result.stdout or "") + (staged.stdout or "")
    if not combined.strip():
        return None

    hyphae_root = resolve_repo_root()
    patches_dir = hyphae_root / HYPHAE_DIR / "patches"
    patches_dir.mkdir(parents=True, exist_ok=True)

    repo_name = repo_path.name
    patch_path = patches_dir / f"{thread_name}--{repo_name}.patch"
    patch_path.write_text(combined, encoding="utf-8")
    return str(patch_path)


def hyphae_fruit_impl(
    priorities: str = "",
    working_memory: str = "",
) -> str:
    repo_root = resolve_repo_root()
    machine = get_machine()
    session_id = os.environ.get("SPORE_SESSION_ID", str(uuid.uuid4())[:8])
    timestamp = datetime.now(timezone.utc).isoformat()

    threads = list_active_threads(repo_root)

    repos = []
    for repo_path in managed_repos(repo_root):
        state = _get_repo_state(repo_path)
        if state:
            repos.append(state)

    patches_created = []
    patches_cross_machine = _load_policy(repo_root).get("patches_cross_machine", False)
    if patches_cross_machine:
        for repo in repos:
            if not repo["clean"]:
                for thread in threads:
                    thread_data = read_thread(repo_root, thread["thread_name"])
                    if thread_data and thread_data.get("relevant_files", ""):
                        repo_path_str = repo["path"]
                        if any(repo_path_str in f for f in thread_data["relevant_files"].split(",")):
                            patch = _create_patch(Path(repo["path"]), thread["thread_name"])
                            if patch:
                                patches_created.append(patch)
                                break

    snapshot = {
        "type": "fruit",
        "timestamp": timestamp,
        "machine": machine,
        "session_id": session_id,
        "priorities": priorities,
        "working_memory": working_memory,
        "threads": [t["thread_name"] for t in threads],
        "thread_count": len(threads),
        "repos": repos,
        "patches": patches_created,
        "goose_extensions": _detect_extensions(),
    }

    snapshot_path = repo_root / HYPHAE_DIR / "fruit.yaml"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    with open(snapshot_path, "w") as f:
        yaml.dump(snapshot, f, default_flow_style=False, sort_keys=False)

    result = {
        "status": "fruited",
        "machine": machine,
        "timestamp": timestamp,
        "threads_captured": len(threads),
        "repos_captured": len(repos),
        "dirty_repos": sum(1 for r in repos if not r["clean"]),
        "patches_created": len(patches_created),
        "path": str(snapshot_path),
    }
    return json.dumps(result, indent=2)


def _load_policy(repo_root: Path) -> dict:
    policy_path = repo_root / HYPHAE_DIR / "policy.yaml"
    if not policy_path.exists():
        return {"patches_cross_machine": False}
    try:
        with open(policy_path, "r") as f:
            raw = yaml.safe_load(f) or {}
        return raw.get("policy", raw)
    except (yaml.YAMLError, OSError):
        return {"patches_cross_machine": False}


def _detect_extensions() -> list[str]:
    config_path = Path.home() / ".config" / "goose" / "config.yaml"
    if not config_path.exists():
        return []

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    except (yaml.YAMLError, OSError):
        return []

    extensions = config.get("extensions", {})
    return [
        name for name, ext in extensions.items()
        if isinstance(ext, dict) and ext.get("enabled", False)
    ]
