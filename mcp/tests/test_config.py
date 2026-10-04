from pathlib import Path

from mcp_hyphae.core.config import (
    ACTIVE_DIR,
    HISTORY_DIR,
    HYPHAE_DIR,
    get_machine,
    resolve_repo_root,
)


def test_hyphae_dir_constant():
    assert HYPHAE_DIR == ".hyphae"


def test_active_dir_constant():
    assert ACTIVE_DIR == "active"


def test_history_dir_constant():
    assert HISTORY_DIR == "history"


def test_get_machine_returns_string(monkeypatch):
    monkeypatch.setenv("AGENT_MACHINE", "test-box")
    assert get_machine() == "test-box"


def test_get_machine_falls_back_to_hostname(monkeypatch):
    monkeypatch.delenv("AGENT_MACHINE", raising=False)
    machine_file = Path.home() / ".agent-machine"
    original_exists = machine_file.exists()
    if original_exists:
        monkeypatch.setattr(Path, "exists", lambda self: False if self == machine_file else Path.exists(self))
    result = get_machine()
    assert isinstance(result, str)
    assert len(result) > 0


def test_resolve_repo_root_uses_env(monkeypatch, tmp_path):
    monkeypatch.setenv("HYPHAE_REPO_ROOT", str(tmp_path))
    assert resolve_repo_root() == tmp_path


def test_resolve_repo_root_returns_path(monkeypatch, tmp_path):
    monkeypatch.setenv("HYPHAE_REPO_ROOT", str(tmp_path))
    result = resolve_repo_root()
    assert isinstance(result, Path)
