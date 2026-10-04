import time
from pathlib import Path

import yaml

from mcp_hyphae.core.io import (
    list_active_threads,
    move_to_history,
    read_thread,
    write_thread,
)


def test_write_thread_creates_yaml_file(hyphae_repo):
    write_thread(hyphae_repo, "my-thread", {"task": "do stuff"})
    assert (hyphae_repo / ".hyphae" / "active" / "my-thread.yaml").exists()


def test_write_thread_content_is_valid_yaml(hyphae_repo):
    data = {"task": "build feature", "decisions": "use pytest"}
    write_thread(hyphae_repo, "my-thread", data)
    raw = (hyphae_repo / ".hyphae" / "active" / "my-thread.yaml").read_text()
    parsed = yaml.safe_load(raw)
    assert parsed == data


def test_read_thread_returns_written_data(hyphae_repo):
    data = {"task": "build feature", "context": "some context"}
    write_thread(hyphae_repo, "roundtrip", data)
    result = read_thread(hyphae_repo, "roundtrip")
    assert result == data


def test_read_thread_nonexistent_returns_none(hyphae_repo):
    assert read_thread(hyphae_repo, "does-not-exist") is None


def test_list_active_threads_empty(hyphae_repo):
    assert list_active_threads(hyphae_repo) == []


def test_list_active_threads_returns_all(hyphae_repo):
    write_thread(hyphae_repo, "thread-a", {"thread_name": "thread-a", "task": "a"})
    write_thread(hyphae_repo, "thread-b", {"thread_name": "thread-b", "task": "b"})
    threads = list_active_threads(hyphae_repo)
    names = {t["thread_name"] for t in threads}
    assert names == {"thread-a", "thread-b"}
    assert len(threads) == 2


def test_list_active_threads_sorted_by_mtime(hyphae_repo):
    write_thread(hyphae_repo, "older", {"thread_name": "older", "task": "old"})
    older_file = hyphae_repo / ".hyphae" / "active" / "older.yaml"
    import os
    os.utime(older_file, (1000000, 1000000))

    write_thread(hyphae_repo, "newer", {"thread_name": "newer", "task": "new"})

    threads = list_active_threads(hyphae_repo)
    assert threads[0]["thread_name"] == "newer"
    assert threads[1]["thread_name"] == "older"


def test_list_active_threads_no_active_dir(tmp_path):
    assert list_active_threads(tmp_path) == []


def test_move_to_history_removes_from_active(hyphae_repo):
    write_thread(hyphae_repo, "done-thread", {"task": "finished"})
    move_to_history(hyphae_repo, "done-thread", "completed successfully")
    assert not (hyphae_repo / ".hyphae" / "active" / "done-thread.yaml").exists()


def test_move_to_history_creates_in_history(hyphae_repo):
    write_thread(hyphae_repo, "done-thread", {"task": "finished"})
    move_to_history(hyphae_repo, "done-thread", "completed successfully")
    assert (hyphae_repo / ".hyphae" / "history" / "done-thread.yaml").exists()


def test_move_to_history_adds_completed_at(hyphae_repo):
    write_thread(hyphae_repo, "done-thread", {"task": "finished"})
    move_to_history(hyphae_repo, "done-thread", "all done")
    history_file = hyphae_repo / ".hyphae" / "history" / "done-thread.yaml"
    data = yaml.safe_load(history_file.read_text())
    assert "completed_at" in data
    assert isinstance(data["completed_at"], str)


def test_move_to_history_adds_completion_summary(hyphae_repo):
    write_thread(hyphae_repo, "done-thread", {"task": "finished"})
    move_to_history(hyphae_repo, "done-thread", "shipped the feature")
    history_file = hyphae_repo / ".hyphae" / "history" / "done-thread.yaml"
    data = yaml.safe_load(history_file.read_text())
    assert data["completion_summary"] == "shipped the feature"


def test_move_to_history_nonexistent_thread_is_noop(hyphae_repo):
    move_to_history(hyphae_repo, "ghost", "summary")
    assert not (hyphae_repo / ".hyphae" / "history" / "ghost.yaml").exists()


def test_roundtrip_write_read_preserves_all_fields(hyphae_repo):
    data = {
        "thread_name": "full-thread",
        "task": "build tests",
        "decisions": "use pytest",
        "open_questions": "coverage threshold?",
        "next_steps": "run CI",
        "relevant_files": "mcp/tests/",
        "context": "initial build",
        "timestamp": "2026-09-21T18:00:00+00:00",
        "machine": "test-machine",
        "session_id": "abc123",
    }
    write_thread(hyphae_repo, "full-thread", data)
    result = read_thread(hyphae_repo, "full-thread")
    assert result == data


def test_write_thread_creates_active_dir_if_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("HYPHAE_REPO_ROOT", str(tmp_path))
    write_thread(tmp_path, "auto-dir", {"task": "test"})
    assert (tmp_path / ".hyphae" / "active" / "auto-dir.yaml").exists()
