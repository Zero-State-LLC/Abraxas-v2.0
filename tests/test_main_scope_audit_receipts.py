"""Main-scope cleanliness + fast-ci receipts (Notion engineering-quality audit)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from abraxas.cli import main
from core.audit.fast_ci_receipt import (
    build_fast_ci_receipt,
    run_checks,
    smoke_check_commands,
    write_fast_ci_receipt,
)
from core.audit.main_cleanliness_receipt import (
    build_main_cleanliness_receipt,
    collect_git_state,
    write_main_cleanliness_receipt,
)

REPO = Path(__file__).resolve().parents[1]
CLEAN_SCHEMA = REPO / "contracts" / "audit" / "main_cleanliness.v0.schema.json"
FAST_SCHEMA = REPO / "contracts" / "audit" / "fast_ci_receipt.v0.schema.json"


def test_main_cleanliness_pass_from_injected_state():
    state = {
        "collect_status": "OBSERVED",
        "collect_reason": None,
        "commit_sha": "abc123",
        "branch": "main",
        "compare_ref": "origin/main",
        "origin_main_sha": "abc123",
        "ahead": 0,
        "behind": 0,
        "worktree_clean": True,
        "tracked_dirty": False,
        "untracked_present": True,
        "dirty_tracked_paths": [],
        "untracked_paths_sample": [".hermes/"],
        "count_error": None,
    }
    packet = build_main_cleanliness_receipt(repo_root=REPO, git_state=state)
    assert packet["status"] == "PASS"
    assert packet["worktree_clean"] is True
    assert packet["untracked_present"] is True
    assert packet["authority"]["notion_writeback_allowed"] is False
    Draft7Validator(json.loads(CLEAN_SCHEMA.read_text(encoding="utf-8"))).validate(
        packet
    )


def test_main_cleanliness_fail_when_ahead():
    state = {
        "collect_status": "OBSERVED",
        "commit_sha": "a",
        "branch": "main",
        "compare_ref": "origin/main",
        "origin_main_sha": "b",
        "ahead": 2,
        "behind": 0,
        "worktree_clean": True,
        "tracked_dirty": False,
        "untracked_present": False,
        "dirty_tracked_paths": [],
        "untracked_paths_sample": [],
    }
    packet = build_main_cleanliness_receipt(repo_root=REPO, git_state=state)
    assert packet["status"] == "FAIL"
    assert any("ahead" in b for b in packet["blockers"])


def test_main_cleanliness_fail_when_tracked_dirty():
    state = {
        "collect_status": "OBSERVED",
        "commit_sha": "a",
        "branch": "main",
        "compare_ref": "origin/main",
        "origin_main_sha": "a",
        "ahead": 0,
        "behind": 0,
        "worktree_clean": False,
        "tracked_dirty": True,
        "untracked_present": False,
        "dirty_tracked_paths": ["core/foo.py"],
        "untracked_paths_sample": [],
    }
    packet = build_main_cleanliness_receipt(repo_root=REPO, git_state=state)
    assert packet["status"] == "FAIL"
    assert "tracked_worktree_dirty" in packet["blockers"]


def test_main_cleanliness_collect_with_fake_runner():
    responses = {
        ("rev-parse", "HEAD"): (0, "deadbeef", ""),
        ("branch", "--show-current"): (0, "main", ""),
        ("rev-parse", "origin/main"): (0, "deadbeef", ""),
        ("rev-list", "--left-right", "--count", "HEAD...origin/main"): (0, "0\t0", ""),
        ("status", "--porcelain"): (0, "?? local_only/\n", ""),
    }

    def runner(_root, args):
        return responses[args]

    state = collect_git_state(REPO, runner=runner)
    assert state["worktree_clean"] is True
    assert state["untracked_present"] is True
    packet = build_main_cleanliness_receipt(repo_root=REPO, git_state=state)
    assert packet["status"] == "PASS"


def test_main_cleanliness_writer(tmp_path: Path):
    packet = build_main_cleanliness_receipt(
        repo_root=REPO,
        git_state={
            "collect_status": "OBSERVED",
            "commit_sha": "c",
            "branch": "main",
            "compare_ref": "origin/main",
            "origin_main_sha": "c",
            "ahead": 0,
            "behind": 0,
            "worktree_clean": True,
            "tracked_dirty": False,
            "untracked_present": False,
            "dirty_tracked_paths": [],
            "untracked_paths_sample": [],
        },
    )
    target = tmp_path / "main_cleanliness.latest.json"
    write_main_cleanliness_receipt(target, packet)
    assert target.is_file()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["canonical_hash"] == packet["canonical_hash"]


def test_fast_ci_meta_only_is_not_computable():
    packet = build_fast_ci_receipt(
        repo_root=REPO,
        commit_sha="c",
        origin_main_sha="c",
        execute_smoke=False,
        check_results=None,
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["mode"] == "meta_only"
    assert packet["authoritative_full_ci_command"] == "python scripts/run_fast_ci.py"


def test_fast_ci_injected_pass():
    checks = [
        {
            "name": "pytest_main_scope_audit_receipts",
            "command": ["pytest"],
            "required": True,
            "exit_code": 0,
            "status": "PASS",
        },
        {
            "name": "ruff_audit_modules",
            "command": ["ruff"],
            "required": True,
            "exit_code": 0,
            "status": "PASS",
        },
    ]
    packet = build_fast_ci_receipt(
        repo_root=REPO,
        commit_sha="c",
        origin_main_sha="c",
        check_results=checks,
    )
    assert packet["status"] == "PASS"
    assert packet["mode"] == "injected"
    assert packet["pass_count"] == 2
    Draft7Validator(json.loads(FAST_SCHEMA.read_text(encoding="utf-8"))).validate(
        packet
    )


def test_fast_ci_injected_fail():
    packet = build_fast_ci_receipt(
        repo_root=REPO,
        commit_sha="c",
        origin_main_sha="c",
        check_results=[
            {
                "name": "pytest_main_scope_audit_receipts",
                "command": ["pytest"],
                "required": True,
                "exit_code": 1,
                "status": "FAIL",
            }
        ],
    )
    assert packet["status"] == "FAIL"


def test_fast_ci_run_checks_with_fake_runner():
    def runner(cmd, _root):
        return {"exit_code": 0, "stdout_tail": "ok", "stderr_tail": ""}

    results = run_checks(smoke_check_commands(python="python"), repo_root=REPO, runner=runner)
    assert len(results) == 3
    assert all(r["status"] == "PASS" for r in results)
    packet = build_fast_ci_receipt(
        repo_root=REPO,
        commit_sha="c",
        origin_main_sha="c",
        execute_smoke=True,
        runner=runner,
    )
    assert packet["status"] == "PASS"
    assert packet["mode"] == "smoke_execute"


def test_fast_ci_writer(tmp_path: Path):
    packet = build_fast_ci_receipt(
        repo_root=REPO,
        commit_sha="c",
        origin_main_sha="c",
        check_results=[
            {
                "name": "x",
                "command": ["true"],
                "required": True,
                "exit_code": 0,
                "status": "PASS",
            }
        ],
    )
    target = tmp_path / "fast_ci.latest.json"
    write_fast_ci_receipt(target, packet)
    assert json.loads(target.read_text(encoding="utf-8"))["status"] == "PASS"


def test_cli_os_main_audit(capsys):
    code = main(["os", "main-audit"])
    # Local worktree may be dirty with untracked dirs; command should still emit JSON.
    out = json.loads(capsys.readouterr().out)
    assert "main_cleanliness" in out
    assert "fast_ci" in out
    assert out["advisory_only"] is True
    assert out["main_cleanliness"]["schema_version"] == "MainCleanlinessReceipt.v0"
    assert out["fast_ci"]["schema_version"] == "FastCiReceipt.v0"
    assert code in {0, 1, 2}
