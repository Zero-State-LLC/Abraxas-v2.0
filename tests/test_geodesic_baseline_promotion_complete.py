from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.geodesic_baseline_promotion_complete import (
    COMPLETE_ID,
    COMPLETE_STATUS,
    COMPLETE_STAGE,
    SCHEMA_VERSION,
    SOURCE_PROMOTION_REVIEW_HASH,
    SOURCE_BASELINE_PACK_HASH,
    SOURCE_GEODESIC_CLOSURE_HASH,
    SOURCE_BASELINE_PROMOTION_DECISION_HASH,
    GeodesicBaselinePromotionCompleteError,
    build_geodesic_baseline_promotion_complete,
    validate_geodesic_baseline_promotion_complete,
)
from core.canonical.json import canonical_hash


def _build() -> dict:
    return build_geodesic_baseline_promotion_complete()


def test_builds_without_error() -> None:
    doc = _build()
    assert doc["complete_status"] == COMPLETE_STATUS


def test_schema_version() -> None:
    assert _build()["schema_version"] == SCHEMA_VERSION


def test_complete_id() -> None:
    assert _build()["complete_id"] == COMPLETE_ID


def test_complete_stage() -> None:
    assert _build()["complete_stage"] == COMPLETE_STAGE


def test_intended_lane() -> None:
    assert _build()["intended_lane"] == "SHADOW"


def test_source_hashes_present() -> None:
    doc = _build()
    assert doc["source_promotion_review_hash"] == SOURCE_PROMOTION_REVIEW_HASH
    assert doc["source_baseline_pack_hash"] == SOURCE_BASELINE_PACK_HASH
    assert doc["source_geodesic_closure_hash"] == SOURCE_GEODESIC_CLOSURE_HASH
    assert doc["source_baseline_promotion_decision_hash"] == SOURCE_BASELINE_PROMOTION_DECISION_HASH


def test_deterministic() -> None:
    a = _build()
    b = _build()
    assert a["canonical_hash"] == b["canonical_hash"]


def test_canonical_hash_valid() -> None:
    doc = _build()
    h = doc["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in doc.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_validate_passes() -> None:
    validate_geodesic_baseline_promotion_complete(_build())


def test_phase_summary_all_checks_passed() -> None:
    ps = _build()["phase_summary"]
    assert ps["all_promotion_checks_passed"] is True
    assert ps["geodesic_at_shadow_stub"] is True
    assert ps["parity_achieved"] is True
    assert ps["promotion_review_on_main"] is True
    assert ps["baseline_pack_updated_on_main"] is True


def test_parity_confirmation_all_three_shadow() -> None:
    pc = _build()["parity_confirmation"]
    for op in ("GEODESIC", "WASSERSTEIN", "CHAMFER_DISTANCE"):
        assert pc[op]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR", op
        assert pc[op]["expected_computation_status"] == "SHADOW_STUB_ONLY", op


def test_parity_confirmation_passed() -> None:
    assert _build()["parity_confirmation"]["parity_confirmation_passed"] is True


def test_parity_shadow_stub_operators_set() -> None:
    shadow = _build()["parity_confirmation"]["shadow_stub_operators"]
    assert set(shadow) == {"WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC"}


def test_provenance_chain_all_sources_verified() -> None:
    pc = _build()["provenance_chain"]
    assert pc["all_sources_verified"] is True
    assert pc["geodesic_baseline_promotion_review_hash"] == SOURCE_PROMOTION_REVIEW_HASH
    assert pc["metric_operator_baseline_test_vector_pack_hash"] == SOURCE_BASELINE_PACK_HASH
    assert pc["geodesic_computation_operator_closure_hash"] == SOURCE_GEODESIC_CLOSURE_HASH
    assert pc["geodesic_baseline_promotion_decision_hash"] == SOURCE_BASELINE_PROMOTION_DECISION_HASH


def test_authority_locks_true_flags() -> None:
    locks = _build()["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["baseline_promotion_authorized"] is True
    assert locks["baseline_promotion_complete"] is True


def test_authority_locks_false_flags() -> None:
    locks = _build()["authority_locks"]
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        assert locks[flag] is False, f"authority_locks.{flag} must be False"


def test_blocked_scopes_all_false() -> None:
    bs = _build()["blocked_scopes"]
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        assert bs[flag] is False, f"blocked_scopes.{flag} must be False"


def test_recommended_next_step() -> None:
    assert _build()["recommended_next_step"] == "GEODESIC_SHADOW_STUB_PHASE_CLOSED"


def test_validate_wrong_schema_version() -> None:
    doc = dict(_build())
    doc["schema_version"] = "WRONG"
    with pytest.raises(GeodesicBaselinePromotionCompleteError, match="schema_version"):
        validate_geodesic_baseline_promotion_complete(doc)


def test_validate_wrong_complete_status() -> None:
    doc = dict(_build())
    doc["complete_status"] = "WRONG"
    with pytest.raises(GeodesicBaselinePromotionCompleteError, match="complete_status"):
        validate_geodesic_baseline_promotion_complete(doc)


def test_validate_authority_lock_flip() -> None:
    doc = dict(_build())
    doc["authority_locks"] = dict(doc["authority_locks"])
    doc["authority_locks"]["execution_authority"] = True
    with pytest.raises(GeodesicBaselinePromotionCompleteError, match="execution_authority"):
        validate_geodesic_baseline_promotion_complete(doc)


def test_validate_parity_wrong_vector_type() -> None:
    doc = dict(_build())
    pc = dict(doc["parity_confirmation"])
    pc["GEODESIC"] = dict(pc["GEODESIC"])
    pc["GEODESIC"]["vector_type"] = "VALID_METADATA_VECTOR"
    doc["parity_confirmation"] = pc
    with pytest.raises(GeodesicBaselinePromotionCompleteError, match="GEODESIC.vector_type"):
        validate_geodesic_baseline_promotion_complete(doc)


def test_artifact_file_written_by_runner() -> None:
    path = Path("out/metric_operator/geodesic_baseline_promotion_complete_001.latest.json")
    if not path.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(path.read_text())
    assert data["complete_status"] == COMPLETE_STATUS
    assert data["schema_version"] == SCHEMA_VERSION
    assert isinstance(data["canonical_hash"], str) and len(data["canonical_hash"]) == 64
