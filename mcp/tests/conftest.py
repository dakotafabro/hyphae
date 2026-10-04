import pytest
from pathlib import Path


@pytest.fixture
def hyphae_repo(tmp_path, monkeypatch):
    (tmp_path / ".hyphae" / "active").mkdir(parents=True)
    (tmp_path / ".hyphae" / "history").mkdir(parents=True)
    monkeypatch.setenv("HYPHAE_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("AGENT_MACHINE", "test-machine")
    return tmp_path
