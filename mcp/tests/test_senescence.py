import json

from mcp_hyphae.core.io import write_thread
from mcp_hyphae.tools.senescence import hyphae_senescence_impl


def test_senescence_reports_the_file_it_wrote_for_a_reused_name(hyphae_repo):
    write_thread(hyphae_repo, "pickup", {"thread_name": "pickup", "task": "first"})
    first = json.loads(hyphae_senescence_impl("pickup", "first close"))
    write_thread(hyphae_repo, "pickup", {"thread_name": "pickup", "task": "second"})
    second = json.loads(hyphae_senescence_impl("pickup", "second close"))

    history = hyphae_repo / ".hyphae" / "history"
    assert first["moved_to"] == str(history / "pickup.yaml")
    assert second["moved_to"] != first["moved_to"]
    assert (history / "pickup.yaml").exists()
    assert (history / second["moved_to"].rsplit("/", 1)[-1]).exists()


def test_senescence_not_found(hyphae_repo):
    assert json.loads(hyphae_senescence_impl("ghost"))["status"] == "not_found"
