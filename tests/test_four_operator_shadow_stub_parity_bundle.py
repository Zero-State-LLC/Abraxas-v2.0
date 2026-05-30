from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_cross_operator_parity_receipt import (
    build_metric_operator_cross_operator_parity_receipt,
    default_governance_flags,
    default_output_contract,
    four_operator_default_parity_dimensions,
)
from core.metric_operator_registry_stabilization import (
    build_metric_operator_registry_stabilization,
    default_governance_flags as stab_governance_flags,
    default_output_contract as stab_output_contract,
    four_operator_default_operator_entries,
)
from core.metric_operator_frontier_recommendation import (
    build_metric_operator_frontier_recommendation,
    default_governance_flags as front_governance_flags,
    default_output_contract as front_output_contract,
    four_operator_post_norm_geometry_ranked_options,
)
from core.canonical.json import canonical_hash

SHADOW_OPS   = {"WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY"}
NOT_IMPL_OPS = {
    "TRANSPORT", "HYPERVECTOR_BINDING", "RESERVOIR_STATE_SPACE",
    "COUNTERFACTUAL_DIFFUSION", "HEAVY_TAIL", "HYSTERESIS",
    "STOCHASTIC_GEOMETRY", "TOPOLOGICAL_PRIMITIVES",
}
PATCH_ID = "FOUR_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_001"


