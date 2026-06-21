from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.codegen.fixture_validation import validate_shadow_replay_fixtures
from core.codegen.meta_gate import build_meta_gate_review

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = (
    "tests/fixtures/codegen/shadow_replay_fixture_golden.v1.json",
    "tests/fixtures/codegen/shadow_replay_fixture_meta_gate.v1.json",
)
ENVELOPE_ID = "e" * 64


def test_meta_gate_review_holds_for_operator_after_fixture_summary() -> None:
    summary = validate_shadow_replay_fixtures(FIXTURES, repo_root=REPO_ROOT)
    review = build_meta_gate_review(
        summary,
        reviewed_envelope_id=ENVELOPE_ID,
        timestamp="2026-06-21T00:00:00Z",
    )

    assert review["status"] == "META_GATE_REVIEW_HELD_FOR_OPERATOR"
    assert review["promotion_allowed"] is False
    assert review["operator_gate_required"] is True
    assert review["execution_authority"] is False
    assert review["seal"]["recommendation"] == "HOLD_FOR_OPERATOR"
    assert review["seal"]["promotion_allowed"] is False
    assert review["canonical_hash"] == canonical_hash(
        {key: value for key, value in review.items() if key != "canonical_hash"}
    )


def test_meta_gate_review_blocks_failed_fixture_summary() -> None:
    failed_summary = {
        "schema_version": "CodegenFixtureValidationSummary.v1",
        "status": "FIXTURE_VALIDATION_SUMMARY_FAILED",
        "fixture_count": 1,
        "passed_count": 0,
        "failed_count": 1,
    }
    review = build_meta_gate_review(
        failed_summary,
        reviewed_envelope_id=ENVELOPE_ID,
        timestamp="2026-06-21T00:00:00Z",
    )

    assert review["status"] == "META_GATE_REVIEW_BLOCKED_BY_REPLAY"
    assert review["seal"]["recommendation"] == "BLOCK_REPLAY_FAILURE"
    assert review["recommended_next"] == "REPAIR_FIXTURE_VALIDATION_BEFORE_META_GATE"
