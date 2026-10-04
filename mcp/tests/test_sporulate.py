import json

import yaml

from mcp_hyphae.tools.sporulate import hyphae_sporulate_impl


def test_sporulate_returns_sporulated_status(hyphae_repo):
    result = json.loads(hyphae_sporulate_impl(thread_name="test-thread", task="build feature"))
    assert result["status"] == "sporulated"


def test_sporulate_returns_thread_name(hyphae_repo):
    result = json.loads(hyphae_sporulate_impl(thread_name="my-thread", task="do work"))
    assert result["thread"] == "my-thread"


def test_sporulate_returns_machine(hyphae_repo):
    result = json.loads(hyphae_sporulate_impl(thread_name="test", task="task"))
    assert result["machine"] == "test-machine"


def test_sporulate_returns_timestamp(hyphae_repo):
    result = json.loads(hyphae_sporulate_impl(thread_name="test", task="task"))
    assert "timestamp" in result
    assert isinstance(result["timestamp"], str)


def test_sporulate_returns_path(hyphae_repo):
    result = json.loads(hyphae_sporulate_impl(thread_name="test", task="task"))
    assert result["path"].endswith(".hyphae/active/test.yaml")


def test_sporulate_creates_thread_file(hyphae_repo):
    hyphae_sporulate_impl(thread_name="disk-check", task="verify file creation")
    assert (hyphae_repo / ".hyphae" / "active" / "disk-check.yaml").exists()


def test_sporulate_thread_file_contains_all_fields(hyphae_repo):
    hyphae_sporulate_impl(
        thread_name="full",
        task="build tests",
        decisions="use pytest",
        open_questions="coverage?",
        next_steps="run CI",
        relevant_files="mcp/tests/",
        context="initial build",
    )
    data = yaml.safe_load((hyphae_repo / ".hyphae" / "active" / "full.yaml").read_text())
    assert data["thread_name"] == "full"
    assert data["task"] == "build tests"
    assert data["decisions"] == "use pytest"
    assert data["open_questions"] == "coverage?"
    assert data["next_steps"] == "run CI"
    assert data["relevant_files"] == "mcp/tests/"
    assert data["context"] == "initial build"
    assert data["machine"] == "test-machine"
    assert "timestamp" in data
    assert "session_id" in data


def test_sporulate_minimal_call(hyphae_repo):
    result = json.loads(hyphae_sporulate_impl(thread_name="minimal", task="just a task"))
    assert result["status"] == "sporulated"
    data = yaml.safe_load((hyphae_repo / ".hyphae" / "active" / "minimal.yaml").read_text())
    assert data["task"] == "just a task"
    assert data["decisions"] == ""
    assert data["open_questions"] == ""


def test_sporulate_records_handoff_effort(hyphae_repo):
    hyphae_sporulate_impl(thread_name="shared", task="t", handoff_effort="feature-123-filter")
    data = yaml.safe_load((hyphae_repo / ".hyphae" / "active" / "shared.yaml").read_text())
    assert data["handoff_effort"] == "feature-123-filter"


def test_sporulate_leaves_handoff_effort_empty_by_default(hyphae_repo):
    hyphae_sporulate_impl(thread_name="personal", task="t")
    data = yaml.safe_load((hyphae_repo / ".hyphae" / "active" / "personal.yaml").read_text())
    assert data["handoff_effort"] == ""
