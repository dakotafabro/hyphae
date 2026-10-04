import os
import socket
import subprocess
from pathlib import Path

HYPHAE_DIR = ".hyphae"
ACTIVE_DIR = "active"
HISTORY_DIR = "history"


def resolve_repo_root() -> Path:
    env_root = os.environ.get("HYPHAE_REPO_ROOT")
    if env_root:
        return Path(env_root)

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return Path.cwd()


def get_machine() -> str:
    env_machine = os.environ.get("AGENT_MACHINE")
    if env_machine:
        return env_machine

    machine_file = Path.home() / ".agent-machine"
    if machine_file.exists():
        content = machine_file.read_text().strip()
        if content:
            return content

    return socket.gethostname()
