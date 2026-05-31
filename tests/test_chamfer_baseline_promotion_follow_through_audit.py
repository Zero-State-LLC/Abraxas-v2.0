"""Tests: ChamferBaselinePromotionFollowThroughAudit.v1 artifact."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_baseline_promotion_follow_through_audit import (
    AUDIT_ID,
    AUDIT_STATUS,
    CURRENT_PACK_HASH,
    OPERATOR_ID,
    SCHEMA_VERSION,
    ChamferBaselinePromotionFollowThroughAuditError,
    build_chamfer_baseline_promotion_follow_through_audit,
    validate_chamfer_baseline_promotion_follow_through_audit,
)
from core.canonical.json import canonical_hash

OUT_PATH = Path(
    "out/metric_operator"
    "/chamfer_baseline_promotion_follow_through_audit_001.latest.json"
)


@pytest.fixture(scope="module")
def audit() -> dict:
    return build_chamfer_baseline_promotion_follow_through_audit()


def test_audit_status(audit: dict) -> None:
    assert audit["audit_status"] == AUDIT_STATUS


def test_audit_id(audit: dict) -> None:
    assert audit["audit_id"] == AUDIT_ID


def test_schema_version(audit: dict) -> None:
    assert audit["schema_version"] == SCHEMA_VERSION


def test_operator_id(audit: dict) -> None:
    assert audit["operator_id"] == OPERATOR_ID


def test_canonical_hash_present_and_valid(audit: dict) -> None:
    h = audit.get("canonical_hash", "")
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_recomputes(audit: dict) -> None:
    preimage = {k: v for k, v in audit.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == audit["canonical_hash"]


def test_authority_locks(audit: dict) -> None:
    al = audit["authority_locks"]
    assert al["advisory_only"] is True
    assert al["audit_only"] is True
    assert al["canon_promotion"] is False
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_lanes"] is False
    assert al["production_activation"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False


def test_recommended_next_step(audit: dict) -> None:
    assert audit["recommended_next_step"] == "CHAMFER_BASELINE_PROMOTION_REVIEW"


def test_intended_lane(audit: dict) -> None:
    assert audit["intended_lane"] == "BASELINE_PROMOTION_FOLLOW_THROUGH"


def test_current_projection_state(audit: dict) -> None:
    s = audit["current_chamfer_projection_state"]
    assert s["status"] == "READY"
    assert s["completion_pct"] == 95
    assert s["all_computation_chain_artifacts_present"] is True
    assert s["cap_reason"] == "promotion_key_not_wired_in_OPERATOR_DEFS"


def test_pack_state_already_promoted(audit: dict) -> None:
    p = audit["current_chamfer_pack_state"]
    assert p["chamfer_already_promoted_in_pack"] is True
    assert p["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert p["expected_computation_status"] == "SHADOW_STUB_ONLY"
    assert p["pack_canonical_hash"] == CURRENT_PACK_HASH


def test_existing_artifact_inventory(audit: dict) -> None:
    inv = audit["existing_chamfer_artifact_inventory"]
    assert inv["present_count"] == 10
    assert inv["absent_count"] == 2
    present_ids = [a["artifact_id"] for a in inv["present_artifacts"]]
    assert "chamfer_distance_computation_receipt_001" in present_ids
    assert "chamfer_distance_computation_complete_review_001" in present_ids
    assert "chamfer_expected_values_addition_receipt_001" in present_ids


def test_absent_artifacts(audit: dict) -> None:
    inv = audit["existing_chamfer_artifact_inventory"]
    absent_ids = [a["artifact_id"] for a in inv["absent_artifacts"]]
    assert "chamfer_baseline_promotion_review_001" in absent_ids
    assert "chamfer_baseline_promotion_complete_001" in absent_ids


def test_missing_artifact_analysis(audit: dict) -> None:
    ma = audit["missing_artifact_analysis"]
    assert ma["chamfer_baseline_promotion_review_001"] == "ABSENT"
    assert ma["chamfer_baseline_promotion_complete_001"] == "ABSENT"
    assert ma["pack_re_promotion_required"] is False
    assert ma["wiring_update_required"] is True


def test_promotion_chain_state(audit: dict) -> None:
    pcs = audit["promotion_chain_state"]
    assert pcs["computation_chain_closed"] is True
    assert pcs["pack_promoted"] is True
    assert pcs["baseline_promotion_review_present"] is False
    assert pcs["baseline_promotion_complete_present"] is False
    assert pcs["governance_closure_chain_complete"] is False
    assert pcs["chain_complete"] is False
    assert pcs["blocking_step"] == "chamfer_baseline_promotion_review_001"


def test_projection_wiring_state(audit: dict) -> None:
    ws = audit["projection_wiring_state"]
    assert ws["promotion_key"] is None
    assert ws["wiring_complete"] is False
    assert ws["projection_cap_at_current_state"] == 95


def test_lawful_next_step_no_pack_rerun(audit: dict) -> None:
    ln = audit["lawful_next_step_determination"]
    assert ln["no_pack_rerun_needed"] is True
    assert ln["no_fixture_mutation_needed"] is True
    assert ln["no_computation_rerun_needed"] is True


def test_blocked_scope_review(audit: dict) -> None:
    bs = audit["blocked_scope_review"]
    assert bs["all_scopes_remain_blocked"] is True
    assert bs["metric_emission"] == "BLOCKED"
    assert bs["forecast_influence"] == "BLOCKED"
    assert bs["p43_lanes"] == "BLOCKED"
    assert bs["research_canary_guardrail"] == "ACTIVE"


def test_validate_passes(audit: dict) -> None:
    validate_chamfer_baseline_promotion_follow_through_audit(audit)


def test_validate_wrong_status_raises(audit: dict) -> None:
    bad = {**audit, "audit_status": "WRONG"}
    with pytest.raises(ChamferBaselinePromotionFollowThroughAuditError):
        validate_chamfer_baseline_promotion_follow_through_audit(bad)


def test_validate_wrong_hash_raises(audit: dict) -> None:
    bad = {**audit, "canonical_hash": "a" * 64}
    with pytest.raises(ChamferBaselinePromotionFollowThroughAuditError):
        validate_chamfer_baseline_promotion_follow_through_audit(bad)


def test_on_disk_artifact_matches_build(audit: dict) -> None:
    if not OUT_PATH.exists():
        pytest.skip("on-disk artifact not yet generated; run the runner script first")
    on_disk = json.loads(OUT_PATH.read_text())
    assert on_disk["canonical_hash"] == audit["canonical_hash"]
    assert on_disk["audit_status"] == AUDIT_STATUS
