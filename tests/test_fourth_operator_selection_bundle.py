from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_rank4_candidate_audit import (
    build_metric_operator_rank4_candidate_audit,
    default_candidate_entries,
    default_output_contract as audit_output_contract,
)
from core.metric_operator_rank4_selection_plan import (
    build_metric_operator_rank4_selection_plan,
    default_implementation_gates,
    default_output_contract as plan_output_contract,
)
from core.norm_geometry_distance_implementation_readiness_dossier import (
    REQUIRED_BLOCKED_SCOPES,
    build_norm_geometry_distance_implementation_readiness_dossier,
    default_authority_locks,
    default_blocked_scopes,
    default_output_contract as dossier_output_contract,
)
from core.norm_geometry_test_vector_schema_plan import (
    build_norm_geometry_test_vector_schema_plan,
    default_output_contract as schema_plan_output_contract,
    default_schema_constraints,
    default_schema_layout_plan,
    default_validation_plan,
)
from core.canonical.json import canonical_hash

COMPLETED_OPS = ["CHAMFER_DISTANCE", "GEODESIC", "WASSERSTEIN"]
NOT_IMPL_OPS = {
    "NORM_GEOMETRY", "TRANSPORT", "TOPOLOGICAL_PRIMITIVES", "HEAVY_TAIL",
    "HYSTERESIS", "STOCHASTIC_GEOMETRY", "RESERVOIR_STATE_SPACE",
    "HYPERVECTOR_BINDING", "COUNTERFACTUAL_DIFFUSION",
}
_LOCKED_FALSE = {
    "production_activation": False, "canon_promotion": False,
    "scheduler_mutation": False, "runtime_authority": False,
    "runtime_mutation": False, "forecast_influence": False,
    "execution_authority": False, "token_minting_allowed": False,
    "valid_for_execution": False, "activation_approved": False,
    "authorization_granted": False,
}


