from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.pr_644_stack_review_receipt import build_pr_644_stack_review_receipt
from scripts import run_pr_644_stack_review_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/operator_review/pr_644_stack_review_receipt.v1.schema.json"


def test_pr_644_stack_review_receipt_holds_for_pending_codeql() -> None:
    packet = build_pr_644_stack_review_receipt(REPO_ROOT)

    assert packet["receipt_status"] == "PR_644_STACK_REVIEW_HELD_FOR_CHECK_COMPLETION"
    assert packet["pr_number"] == 644
    assert packet["state"] == "OPEN"
    assert packet["is_draft"] is True
    assert packet["mergeable"] == "MERGEABLE"
    assert packet["check_summary"]["total_checks"] == 4
    assert packet["check_summary"]["successful_checks"] == 1
    assert packet["check_summary"]["pending_checks"] == 3
    assert "checks_pending" in packet["blockers"]
    assert "operator_review_not_observed" in packet["blockers"]


def test_pr_644_stack_review_receipt_denies_authority() -> None:
    packet = build_pr_644_stack_review_receipt(REPO_ROOT)

    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_merge"] is False
    assert packet["safe_to_mark_ready_for_review"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["merge_authority"] is False
    assert packet["draft_state_mutation_allowed"] is False
    assert packet["auto_approval_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_pr_644_stack_review_receipt_schema_and_hash_are_stable() -> None:
    packet = build_pr_644_stack_review_receipt(REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_pr_644_stack_review_receipt_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/operator_review/pr_644_stack_review_receipt_001.latest.json"
    out_md = out_json.with_suffix(".md")

    first = run_pr_644_stack_review_receipt.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_pr_644_stack_review_receipt.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
    assert first_md.startswith("# PR 644 Stack Review Receipt\n")
