from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_cross_operator_parity_receipt import (
    build_metric_operator_cross_operator_parity_receipt,
    default_governance_flags,
    default_output_contract,
    three_operator_default_parity_dimensions,
)
from core.metric_operator_registry_stabilization import (
    build_metric_operator_registry_stabilization,
    default_governance_flags as stab_governance_flags,
    default_output_contract as stab_output_contract,
    three_operator_default_operator_entries,
)
from core.metric_operator_frontier_recommendation import (
    build_metric_operator_frontier_recommendation,
    default_governance_flags as front_governance_flags,
    default_output_contract as front_output_contract,
    three_operator_default_ranked_options,
)
from core.canonical.json import canonical_hash

SHADOW_OPS = {"WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC"}
NOT_IMPL_OPS = {
    "NORM_GEOMETRY", "TRANSPORT", "HYPERVECTOR_BINDING",
    "RESERVOIR_STATE_SPACE", "COUNTERFACTUAL_DIFFUSION", "HEAVY_TAIL",
    "HYSTERESIS", "STOCHASTIC_GEOMETRY", "TOPOLOGICAL_PRIMITIVES",
}


def _parity_payload() -> dict:
    return {
        "receipt_id": "metric_operator_cross_operator_parity_receipt_002",
        "parity_status": "PARITY_CONFIRMED",
        "operators_compared": ["CHAMFER_DISTANCE", "GEODESIC", "WASSERSTEIN"],
        "parity_dimensions": three_operator_default_parity_dimensions(),
        "output_contract": default_output_contract(),
        "governance_flags": default_governance_flags(),
        "provenance": {
            "source": "THREE_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": "THREE_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_001",
            "evidence_refs": [
                "GeodesicBaselinePromotionComplete.v1:geodesic_baseline_promotion_complete_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_cross_operator_parity_receipt.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _stab_payload() -> dict:
    return {
        "stabilization_id": "metric_operator_registry_stabilization_002",
        "title": "Metric Operator Registry Stabilization — Three-operator SHADOW_STUB_ONLY parity confirmed",
        "stabilization_status": "STABLE",
        "operator_entries": three_operator_default_operator_entries(),
        "source_refs": [
            "GeodesicBaselinePromotionComplete.v1:geodesic_baseline_promotion_complete_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
        ],
        "output_contract": stab_output_contract(),
        "governance_flags": stab_governance_flags(),
        "provenance": {
            "source": "THREE_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": "THREE_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_001",
            "evidence_refs": [
                "GeodesicBaselinePromotionComplete.v1:geodesic_baseline_promotion_complete_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_registry_stabilization.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _frontier_payload() -> dict:
    return {
        "recommendation_id": "metric_operator_frontier_recommendation_002",
        "recommendation_status": "ADVISORY_ONLY",
        "ranked_options": three_operator_default_ranked_options(),
        "recommended_next_step": "G_SEALED_PAUSE",
        "required_operator_decision": True,
        "stop_boundary_reason": (
            "Three-operator SHADOW_STUB_ONLY parity achieved. "
            "All advancement requires explicit operator instruction."
        ),
        "output_contract": front_output_contract(),
        "governance_flags": front_governance_flags(),
        "provenance": {
            "source": "THREE_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": "THREE_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_001",
            "evidence_refs": [
                "GeodesicBaselinePromotionComplete.v1:geodesic_baseline_promotion_complete_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_frontier_recommendation.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ── Parity Receipt 002 ────────────────────────────────────────────────────────

def test_three_operator_parity_dimensions_count() -> None:
    dims = three_operator_default_parity_dimensions()
    assert len(dims) == 8


def test_three_operator_parity_dimensions_all_confirmed() -> None:
    dims = three_operator_default_parity_dimensions()
    for d in dims:
        assert d["parity_confirmed"] is True, d["dimension_id"]


def test_three_operator_parity_dimensions_cover_geodesic() -> None:
    dims = three_operator_default_parity_dimensions()
    for d in dims:
        assert "GEODESIC" in d["observed_values"], d["dimension_id"]


def test_three_operator_parity_dimensions_computation_phase_present() -> None:
    dims = three_operator_default_parity_dimensions()
    ids = {d["dimension_id"] for d in dims}
    assert "dim-008-computation-phase" in ids


def test_parity_receipt_002_builds() -> None:
    receipt = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    assert receipt["parity_status"] == "PARITY_CONFIRMED"
    assert set(receipt["operators_compared"]) == SHADOW_OPS


def test_parity_receipt_002_deterministic() -> None:
    a = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    b = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_parity_receipt_002_hash_valid() -> None:
    receipt = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    h = receipt["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in receipt.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_parity_receipt_002_governance_all_false() -> None:
    receipt = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    for flag, val in receipt["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── Registry Stabilization 002 ────────────────────────────────────────────────

def test_three_operator_default_entries_shadow_ops() -> None:
    entries = three_operator_default_operator_entries()
    by_id = {e["operator_id"]: e for e in entries}
    for op in SHADOW_OPS:
        assert by_id[op]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR", op
        assert by_id[op]["expected_computation_status"] == "SHADOW_STUB_ONLY", op


def test_three_operator_default_entries_not_impl_ops() -> None:
    entries = three_operator_default_operator_entries()
    by_id = {e["operator_id"]: e for e in entries}
    for op in NOT_IMPL_OPS:
        assert by_id[op]["vector_type"] == "VALID_METADATA_VECTOR", op
        assert by_id[op]["expected_computation_status"] == "NOT_IMPLEMENTED", op


def test_three_operator_default_entries_all_blocked() -> None:
    entries = three_operator_default_operator_entries()
    for e in entries:
        assert e["execution_blocked"] is True, e["operator_id"]
        assert e["metric_emission_blocked"] is True, e["operator_id"]


def test_three_operator_default_entries_geodesic_shadow() -> None:
    entries = three_operator_default_operator_entries()
    geo = next(e for e in entries if e["operator_id"] == "GEODESIC")
    assert geo["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert geo["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_registry_stabilization_002_builds() -> None:
    stab = build_metric_operator_registry_stabilization(_stab_payload())
    assert stab["stabilization_status"] == "STABLE"
    assert stab["stabilization_id"] == "metric_operator_registry_stabilization_002"


def test_registry_stabilization_002_deterministic() -> None:
    a = build_metric_operator_registry_stabilization(_stab_payload())
    b = build_metric_operator_registry_stabilization(_stab_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_registry_stabilization_002_hash_valid() -> None:
    stab = build_metric_operator_registry_stabilization(_stab_payload())
    h = stab["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in stab.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_registry_stabilization_002_geodesic_shadow() -> None:
    stab = build_metric_operator_registry_stabilization(_stab_payload())
    by_id = {e["operator_id"]: e for e in stab["operator_entries"]}
    assert by_id["GEODESIC"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert by_id["GEODESIC"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_registry_stabilization_002_governance_all_false() -> None:
    stab = build_metric_operator_registry_stabilization(_stab_payload())
    for flag, val in stab["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── Frontier Recommendation 002 ───────────────────────────────────────────────

def test_three_operator_ranked_options_count() -> None:
    opts = three_operator_default_ranked_options()
    assert len(opts) == 6


def test_three_operator_ranked_options_rank1_sealed_pause() -> None:
    opts = three_operator_default_ranked_options()
    r1 = next(o for o in opts if o["rank"] == 1)
    assert r1["option_id"] == "G_SEALED_PAUSE"
    assert r1["authority_posture"] == "ADVISORY_ONLY"
    assert r1["requires_operator_instruction"] is False


def test_three_operator_ranked_options_rank2_fourth_operator() -> None:
    opts = three_operator_default_ranked_options()
    r2 = next(o for o in opts if o["rank"] == 2)
    assert r2["option_id"] == "B_FOURTH_OPERATOR_SELECTION"
    assert r2["authority_posture"] == "ADVISORY_ONLY"


def test_three_operator_ranked_options_blocked_options() -> None:
    opts = three_operator_default_ranked_options()
    blocked = [o for o in opts if o["authority_posture"] == "BLOCKED"]
    blocked_ids = {o["option_id"] for o in blocked}
    assert "C_METRIC_EMISSION_AUTHORIZATION_REVIEW" in blocked_ids
    assert "E_P43_SURFACE_LANE_READINESS" in blocked_ids


def test_three_operator_ranked_options_unique_ranks() -> None:
    opts = three_operator_default_ranked_options()
    ranks = [o["rank"] for o in opts]
    assert len(ranks) == len(set(ranks))


def test_frontier_recommendation_002_builds() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    assert rec["recommendation_status"] == "ADVISORY_ONLY"
    assert rec["recommendation_id"] == "metric_operator_frontier_recommendation_002"
    assert rec["recommended_next_step"] == "G_SEALED_PAUSE"


def test_frontier_recommendation_002_deterministic() -> None:
    a = build_metric_operator_frontier_recommendation(_frontier_payload())
    b = build_metric_operator_frontier_recommendation(_frontier_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_frontier_recommendation_002_hash_valid() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    h = rec["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in rec.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_frontier_recommendation_002_governance_all_false() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    for flag, val in rec["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_frontier_recommendation_002_registry_hardening_present() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    ids = {o["option_id"] for o in rec["ranked_options"]}
    assert "H_REGISTRY_HARDENING" in ids


# ── Artifact file presence (post-runner) ─────────────────────────────────────

def test_parity_receipt_002_file_written() -> None:
    p = Path("out/metric_operator/metric_operator_cross_operator_parity_receipt_002.latest.json")
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["parity_status"] == "PARITY_CONFIRMED"
    assert set(data["operators_compared"]) == SHADOW_OPS


def test_registry_stabilization_002_file_written() -> None:
    p = Path("out/metric_operator/metric_operator_registry_stabilization_002.latest.json")
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["stabilization_status"] == "STABLE"
    by_id = {e["operator_id"]: e for e in data["operator_entries"]}
    assert by_id["GEODESIC"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_frontier_recommendation_002_file_written() -> None:
    p = Path("out/metric_operator/metric_operator_frontier_recommendation_002.latest.json")
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["recommendation_status"] == "ADVISORY_ONLY"
    assert data["recommended_next_step"] == "G_SEALED_PAUSE"