def _audit_payload() -> dict:
    return {
        "audit_id": "metric_operator_rank4_candidate_audit_001",
        "audit_status": "RANK4_CANDIDATE_SELECTED",
        "completed_operators": list(COMPLETED_OPS),
        "candidate_entries": default_candidate_entries(),
        "recommended_rank4": "NORM_GEOMETRY",
        "output_contract": audit_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "FOURTH_OPERATOR_SELECTION_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": "FOURTH_OPERATOR_SELECTION_BUNDLE_001",
            "evidence_refs": [
                "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_002",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_rank4_candidate_audit.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _plan_payload() -> dict:
    return {
        "plan_id": "metric_operator_rank4_selection_plan_001",
        "selected_operator_id": "NORM_GEOMETRY",
        "selection_scope": {
            "intended_lane": "SHADOW",
            "selection_family": "RANK4_OPERATOR_SELECTION",
            "selection_stage": "SELECTION_PLAN_ONLY",
        },
        "source_audit_refs": [
            "MetricOperatorRank4CandidateAudit.v1:metric_operator_rank4_candidate_audit_001",
        ],
        "source_registry_stabilization_refs": [
            "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_002",
        ],
        "source_frontier_recommendation_refs": [
            "MetricOperatorFrontierRecommendation.v1:metric_operator_frontier_recommendation_002",
        ],
        "implementation_gates": default_implementation_gates(),
        "output_contract": plan_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "FOURTH_OPERATOR_SELECTION_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": "FOURTH_OPERATOR_SELECTION_BUNDLE_001",
            "evidence_refs": [
                "MetricOperatorRank4CandidateAudit.v1:metric_operator_rank4_candidate_audit_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_rank4_selection_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _dossier_payload() -> dict:
    return {
        "dossier_id": "norm_geometry_distance_implementation_readiness_dossier_001",
        "implementation_scope": "NORM_GEOMETRY_DISTANCE_READINESS_ONLY",
        "output_contract": dossier_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "FOURTH_OPERATOR_SELECTION_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": "FOURTH_OPERATOR_SELECTION_BUNDLE_001",
            "evidence_refs": [
                "MetricOperatorRank4SelectionPlan.v1:metric_operator_rank4_selection_plan_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/norm_geometry_distance_implementation_readiness_dossier.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _schema_plan_payload() -> dict:
    return {
        "plan_id": "norm_geometry_test_vector_schema_plan_001",
        "schema_scope": {
            "schema_family": "MIXED_SCHEMA_PLAN",
            "intended_lane": "SHADOW",
            "schema_stage": "SCHEMA_PLAN_ONLY",
        },
        "source_dossier_refs": [
            "NormGeometryDistanceImplementationReadinessDossier.v1:"
            "norm_geometry_distance_implementation_readiness_dossier_001",
        ],
        "source_metric_registry_refs": [
            "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_002",
        ],
        "source_baseline_vector_pack_refs": [
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
        ],
        "schema_layout_plan": default_schema_layout_plan(),
        "schema_constraints": default_schema_constraints(),
        "validation_plan": default_validation_plan(),
        "output_contract": schema_plan_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "FOURTH_OPERATOR_SELECTION_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": "FOURTH_OPERATOR_SELECTION_BUNDLE_001",
            "evidence_refs": [
                "NormGeometryDistanceImplementationReadinessDossier.v1:"
                "norm_geometry_distance_implementation_readiness_dossier_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/norm_geometry_test_vector_schema_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ── Rank4 Candidate Audit ─────────────────────────────────────────────────────

def test_candidate_entries_count() -> None:
    entries = default_candidate_entries()
    assert len(entries) == 9


def test_candidate_entries_cover_all_not_impl_ops() -> None:
    entries = default_candidate_entries()
    ids = {e["operator_id"] for e in entries}
    assert ids == NOT_IMPL_OPS


def test_candidate_entries_exactly_one_selected() -> None:
    entries = default_candidate_entries()
    selected = [e for e in entries if e["selection_status"] == "SELECTED_RANK4"]
    assert len(selected) == 1


def test_candidate_entries_norm_geometry_selected() -> None:
    entries = default_candidate_entries()
    sel = next(e for e in entries if e["selection_status"] == "SELECTED_RANK4")
    assert sel["operator_id"] == "NORM_GEOMETRY"
    assert sel["composite_rank"] == 1


def test_candidate_entries_norm_geometry_low_risk() -> None:
    entries = default_candidate_entries()
    ng = next(e for e in entries if e["operator_id"] == "NORM_GEOMETRY")
    assert ng["numerical_stability_risk"] == "LOW"
    assert ng["schema_complexity"] == "LOW"
    assert ng["deterministic_fixture_feasibility"] == "HIGH"


def test_candidate_entries_rejected_have_reason() -> None:
    entries = default_candidate_entries()
    for e in entries:
        if e["selection_status"] == "REJECTED":
            assert "rejection_reason" in e, e["operator_id"]


def test_rank4_audit_builds() -> None:
    audit = build_metric_operator_rank4_candidate_audit(_audit_payload())
    assert audit["audit_status"] == "RANK4_CANDIDATE_SELECTED"
    assert audit["recommended_rank4"] == "NORM_GEOMETRY"
    assert sorted(audit["completed_operators"]) == sorted(COMPLETED_OPS)


def test_rank4_audit_deterministic() -> None:
    a = build_metric_operator_rank4_candidate_audit(_audit_payload())
    b = build_metric_operator_rank4_candidate_audit(_audit_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_rank4_audit_hash_valid() -> None:
    audit = build_metric_operator_rank4_candidate_audit(_audit_payload())
    h = audit["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in audit.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_rank4_audit_governance_all_false() -> None:
    audit = build_metric_operator_rank4_candidate_audit(_audit_payload())
    for flag, val in audit["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── Rank4 Selection Plan ──────────────────────────────────────────────────────

def test_rank4_selection_plan_builds() -> None:
    plan = build_metric_operator_rank4_selection_plan(_plan_payload())
    assert plan["selected_operator_id"] == "NORM_GEOMETRY"
    assert plan["selection_scope"]["selection_stage"] == "SELECTION_PLAN_ONLY"


def test_rank4_selection_plan_implementation_gates() -> None:
    plan = build_metric_operator_rank4_selection_plan(_plan_payload())
    gates = plan["implementation_gates"]
    assert gates["implementation_blocked"] is True
    assert gates["fixture_creation_blocked"] is True
    assert gates["planning_only"] is True


def test_rank4_selection_plan_deterministic() -> None:
    a = build_metric_operator_rank4_selection_plan(_plan_payload())
    b = build_metric_operator_rank4_selection_plan(_plan_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_rank4_selection_plan_hash_valid() -> None:
    plan = build_metric_operator_rank4_selection_plan(_plan_payload())
    h = plan["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in plan.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_rank4_selection_plan_governance_all_false() -> None:
    plan = build_metric_operator_rank4_selection_plan(_plan_payload())
    for flag, val in plan["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_rank4_selection_plan_emits_selection_metadata_only() -> None:
    plan = build_metric_operator_rank4_selection_plan(_plan_payload())
    oc = plan["output_contract"]
    assert oc["emits_selection_metadata"] is True
    assert oc["emits_metric_values"] is False
    assert oc["emits_authority_tokens"] is False


# ── Norm Geometry Readiness Dossier ──────────────────────────────────────────

def test_dossier_default_blocked_scopes_complete() -> None:
    blocked = set(default_blocked_scopes())
    assert REQUIRED_BLOCKED_SCOPES.issubset(blocked)


def test_dossier_default_authority_locks() -> None:
    locks = default_authority_locks()
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["readiness_dossier_only"] is True
    assert locks["norm_geometry_computation_authorized"] is False
    assert locks["emits_metric_values"] is False
    assert locks["execution_authority"] is False


def test_norm_geometry_dossier_builds() -> None:
    dossier = build_norm_geometry_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    assert dossier["selected_operator"] == "NORM_GEOMETRY"
    assert dossier["dossier_status"] == "NORM_GEOMETRY_READINESS_DOSSIER_DEFINED"
    assert dossier["intended_lane"] == "SHADOW"
    assert dossier["readiness_scope"] == "IMPLEMENTATION_READINESS_ONLY"


def test_norm_geometry_dossier_deterministic() -> None:
    a = build_norm_geometry_distance_implementation_readiness_dossier(_dossier_payload())
    b = build_norm_geometry_distance_implementation_readiness_dossier(_dossier_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_norm_geometry_dossier_hash_valid() -> None:
    dossier = build_norm_geometry_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    h = dossier["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in dossier.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_norm_geometry_dossier_governance_all_false() -> None:
    dossier = build_norm_geometry_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    for flag, val in dossier["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_norm_geometry_dossier_output_contract_safe() -> None:
    dossier = build_norm_geometry_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    oc = dossier["output_contract"]
    for key in oc:
        assert oc[key] is False, f"output_contract.{key} must be False"


def test_norm_geometry_dossier_mathematical_requirements_non_empty() -> None:
    dossier = build_norm_geometry_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    assert len(dossier["mathematical_requirements"]) >= 4


def test_norm_geometry_dossier_has_special_case_p_values() -> None:
    dossier = build_norm_geometry_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    joined = " ".join(dossier["mathematical_requirements"]).lower()
    assert "p=1" in joined or "l1" in joined
    assert "p=2" in joined or "l2" in joined
    assert "p=inf" in joined or "chebyshev" in joined


# ── Norm Geometry Test Vector Schema Plan ─────────────────────────────────────

def test_schema_plan_builds() -> None:
    plan = build_norm_geometry_test_vector_schema_plan(_schema_plan_payload())
    assert plan["operator_id"] == "NORM_GEOMETRY"
    assert plan["schema_scope"]["schema_stage"] == "SCHEMA_PLAN_ONLY"
    assert plan["schema_scope"]["schema_family"] == "MIXED_SCHEMA_PLAN"


def test_schema_plan_valid_groups_non_empty() -> None:
    plan = build_norm_geometry_test_vector_schema_plan(_schema_plan_payload())
    assert len(plan["valid_schema_groups"]) >= 4


def test_schema_plan_invalid_groups_non_empty() -> None:
    plan = build_norm_geometry_test_vector_schema_plan(_schema_plan_payload())
    assert len(plan["invalid_schema_groups"]) >= 2


def test_schema_plan_not_computable_groups_non_empty() -> None:
    plan = build_norm_geometry_test_vector_schema_plan(_schema_plan_payload())
    assert len(plan["not_computable_schema_groups"]) >= 2


def test_schema_plan_covers_p1_p2_p_inf() -> None:
    plan = build_norm_geometry_test_vector_schema_plan(_schema_plan_payload())
    contracts = {g["expected_input_contract"] for g in plan["valid_schema_groups"]}
    assert any("p1" in c or "p_1" in c or "p=1" in c for c in contracts)
    assert any("p2" in c or "p_2" in c or "p=2" in c for c in contracts)
    assert any("inf" in c for c in contracts)


def test_schema_plan_p_below_minimum_not_computable() -> None:
    plan = build_norm_geometry_test_vector_schema_plan(_schema_plan_payload())
    reasons = {g["not_computable_reason"] for g in plan["not_computable_schema_groups"]}
    assert "P_BELOW_MINIMUM" in reasons


def test_schema_plan_fixture_creation_blocked() -> None:
    plan = build_norm_geometry_test_vector_schema_plan(_schema_plan_payload())
    assert plan["schema_layout_plan"]["fixture_files_added"] is False
    assert plan["schema_constraints"]["fixture_artifacts_generated"] is False
    assert plan["schema_constraints"]["norm_geometry_computation_added"] is False


def test_schema_plan_deterministic() -> None:
    a = build_norm_geometry_test_vector_schema_plan(_schema_plan_payload())
    b = build_norm_geometry_test_vector_schema_plan(_schema_plan_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_schema_plan_hash_valid() -> None:
    plan = build_norm_geometry_test_vector_schema_plan(_schema_plan_payload())
    h = plan["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in plan.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_schema_plan_governance_all_false() -> None:
    plan = build_norm_geometry_test_vector_schema_plan(_schema_plan_payload())
    for flag, val in plan["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── Artifact file presence (post-runner) ─────────────────────────────────────

def test_rank4_candidate_audit_file_written() -> None:
    p = Path("out/metric_operator/metric_operator_rank4_candidate_audit_001.latest.json")
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["recommended_rank4"] == "NORM_GEOMETRY"
    assert data["audit_status"] == "RANK4_CANDIDATE_SELECTED"


def test_rank4_selection_plan_file_written() -> None:
    p = Path("out/metric_operator/metric_operator_rank4_selection_plan_001.latest.json")
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["selected_operator_id"] == "NORM_GEOMETRY"
    assert data["implementation_gates"]["fixture_creation_blocked"] is True


def test_norm_geometry_dossier_file_written() -> None:
    p = Path(
        "out/metric_operator/"
        "norm_geometry_distance_implementation_readiness_dossier_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["selected_operator"] == "NORM_GEOMETRY"
    assert data["dossier_status"] == "NORM_GEOMETRY_READINESS_DOSSIER_DEFINED"


def test_norm_geometry_schema_plan_file_written() -> None:
    p = Path(
        "out/metric_operator/norm_geometry_test_vector_schema_plan_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["operator_id"] == "NORM_GEOMETRY"
    assert data["schema_scope"]["schema_stage"] == "SCHEMA_PLAN_ONLY"
