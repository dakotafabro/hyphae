from pathlib import Path

from mcp_hyphae.tools.fruit import managed_repos


def test_defaults_to_repo_root(monkeypatch, tmp_path):
    # given
    monkeypatch.delenv("HYPHAE_REPOS", raising=False)
    monkeypatch.delenv("HYPHAE_EXTRA_REPOS", raising=False)

    # when
    result = managed_repos(tmp_path)

    # then
    assert result == [tmp_path]


def test_reads_configured_and_extra_repos_without_duplicates(monkeypatch, tmp_path):
    # given
    monkeypatch.setenv("HYPHAE_REPOS", f"{tmp_path}/a:{tmp_path}/b")
    monkeypatch.setenv("HYPHAE_EXTRA_REPOS", f"{tmp_path}/b:{tmp_path}/c")

    # when
    result = managed_repos(tmp_path)

    # then
    assert result == [Path(f"{tmp_path}/a"), Path(f"{tmp_path}/b"), Path(f"{tmp_path}/c")]
