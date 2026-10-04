import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

from ..core.config import HYPHAE_DIR, get_machine, resolve_repo_root
from ..core.io import list_active_threads, read_thread


def _tag_germination(repo_root: Path, thread_name: str, cross_machine: bool) -> None:
    session_id = os.environ.get("SPORE_SESSION_ID", "")
    tag = {
        "germinated": True,
        "cross_machine": cross_machine,
        "thread": thread_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
    }

    tag_path = repo_root / HYPHAE_DIR / ".last-germination.yaml"
    tag_path.parent.mkdir(parents=True, exist_ok=True)
    with open(tag_path, "w") as f:
        yaml.dump(tag, f, default_flow_style=False, sort_keys=False)

    os.environ["HYPHAE_GERMINATED"] = "true"
    os.environ["HYPHAE_GERMINATED_CROSS_MACHINE"] = str(cross_machine).lower()


def _read_fruit(repo_root: Path) -> dict | None:
    fruit_path = repo_root / HYPHAE_DIR / "fruit.yaml"
    if not fruit_path.exists():
        return None
    with open(fruit_path, "r") as f:
        return yaml.safe_load(f)


def _check_repo(repo_path: str) -> dict:
    p = Path(repo_path)
    if not p.exists():
        return {"path": repo_path, "status": "missing", "action": "repo not found on this machine"}

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=p, timeout=5,
        )
        current_branch = result.stdout.strip() if result.returncode == 0 else "unknown"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        current_branch = "unknown"

    return {"path": repo_path, "status": "present", "current_branch": current_branch}


def _check_extension_gaps(fruit_extensions: list[str]) -> list[str]:
    config_path = Path.home() / ".config" / "goose" / "config.yaml"
    if not config_path.exists():
        return fruit_extensions

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    except (yaml.YAMLError, OSError):
        return fruit_extensions

    extensions = config.get("extensions", {})
    local_enabled = {
        name for name, ext in extensions.items()
        if isinstance(ext, dict) and ext.get("enabled", False)
    }

    return [ext for ext in fruit_extensions if ext not in local_enabled]


def hyphae_germinate_impl(thread_name: str = "") -> str:
    repo_root = resolve_repo_root()
    current_machine = get_machine()

    if thread_name:
        data = read_thread(repo_root, thread_name)
        if data is None:
            return json.dumps({"status": "not_found", "thread": thread_name}, indent=2)
        cross = data.get("machine", "") != current_machine
        _tag_germination(repo_root, thread_name, cross)
        return json.dumps({"status": "germinated", "thread": data}, indent=2)

    fruit = _read_fruit(repo_root)

    if fruit:
        origin_machine = fruit.get("machine", "unknown")
        cross_machine = origin_machine != current_machine

        threads = list_active_threads(repo_root)
        thread_summaries = []
        for t in threads:
            thread_summaries.append({
                "thread_name": t.get("thread_name", "unknown"),
                "task": t.get("task", "")[:100],
                "machine": t.get("machine", "unknown"),
                "timestamp": t.get("timestamp", ""),
            })

        repos = fruit.get("repos", [])
        repo_status = []
        for repo in repos:
            status = _check_repo(repo.get("path", ""))
            status["fruit_branch"] = repo.get("branch", "unknown")
            status["fruit_clean"] = repo.get("clean", True)
            status["fruit_dirty_files"] = repo.get("dirty_files", [])
            if status["status"] == "present" and status.get("current_branch") != repo.get("branch"):
                status["branch_mismatch"] = True
                status["action"] = f"checkout {repo.get('branch')} to match"
            else:
                status["branch_mismatch"] = False
            repo_status.append(status)

        extension_gaps = _check_extension_gaps(fruit.get("goose_extensions", []))

        patches_dir = repo_root / HYPHAE_DIR / "patches"
        available_patches = []
        if patches_dir.exists():
            available_patches = [p.name for p in patches_dir.glob("*.patch")]

        result = {
            "status": "fruit_available",
            "cross_machine": cross_machine,
            "origin": origin_machine,
            "fruited_at": fruit.get("timestamp", ""),
            "priorities": fruit.get("priorities", ""),
            "working_memory": fruit.get("working_memory", ""),
            "threads": thread_summaries,
            "repos": repo_status,
            "extension_gaps": extension_gaps,
            "patches_available": available_patches,
            "instructions": "Select threads to activate. For repos with branch_mismatch, offer to checkout. For extension_gaps, surface what's missing.",
        }
        return json.dumps(result, indent=2)

    threads = list_active_threads(repo_root)
    if not threads:
        return json.dumps(
            {"status": "empty", "message": "No active threads or fruit found. Use hyphae_sporulate to save working state."},
            indent=2,
        )

    most_recent = threads[0]
    cross = most_recent.get("machine", "") != current_machine
    _tag_germination(repo_root, most_recent.get("thread_name", "unknown"), cross)
    return json.dumps({"status": "germinated", "thread": most_recent}, indent=2)


def hyphae_germinate_thread_impl(thread_name: str) -> str:
    repo_root = resolve_repo_root()
    data = read_thread(repo_root, thread_name)
    if data is None:
        return json.dumps({"status": "not_found", "thread": thread_name}, indent=2)
    return json.dumps({"status": "germinated", "thread": data}, indent=2)


def hyphae_germinate_repos_impl(repo_paths: str) -> str:
    results = []
    for repo_path in repo_paths.split(","):
        repo_path = repo_path.strip()
        if not repo_path:
            continue

        p = Path(repo_path).expanduser()
        if not p.exists():
            results.append({"path": repo_path, "status": "missing"})
            continue

        try:
            subprocess.run(
                ["git", "pull", "--rebase"],
                capture_output=True, text=True, cwd=p, timeout=30,
            )
            results.append({"path": repo_path, "status": "pulled"})
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            results.append({"path": repo_path, "status": "error", "error": str(e)})

    return json.dumps({"status": "repos_synced", "results": results}, indent=2)


def hyphae_apply_patch_impl(patch_name: str) -> str:
    repo_root = resolve_repo_root()
    patches_dir = repo_root / HYPHAE_DIR / "patches"
    patch_path = patches_dir / patch_name

    if not patch_path.exists():
        return json.dumps({"status": "not_found", "patch": patch_name}, indent=2)

    parts = patch_name.replace(".patch", "").split("--")
    if len(parts) >= 2:
        repo_name = parts[-1]
        candidate_paths = [
            Path.home() / "development" / repo_name,
            Path.home() / repo_name,
        ]
        target_repo = None
        for candidate in candidate_paths:
            if candidate.exists():
                target_repo = candidate
                break

        if target_repo is None:
            return json.dumps({
                "status": "error",
                "message": f"Could not find repo '{repo_name}' to apply patch to",
                "patch": patch_name,
            }, indent=2)
    else:
        target_repo = repo_root

    try:
        result = subprocess.run(
            ["git", "apply", "--check", str(patch_path)],
            capture_output=True, text=True, cwd=target_repo, timeout=10,
        )
        if result.returncode != 0:
            return json.dumps({
                "status": "conflict",
                "message": "Patch does not apply cleanly",
                "error": result.stderr.strip(),
                "patch": patch_name,
                "target": str(target_repo),
            }, indent=2)

        subprocess.run(
            ["git", "apply", str(patch_path)],
            capture_output=True, text=True, cwd=target_repo, timeout=10,
        )
        return json.dumps({
            "status": "applied",
            "patch": patch_name,
            "target": str(target_repo),
        }, indent=2)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)
