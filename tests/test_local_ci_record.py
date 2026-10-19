"""Local CI sign-off validity (scripts/governance/local_ci_record.py check)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts.governance import local_ci_record


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _repo_with_record(tmp_path: Path, status: str = "PASS") -> Path:
    (tmp_path / "core.py").write_text("x = 1\n")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "code")
    tested = _git(tmp_path, "rev-parse", "HEAD")
    record_dir = tmp_path / local_ci_record.RECORD_DIR
    record_dir.mkdir(parents=True)
    (record_dir / f"{tested}.json").write_text(
        json.dumps(
            {
                "schema_version": local_ci_record.RECORD_SCHEMA,
                "kind": "LOCAL_VERIFICATION",
                "tested_commit": tested,
                "recorded_at": "2026-10-10T00:00:00+00:00",
                "status": status,
            }
        )
    )
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "docs: local CI record")
    return tmp_path


def test_record_stays_valid_across_doc_only_commits(tmp_path, monkeypatch, capsys):
    repo = _repo_with_record(tmp_path)
    (repo / "NOTES.md").write_text("notes\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "docs: notes")
    monkeypatch.chdir(repo)
    assert local_ci_record.check() == 0
    assert json.loads(capsys.readouterr().out)["kind"] == "LOCAL_VERIFICATION"


def test_code_change_invalidates_record(tmp_path, monkeypatch, capsys):
    repo = _repo_with_record(tmp_path)
    (repo / "core.py").write_text("x = 2\n")
    _git(repo, "commit", "-q", "-am", "fix: change code")
    monkeypatch.chdir(repo)
    assert local_ci_record.check() == 1
    assert json.loads(capsys.readouterr().out)["code_changed_since"] == ["core.py"]


def test_failed_record_is_never_valid(tmp_path, monkeypatch):
    repo = _repo_with_record(tmp_path, status="FAIL")
    monkeypatch.chdir(repo)
    assert local_ci_record.check() == 1


def test_missing_record_fails(tmp_path, monkeypatch):
    (tmp_path / "a.py").write_text("")
    _git(tmp_path, "init", "-q")
    monkeypatch.chdir(tmp_path)
    assert local_ci_record.check() == 1


def test_run_refuses_dirty_tree(tmp_path, monkeypatch):
    repo = _repo_with_record(tmp_path)
    (repo / "core.py").write_text("dirty\n")
    monkeypatch.chdir(repo)
    assert local_ci_record.run("python3") == 2
