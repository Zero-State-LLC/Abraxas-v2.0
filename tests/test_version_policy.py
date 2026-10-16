"""Doctrine-revision version policy (scripts/governance/validate_version_policy.py)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.governance.validate_version_policy import REFERENCE_PACKAGE_VERSION, evaluate

REPO_ROOT = Path(__file__).resolve().parents[1]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
        check=True,
        capture_output=True,
    )


def _repo(tmp_path: Path, *, version: str, changelog_top: str, package: str = REFERENCE_PACKAGE_VERSION) -> Path:
    (tmp_path / "VERSION").write_text(f"{version}\n")
    (tmp_path / "CHANGELOG.md").write_text(f"# [{changelog_top}](https://example.invalid) (2026-01-01)\n")
    (tmp_path / "pyproject.toml").write_text(f'[project]\nname = "x"\nversion = "{package}"\n')
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def _commit(repo: Path, message: str) -> None:
    _git(repo, "commit", "-q", "--allow-empty", "-m", message)


def test_repository_satisfies_policy():
    result = evaluate(REPO_ROOT)
    assert result["status"] == "PASS", result


def test_development_commits_after_release_tag_pass(tmp_path):
    repo = _repo(tmp_path, version="1.2.0", changelog_top="1.2.0")
    _git(repo, "tag", "v1.2.0")
    _commit(repo, "feat: unreleased work")
    assert evaluate(repo)["status"] == "PASS"
    assert evaluate(repo, strict=True)["status"] == "PASS"


def test_tag_created_later_only_warns_until_sync_pr(tmp_path):
    repo = _repo(tmp_path, version="1.2.0", changelog_top="1.2.0")
    _git(repo, "tag", "v1.2.0")
    _commit(repo, "feat: released by bot")
    _git(repo, "tag", "v1.3.0")
    relaxed = evaluate(repo)
    assert relaxed["status"] == "PASS"
    assert relaxed["tag_status"] == "LAGGING"
    assert relaxed["warnings"] == ["VERSION_LAGS_LATEST_TAG:v1.2.0<v1.3.0"]
    assert evaluate(repo, strict=True)["status"] == "FAIL"


def test_product_version_without_tag_fails(tmp_path):
    repo = _repo(tmp_path, version="2.5.0", changelog_top="2.5.0")
    _git(repo, "tag", "v1.180.0")
    result = evaluate(repo)
    assert result["status"] == "FAIL"
    assert "VERSION_HAS_NO_REACHABLE_TAG:v2.5.0" in result["errors"]


def test_changelog_must_match_version(tmp_path):
    repo = _repo(tmp_path, version="1.2.0", changelog_top="1.1.0")
    _git(repo, "tag", "v1.2.0")
    assert "CHANGELOG_TOP_MISMATCH:1.1.0!=1.2.0" in evaluate(repo)["errors"]


def test_pyproject_must_not_claim_product_version(tmp_path):
    repo = _repo(tmp_path, version="1.2.0", changelog_top="1.2.0", package="2.5.0")
    _git(repo, "tag", "v1.2.0")
    assert "PYPROJECT_NOT_REFERENCE:2.5.0" in evaluate(repo)["errors"]


@pytest.mark.parametrize("strict, expected", [(False, "PASS"), (True, "FAIL")])
def test_missing_tags_are_not_computable(tmp_path, strict, expected):
    repo = _repo(tmp_path, version="1.2.0", changelog_top="1.2.0")
    result = evaluate(repo, strict=strict)
    assert result["tag_status"] == "NOT_COMPUTABLE"
    assert result["status"] == expected