def _parity_payload() -> dict:
    return {
        "receipt_id": "metric_operator_cross_operator_parity_receipt_003",
        "parity_status": "PARITY_CONFIRMED",
        "operators_compared": ["CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY", "WASSERSTEIN"],
        "parity_dimensions": four_operator_default_parity_dimensions(),
        "output_contract": default_output_contract(),
        "governance_flags": default_governance_flags(),
        "provenance": {
            "source": "FOUR_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "NormGeometryBaselinePromotionComplete.v1:norm_geometry_baseline_promotion_complete_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_cross_operator_parity_receipt.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _stab_payload() -> dict:
    return {
        "stabilization_id": "metric_operator_registry_stabilization_003",
        "title": "Metric Operator Registry Stabilization — Four-operator SHADOW_STUB_ONLY parity confirmed",
        "stabilization_status": "STABLE",
        "operator_entries": four_operator_default_operator_entries(),
        "source_refs": [
            "NormGeometryBaselinePromotionComplete.v1:norm_geometry_baseline_promotion_complete_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
        ],
        "output_contract": stab_output_contract(),
        "governance_flags": stab_governance_flags(),
        "provenance": {
            "source": "FOUR_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "NormGeometryBaselinePromotionComplete.v1:norm_geometry_baseline_promotion_complete_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_registry_stabilization.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _frontier_payload() -> dict:
    return {
        "recommendation_id": "metric_operator_frontier_recommendation_005",
        "recommendation_status": "ADVISORY_ONLY",
        "ranked_options": four_operator_post_norm_geometry_ranked_options(),
        "recommended_next_step": "G_SEALED_PAUSE",
        "required_operator_decision": True,
        "stop_boundary_reason": (
            "Four-operator SHADOW_STUB_ONLY parity achieved. "
            "All advancement requires explicit operator instruction."
        ),
        "output_contract": front_output_contract(),
        "governance_flags": front_governance_flags(),
        "provenance": {
            "source": "FOUR_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "NormGeometryBaselinePromotionComplete.v1:norm_geometry_baseline_promotion_complete_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_frontier_recommendation.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ── four_operator_default_parity_dimensions ────────────────────────────────────

def test_four_operator_parity_dimensions_count() -> None:
    dims = four_operator_default_parity_dimensions()
    assert len(dims) == 9


def test_four_operator_parity_dimensions_all_confirmed() -> None:
    dims = four_operator_default_parity_dimensions()
    for d in dims:
        assert d["parity_confirmed"] is True, d["dimension_id"]


def test_four_operator_parity_dimensions_cover_norm_geometry() -> None:
    dims = four_operator_default_parity_dimensions()
    for d in dims:
        assert "NORM_GEOMETRY" in d["observed_values"], d["dimension_id"]


def test_four_operator_parity_dimensions_cover_all_shadow_ops() -> None:
    dims = four_operator_default_parity_dimensions()
    for d in dims:
        for op in SHADOW_OPS:
            assert op in d["observed_values"], f"{d['dimension_id']} missing {op}"


def test_four_operator_parity_dimensions_computation_phase_present() -> None:
    dims = four_operator_default_parity_dimensions()
    ids = {d["dimension_id"] for d in dims}
    assert "dim-008-computation-phase" in ids


def test_four_operator_parity_dimensions_baseline_promotion_present() -> None:
    dims = four_operator_default_parity_dimensions()
    ids = {d["dimension_id"] for d in dims}
    assert "dim-009-baseline-promotion" in ids


def test_four_operator_parity_dimensions_baseline_promotion_complete() -> None:
    dims = four_operator_default_parity_dimensions()
    bp = next(d for d in dims if d["dimension_id"] == "dim-009-baseline-promotion")
    for op in SHADOW_OPS:
        assert bp["observed_values"][op] == "COMPLETE", op


def test_four_operator_parity_dimensions_vector_type_shadow_only() -> None:
    dims = four_operator_default_parity_dimensions()
    vt = next(d for d in dims if d["dimension_id"] == "dim-001-vector-type")
    for op in SHADOW_OPS:
        assert vt["observed_values"][op] == "VALID_SHADOW_ONLY_VECTOR", op


def test_four_operator_parity_dimensions_computation_status_shadow_stub() -> None:
    dims = four_operator_default_parity_dimensions()
    cs = next(d for d in dims if d["dimension_id"] == "dim-002-computation-status")
    for op in SHADOW_OPS:
        assert cs["observed_values"][op] == "SHADOW_STUB_ONLY", op


def test_four_operator_parity_dimensions_all_blocked() -> None:
    dims = four_operator_default_parity_dimensions()
    for d in dims:
        if "blocked" in d["dimension_name"]:
            for val in d["observed_values"].values():
                assert val == "BLOCKED", f"{d['dimension_id']}: expected BLOCKED got {val}"


# ── Parity Receipt 003 ─────────────────────────────────────────────────────────

def test_parity_receipt_003_builds() -> None:
    receipt = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    assert receipt["parity_status"] == "PARITY_CONFIRMED"
    assert set(receipt["operators_compared"]) == SHADOW_OPS


def test_parity_receipt_003_receipt_id() -> None:
    receipt = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    assert receipt["receipt_id"] == "metric_operator_cross_operator_parity_receipt_003"


def test_parity_receipt_003_deterministic() -> None:
    a = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    b = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_parity_receipt_003_hash_valid() -> None:
    receipt = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    h = receipt["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in receipt.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_parity_receipt_003_governance_all_false() -> None:
    receipt = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    for flag, val in receipt["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_parity_receipt_003_nine_dimensions() -> None:
    receipt = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    assert len(receipt["parity_dimensions"]) == 9


def test_parity_receipt_003_four_operators_compared() -> None:
    receipt = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    assert len(receipt["operators_compared"]) == 4


def test_parity_receipt_003_output_contract_emits_parity() -> None:
    receipt = build_metric_operator_cross_operator_parity_receipt(_parity_payload())
    assert receipt["output_contract"]["emits_parity_receipt"] is True
    assert receipt["output_contract"]["emits_metric_values"] is False


# ── four_operator_default_operator_entries ─────────────────────────────────────

def test_four_operator_default_entries_shadow_ops() -> None:
    entries = four_operator_default_operator_entries()
    by_id = {e["operator_id"]: e for e in entries}
    for op in SHADOW_OPS:
        assert by_id[op]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR", op
        assert by_id[op]["expected_computation_status"] == "SHADOW_STUB_ONLY", op


def test_four_operator_default_entries_not_impl_ops() -> None:
    entries = four_operator_default_operator_entries()
    by_id = {e["operator_id"]: e for e in entries}
    for op in NOT_IMPL_OPS:
        assert by_id[op]["vector_type"] == "VALID_METADATA_VECTOR", op
        assert by_id[op]["expected_computation_status"] == "NOT_IMPLEMENTED", op


def test_four_operator_default_entries_all_blocked() -> None:
    entries = four_operator_default_operator_entries()
    for e in entries:
        assert e["execution_blocked"] is True, e["operator_id"]
        assert e["metric_emission_blocked"] is True, e["operator_id"]


def test_four_operator_default_entries_norm_geometry_shadow() -> None:
    entries = four_operator_default_operator_entries()
    ng = next(e for e in entries if e["operator_id"] == "NORM_GEOMETRY")
    assert ng["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert ng["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_four_operator_default_entries_transport_cpu_baseline() -> None:
    entries = four_operator_default_operator_entries()
    tr = next(e for e in entries if e["operator_id"] == "TRANSPORT")
    assert tr["expected_computation_status"] == "NOT_IMPLEMENTED"
    assert tr["cpu_baseline_planning_status"] == "CPU_BASELINE_PLANNING_COMPLETE"


def test_four_operator_default_entries_twelve_operators() -> None:
    entries = four_operator_default_operator_entries()
    assert len(entries) == 12


# ── Registry Stabilization 003 ────────────────────────────────────────────────

def test_registry_stabilization_003_builds() -> None:
    stab = build_metric_operator_registry_stabilization(_stab_payload())
    assert stab["stabilization_status"] == "STABLE"
    assert stab["stabilization_id"] == "metric_operator_registry_stabilization_003"


def test_registry_stabilization_003_deterministic() -> None:
    a = build_metric_operator_registry_stabilization(_stab_payload())
    b = build_metric_operator_registry_stabilization(_stab_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_registry_stabilization_003_hash_valid() -> None:
    stab = build_metric_operator_registry_stabilization(_stab_payload())
    h = stab["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in stab.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_registry_stabilization_003_norm_geometry_shadow() -> None:
    stab = build_metric_operator_registry_stabilization(_stab_payload())
    by_id = {e["operator_id"]: e for e in stab["operator_entries"]}
    assert by_id["NORM_GEOMETRY"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert by_id["NORM_GEOMETRY"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_registry_stabilization_003_geodesic_shadow() -> None:
    stab = build_metric_operator_registry_stabilization(_stab_payload())
    by_id = {e["operator_id"]: e for e in stab["operator_entries"]}
    assert by_id["GEODESIC"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert by_id["GEODESIC"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_registry_stabilization_003_all_shadow_ops_confirmed() -> None:
    stab = build_metric_operator_registry_stabilization(_stab_payload())
    by_id = {e["operator_id"]: e for e in stab["operator_entries"]}
    for op in SHADOW_OPS:
        assert by_id[op]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR", op
        assert by_id[op]["expected_computation_status"] == "SHADOW_STUB_ONLY", op


def test_registry_stabilization_003_transport_cpu_baseline() -> None:
    stab = build_metric_operator_registry_stabilization(_stab_payload())
    by_id = {e["operator_id"]: e for e in stab["operator_entries"]}
    assert by_id["TRANSPORT"]["cpu_baseline_planning_status"] == "CPU_BASELINE_PLANNING_COMPLETE"
    assert by_id["TRANSPORT"]["expected_computation_status"] == "NOT_IMPLEMENTED"


def test_registry_stabilization_003_governance_all_false() -> None:
    stab = build_metric_operator_registry_stabilization(_stab_payload())
    for flag, val in stab["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_registry_stabilization_003_title_four_operator() -> None:
    stab = build_metric_operator_registry_stabilization(_stab_payload())
    assert "Four-operator" in stab["title"] or "four-operator" in stab["title"].lower()


# ── four_operator_post_norm_geometry_ranked_options ────────────────────────────

def test_four_operator_ranked_options_count() -> None:
    opts = four_operator_post_norm_geometry_ranked_options()
    assert len(opts) == 6


def test_four_operator_ranked_options_rank1_sealed_pause() -> None:
    opts = four_operator_post_norm_geometry_ranked_options()
    r1 = next(o for o in opts if o["rank"] == 1)
    assert r1["option_id"] == "G_SEALED_PAUSE"
    assert r1["authority_posture"] == "ADVISORY_ONLY"
    assert r1["requires_operator_instruction"] is False


def test_four_operator_ranked_options_rank2_transport_auth() -> None:
    opts = four_operator_post_norm_geometry_ranked_options()
    r2 = next(o for o in opts if o["rank"] == 2)
    assert r2["option_id"] == "K_TRANSPORT_IMPLEMENTATION_AUTHORIZATION"
    assert r2["authority_posture"] == "ADVISORY_ONLY"
    assert r2["requires_operator_instruction"] is True


def test_four_operator_ranked_options_rank3_rank6_selection() -> None:
    opts = four_operator_post_norm_geometry_ranked_options()
    r3 = next(o for o in opts if o["rank"] == 3)
    assert r3["option_id"] == "N_RANK6_OPERATOR_SELECTION"
    assert r3["authority_posture"] == "ADVISORY_ONLY"


def test_four_operator_ranked_options_rank4_registry_hardening() -> None:
    opts = four_operator_post_norm_geometry_ranked_options()
    r4 = next(o for o in opts if o["rank"] == 4)
    assert r4["option_id"] == "M_REGISTRY_HARDENING"
    assert r4["authority_posture"] == "ADVISORY_ONLY"


def test_four_operator_ranked_options_blocked_options() -> None:
    opts = four_operator_post_norm_geometry_ranked_options()
    blocked = {o["option_id"] for o in opts if o["authority_posture"] == "BLOCKED"}
    assert "C_METRIC_EMISSION_AUTHORIZATION_REVIEW" in blocked
    assert "E_P43_SURFACE_LANE_READINESS" in blocked


def test_four_operator_ranked_options_unique_ranks() -> None:
    opts = four_operator_post_norm_geometry_ranked_options()
    ranks = [o["rank"] for o in opts]
    assert len(ranks) == len(set(ranks))


def test_four_operator_ranked_options_no_norm_geometry_auth() -> None:
    opts = four_operator_post_norm_geometry_ranked_options()
    ids = {o["option_id"] for o in opts}
    assert "J_NORM_GEOMETRY_IMPLEMENTATION_AUTHORIZATION" not in ids


# ── Frontier Recommendation 005 ───────────────────────────────────────────────

def test_frontier_recommendation_005_builds() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    assert rec["recommendation_status"] == "ADVISORY_ONLY"
    assert rec["recommendation_id"] == "metric_operator_frontier_recommendation_005"
    assert rec["recommended_next_step"] == "G_SEALED_PAUSE"


def test_frontier_recommendation_005_deterministic() -> None:
    a = build_metric_operator_frontier_recommendation(_frontier_payload())
    b = build_metric_operator_frontier_recommendation(_frontier_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_frontier_recommendation_005_hash_valid() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    h = rec["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in rec.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_frontier_recommendation_005_governance_all_false() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    for flag, val in rec["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_frontier_recommendation_005_required_operator_decision() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    assert rec["required_operator_decision"] is True


def test_frontier_recommendation_005_transport_advisory() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    transport = next(
        (o for o in rec["ranked_options"] if o["option_id"] == "K_TRANSPORT_IMPLEMENTATION_AUTHORIZATION"),
        None,
    )
    assert transport is not None
    assert transport["authority_posture"] == "ADVISORY_ONLY"


def test_frontier_recommendation_005_metric_emission_blocked() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    emission = next(
        o for o in rec["ranked_options"]
        if o["option_id"] == "C_METRIC_EMISSION_AUTHORIZATION_REVIEW"
    )
    assert emission["authority_posture"] == "BLOCKED"


def test_frontier_recommendation_005_p43_blocked() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    p43 = next(
        o for o in rec["ranked_options"]
        if o["option_id"] == "E_P43_SURFACE_LANE_READINESS"
    )
    assert p43["authority_posture"] == "BLOCKED"


def test_frontier_recommendation_005_output_contract_emits_recommendation() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    assert rec["output_contract"]["emits_recommendation"] is True
    assert rec["output_contract"]["emits_metric_values"] is False


# ── Artifact file presence (post-runner) ──────────────────────────────────────

def test_parity_receipt_003_file_written() -> None:
    p = Path("out/metric_operator/metric_operator_cross_operator_parity_receipt_003.latest.json")
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["parity_status"] == "PARITY_CONFIRMED"
    assert set(data["operators_compared"]) == SHADOW_OPS


def test_registry_stabilization_003_file_written() -> None:
    p = Path("out/metric_operator/metric_operator_registry_stabilization_003.latest.json")
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["stabilization_status"] == "STABLE"
    by_id = {e["operator_id"]: e for e in data["operator_entries"]}
    assert by_id["NORM_GEOMETRY"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_frontier_recommendation_005_file_written() -> None:
    p = Path("out/metric_operator/metric_operator_frontier_recommendation_005.latest.json")
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["recommendation_status"] == "ADVISORY_ONLY"
    assert data["recommended_next_step"] == "G_SEALED_PAUSE"
