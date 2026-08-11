"""Tests for Track B full pipeline contract closure."""

from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.track_b_contract_closure import (
    AUTHORITY_LOCKS,
    ISSUE_BY_PIPELINE,
    TRACK_B_PIPELINE_IDS,
    build_track_b_contract_closure_receipt,
    write_track_b_contract_closure_receipt,
)

REPO = Path(".")


def test_track_b_receipt_aligns_all_prabu_slices() -> None:
    receipt = build_track_b_contract_closure_receipt(REPO)

    assert receipt["status"] == "TRACK_B_CONTRACT_CLOSURE_ALIGNED_ADVISORY_ONLY"
    assert receipt["coordination"]["issue_author"] == "prabu-openclaw"
    assert receipt["coordination"]["writeback_performed"] is False
    assert receipt["summary"] == {
        "target_count": 8,
        "aligned_count": 8,
        "not_aligned_count": 0,
        "matrix_expected_alignment": "ALIGNED",
    }
    assert [row["pipeline_id"] for row in receipt["contract_closures"]] == TRACK_B_PIPELINE_IDS
    assert receipt["leaf_issues"] == [ISSUE_BY_PIPELINE[pipeline_id] for pipeline_id in TRACK_B_PIPELINE_IDS]
    assert all(row["alignment"] == "ALIGNED" for row in receipt["contract_closures"])


def test_track_b_receipt_preserves_shadow_advisory_authority() -> None:
    receipt = build_track_b_contract_closure_receipt(REPO)

    assert AUTHORITY_LOCKS and all(value is False for value in receipt["authority_locks"].values())
    assert all(value is False for value in receipt["authority"].values())
    for row in receipt["contract_closures"]:
        assert row["authority_locked"] is True
        assert all(value is False for value in row["authority"].values())
        assert "SHADOW/advisory-only" in row["operator_posture"]
        assert "hold" in row["final_state_policy"]
        assert "eligible_for_operator_review" in row["final_state_policy"]
        assert not row["missing_required"]


def test_track_b_receipt_canonical_hash_is_stable() -> None:
    receipt = build_track_b_contract_closure_receipt(REPO)
    body = {key: value for key, value in receipt.items() if key != "canonical_hash"}
    assert receipt["canonical_hash"] == canonical_hash(body)


def test_track_b_runner_writes_receipt(tmp_path: Path) -> None:
    out = tmp_path / "track_b.latest.json"
    receipt = write_track_b_contract_closure_receipt(REPO, out)
    assert out.exists()
    assert receipt["status"] == "TRACK_B_CONTRACT_CLOSURE_ALIGNED_ADVISORY_ONLY"
