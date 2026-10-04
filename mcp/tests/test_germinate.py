import json

import yaml

from mcp_hyphae.core.io import write_thread
from mcp_hyphae.tools.germinate import hyphae_germinate_impl


def test_germinate_specific_thread_exists(hyphae_repo):
    write_thread(hyphae_repo, "target", {"thread_name": "target", "task": "do work", "machine": "test-machine"})
    result = json.loads(hyphae_germinate_impl(thread_name="target"))
    assert result["status"] == "germinated"
    assert result["thread"]["task"] == "do work"


def test_germinate_specific_thread_not_found(hyphae_repo):
    result = json.loads(hyphae_germinate_impl(thread_name="ghost"))
    assert result["status"] == "not_found"
    assert result["thread"] == "ghost"


def test_germinate_no_threads_no_fruit(hyphae_repo):
    result = json.loads(hyphae_germinate_impl())
    assert result["status"] == "empty"
    assert "message" in result


def test_germinate_no_thread_name_returns_most_recent(hyphae_repo):
    import os
    write_thread(hyphae_repo, "old-thread", {"thread_name": "old-thread", "task": "old", "machine": "test-machine"})
    os.utime(hyphae_repo / ".hyphae" / "active" / "old-thread.yaml", (1000000, 1000000))
    write_thread(hyphae_repo, "new-thread", {"thread_name": "new-thread", "task": "new", "machine": "test-machine"})
    result = json.loads(hyphae_germinate_impl())
    assert result["status"] == "germinated"
    assert result["thread"]["thread_name"] == "new-thread"


def test_germinate_cross_machine_detection(hyphae_repo):
    write_thread(hyphae_repo, "remote", {"thread_name": "remote", "task": "remote work", "machine": "other-machine"})
    result = json.loads(hyphae_germinate_impl(thread_name="remote"))
    assert result["status"] == "germinated"
    tag_path = hyphae_repo / ".hyphae" / ".last-germination.yaml"
    assert tag_path.exists()
    tag = yaml.safe_load(tag_path.read_text())
    assert tag["cross_machine"] is True


def test_germinate_same_machine_not_cross(hyphae_repo):
    write_thread(hyphae_repo, "local", {"thread_name": "local", "task": "local work", "machine": "test-machine"})
    hyphae_germinate_impl(thread_name="local")
    tag_path = hyphae_repo / ".hyphae" / ".last-germination.yaml"
    tag = yaml.safe_load(tag_path.read_text())
    assert tag["cross_machine"] is False


def test_germinate_with_fruit(hyphae_repo):
    fruit_data = {
        "type": "fruit",
        "timestamp": "2026-09-21T18:00:00+00:00",
        "machine": "other-machine",
        "priorities": "ship tests",
        "working_memory": "building hyphae test suite",
        "threads": [],
        "repos": [],
        "goose_extensions": [],
    }
    fruit_path = hyphae_repo / ".hyphae" / "fruit.yaml"
    with open(fruit_path, "w") as f:
        yaml.dump(fruit_data, f)

    result = json.loads(hyphae_germinate_impl())
    assert result["status"] == "fruit_available"
    assert result["cross_machine"] is True
    assert result["origin"] == "other-machine"
    assert result["priorities"] == "ship tests"


def test_germinate_tags_germination_file(hyphae_repo):
    write_thread(hyphae_repo, "tagged", {"thread_name": "tagged", "task": "test tagging", "machine": "test-machine"})
    hyphae_germinate_impl(thread_name="tagged")
    tag_path = hyphae_repo / ".hyphae" / ".last-germination.yaml"
    assert tag_path.exists()
    tag = yaml.safe_load(tag_path.read_text())
    assert tag["germinated"] is True
    assert tag["thread"] == "tagged"
    assert "timestamp" in tag
