from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_rank5_candidate_audit import (
    build_metric_operator_rank5_candidate_audit,
    default_candidate_entries,
    default_output_contract as audit_output_contract,
)
from core.metric_operator_rank5_selection_plan import (
    build_metric_operator_rank5_selection_plan,
    default_implementation_gates,
    default_output_contract as plan_output_contract,
)
from core.transport_distance_implementation_readiness_dossier import (
    REQUIRED_BLOCKED_SCOPES,
    build_transport_distance_implementation_readiness_dossier,
    default_authority_locks,
    default_blocked_scopes,
    default_output_contract as dossier_output_contract,
)
from core.transport_test_vector_schema_plan import (
    build_transport_test_vector_schema_plan,
    default_output_contract as schema_plan_output_contract,
    default_schema_constraints,
    default_schema_layout_plan,
    default_validation_plan,
)
from core.canonical.json import canonical_hash

COMPLETED_OPS_RANK5 = [
    "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY", "WASSERSTEIN",
]
NOT_IMPL_OPS_RANK5 = {
    "TRANSPORT", "TOPOLOGICAL_PRIMITIVES", "HEAVY_TAIL",
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
        "audit_id": "metric_operator_rank5_candidate_audit_001",
        "audit_status": "RANK5_CANDIDATE_SELECTED",
        "completed_operators": list(COMPLETED_OPS_RANK5),
        "candidate_entries": default_candidate_entries(),
        "recommended_rank5": "TRANSPORT",
        "output_contract": audit_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "FIFTH_OPERATOR_SELECTION_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": "FIFTH_OPERATOR_SELECTION_BUNDLE_001",
            "evidence_refs": [
                "MetricOperatorRegistryHardening.v1:metric_operator_registry_hardening_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_rank5_candidate_audit.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _plan_payload() -> dict:
    return {
        "plan_id": "metric_operator_rank5_selection_plan_001",
        "selected_operator_id": "TRANSPORT",
        "selection_scope": {
            "intended_lane": "SHADOW",
            "selection_family": "RANK5_OPERATOR_SELECTION",
            "selection_stage": "SELECTION_PLAN_ONLY",
        },
        "source_audit_refs": [
            "MetricOperatorRank5CandidateAudit.v1:metric_operator_rank5_candidate_audit_001",
        ],
        "source_registry_stabilization_refs": [
            "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_002",
        ],
        "source_frontier_recommendation_refs": [
            "MetricOperatorFrontierRecommendation.v1:metric_operator_frontier_recommendation_003",
        ],
        "implementation_gates": default_implementation_gates(),
        "output_contract": plan_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "FIFTH_OPERATOR_SELECTION_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": "FIFTH_OPERATOR_SELECTION_BUNDLE_001",
            "evidence_refs": [
                "MetricOperatorRank5CandidateAudit.v1:metric_operator_rank5_candidate_audit_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_rank5_selection_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _dossier_payload() -> dict:
    return {
        "dossier_id": "transport_distance_implementation_readiness_dossier_001",
        "implementation_scope": "TRANSPORT_DISTANCE_READINESS_ONLY",
        "output_contract": dossier_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "FIFTH_OPERATOR_SELECTION_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": "FIFTH_OPERATOR_SELECTION_BUNDLE_001",
            "evidence_refs": [
                "MetricOperatorRank5SelectionPlan.v1:metric_operator_rank5_selection_plan_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/transport_distance_implementation_readiness_dossier.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _schema_plan_payload() -> dict:
    return {
        "plan_id": "transport_test_vector_schema_plan_001",
        "schema_scope": {
            "schema_family": "MIXED_SCHEMA_PLAN",
            "intended_lane": "SHADOW",
            "schema_stage": "SCHEMA_PLAN_ONLY",
        },
        "source_dossier_refs": [
            "TransportDistanceImplementationReadinessDossier.v1:"
            "transport_distance_implementation_readiness_dossier_001",
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
            "source": "FIFTH_OPERATOR_SELECTION_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": "FIFTH_OPERATOR_SELECTION_BUNDLE_001",
            "evidence_refs": [
                "TransportDistanceImplementationReadinessDossier.v1:"
                "transport_distance_implementation_readiness_dossier_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/transport_test_vector_schema_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ── Rank5 Candidate Audit ─────────────────────────────────────────────────────

def test_candidate_entries_count() -> None:
    entries = default_candidate_entries()
    assert len(entries) == 8


def test_candidate_entries_cover_all_not_impl_ops() -> None:
    entries = default_candidate_entries()
    ids = {e["operator_id"] for e in entries}
    assert ids == NOT_IMPL_OPS_RANK5


def test_candidate_entries_norm_geometry_absent() -> None:
    entries = default_candidate_entries()
    ids = {e["operator_id"] for e in entries}
    assert "NORM_GEOMETRY" not in ids


def test_candidate_entries_exactly_one_selected() -> None:
    entries = default_candidate_entries()
    selected = [e for e in entries if e["selection_status"] == "SELECTED_RANK5"]
    assert len(selected) == 1


def test_candidate_entries_transport_selected() -> None:
    entries = default_candidate_entries()
    sel = next(e for e in entries if e["selection_status"] == "SELECTED_RANK5")
    assert sel["operator_id"] == "TRANSPORT"
    assert sel["composite_rank"] == 1


def test_candidate_entries_transport_governance_risk_low() -> None:
    entries = default_candidate_entries()
    tr = next(e for e in entries if e["operator_id"] == "TRANSPORT")
    assert tr["governance_risk"] == "LOW"
    assert tr["proximity_to_completed_operators"] == "HIGH"


def test_candidate_entries_rejected_have_reason() -> None:
    entries = default_candidate_entries()
    for e in entries:
        if e["selection_status"] == "REJECTED":
            assert "rejection_reason" in e, e["operator_id"]


def test_candidate_entries_composite_ranks_unique() -> None:
    entries = default_candidate_entries()
    ranks = [e["composite_rank"] for e in entries]
    assert len(ranks) == len(set(ranks))


def test_rank5_audit_builds() -> None:
    audit = build_metric_operator_rank5_candidate_audit(_audit_payload())
    assert audit["audit_status"] == "RANK5_CANDIDATE_SELECTED"
    assert audit["recommended_rank5"] == "TRANSPORT"
    assert sorted(audit["completed_operators"]) == sorted(COMPLETED_OPS_RANK5)


def test_rank5_audit_completed_ops_include_norm_geometry() -> None:
    audit = build_metric_operator_rank5_candidate_audit(_audit_payload())
    assert "NORM_GEOMETRY" in audit["completed_operators"]


def test_rank5_audit_deterministic() -> None:
    a = build_metric_operator_rank5_candidate_audit(_audit_payload())
    b = build_metric_operator_rank5_candidate_audit(_audit_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_rank5_audit_hash_valid() -> None:
    audit = build_metric_operator_rank5_candidate_audit(_audit_payload())
    h = audit["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in audit.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_rank5_audit_governance_all_false() -> None:
    audit = build_metric_operator_rank5_candidate_audit(_audit_payload())
    for flag, val in audit["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_rank5_audit_output_contract_emits_ranking_only() -> None:
    audit = build_metric_operator_rank5_candidate_audit(_audit_payload())
    oc = audit["output_contract"]
    assert oc["emits_candidate_ranking"] is True
    assert oc["emits_metric_values"] is False
    assert oc["emits_authority_tokens"] is False


# ── Rank5 Selection Plan ──────────────────────────────────────────────────────

def test_rank5_selection_plan_builds() -> None:
    plan = build_metric_operator_rank5_selection_plan(_plan_payload())
    assert plan["selected_operator_id"] == "TRANSPORT"
    assert plan["selection_scope"]["selection_stage"] == "SELECTION_PLAN_ONLY"
    assert plan["selection_scope"]["selection_family"] == "RANK5_OPERATOR_SELECTION"


def test_rank5_selection_plan_implementation_gates() -> None:
    plan = build_metric_operator_rank5_selection_plan(_plan_payload())
    gates = plan["implementation_gates"]
    assert gates["implementation_blocked"] is True
    assert gates["fixture_creation_blocked"] is True
    assert gates["planning_only"] is True
    assert gates["requires_dedicated_tests"] is True
    assert gates["requires_new_operator_plan"] is True


def test_rank5_selection_plan_deterministic() -> None:
    a = build_metric_operator_rank5_selection_plan(_plan_payload())
    b = build_metric_operator_rank5_selection_plan(_plan_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_rank5_selection_plan_hash_valid() -> None:
    plan = build_metric_operator_rank5_selection_plan(_plan_payload())
    h = plan["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in plan.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_rank5_selection_plan_governance_all_false() -> None:
    plan = build_metric_operator_rank5_selection_plan(_plan_payload())
    for flag, val in plan["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_rank5_selection_plan_emits_selection_metadata_only() -> None:
    plan = build_metric_operator_rank5_selection_plan(_plan_payload())
    oc = plan["output_contract"]
    assert oc["emits_selection_metadata"] is True
    assert oc["emits_metric_values"] is False
    assert oc["emits_authority_tokens"] is False


def test_rank5_selection_plan_source_refs_non_empty() -> None:
    plan = build_metric_operator_rank5_selection_plan(_plan_payload())
    assert len(plan["source_audit_refs"]) >= 1
    assert len(plan["source_registry_stabilization_refs"]) >= 1
    assert len(plan["source_frontier_recommendation_refs"]) >= 1


# ── Transport Readiness Dossier ───────────────────────────────────────────────

def test_dossier_default_blocked_scopes_complete() -> None:
    blocked = set(default_blocked_scopes())
    assert REQUIRED_BLOCKED_SCOPES.issubset(blocked)


def test_dossier_blocked_scopes_include_lp_solver() -> None:
    blocked = default_blocked_scopes()
    assert "lp_solver_invocation" in blocked
    assert "transport_computation" in blocked


def test_dossier_default_authority_locks() -> None:
    locks = default_authority_locks()
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["readiness_dossier_only"] is True
    assert locks["transport_computation_authorized"] is False
    assert locks["lp_solver_invocation_authorized"] is False
    assert locks["emits_metric_values"] is False
    assert locks["execution_authority"] is False


def test_transport_dossier_builds() -> None:
    dossier = build_transport_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    assert dossier["selected_operator"] == "TRANSPORT"
    assert dossier["dossier_status"] == "TRANSPORT_READINESS_DOSSIER_DEFINED"
    assert dossier["intended_lane"] == "SHADOW"
    assert dossier["readiness_scope"] == "IMPLEMENTATION_READINESS_ONLY"


def test_transport_dossier_deterministic() -> None:
    a = build_transport_distance_implementation_readiness_dossier(_dossier_payload())
    b = build_transport_distance_implementation_readiness_dossier(_dossier_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_transport_dossier_hash_valid() -> None:
    dossier = build_transport_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    h = dossier["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in dossier.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_transport_dossier_governance_all_false() -> None:
    dossier = build_transport_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    for flag, val in dossier["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_transport_dossier_output_contract_all_false() -> None:
    dossier = build_transport_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    oc = dossier["output_contract"]
    for key in oc:
        assert oc[key] is False, f"output_contract.{key} must be False"


def test_transport_dossier_mathematical_requirements_non_empty() -> None:
    dossier = build_transport_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    assert len(dossier["mathematical_requirements"]) >= 4


def test_transport_dossier_mentions_balanced_transport() -> None:
    dossier = build_transport_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    joined = " ".join(dossier["mathematical_requirements"]).lower()
    assert "balanced" in joined or "sum(s)" in joined or "sum(d)" in joined


def test_transport_dossier_mentions_cost_matrix() -> None:
    dossier = build_transport_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    joined = " ".join(dossier["mathematical_requirements"]).lower()
    assert "cost" in joined


def test_transport_dossier_mentions_degenerate_cases() -> None:
    dossier = build_transport_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    joined = " ".join(dossier["mathematical_requirements"]).lower()
    assert "m=1" in joined or "single-source" in joined or "single source" in joined


def test_transport_dossier_has_lp_solver_dependency() -> None:
    dossier = build_transport_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    dep_types = {d["dependency_type"] for d in dossier["dependency_inventory"]}
    assert "SOLVER_POLICY" in dep_types


def test_transport_dossier_has_implementation_risks() -> None:
    dossier = build_transport_distance_implementation_readiness_dossier(
        _dossier_payload()
    )
    assert len(dossier["implementation_risks"]) >= 2
    levels = {r["risk_level"] for r in dossier["implementation_risks"]}
    assert levels.issubset({"LOW", "MEDIUM", "HIGH"})


# ── Transport Test Vector Schema Plan ─────────────────────────────────────────

def test_schema_plan_builds() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    assert plan["operator_id"] == "TRANSPORT"
    assert plan["schema_scope"]["schema_stage"] == "SCHEMA_PLAN_ONLY"
    assert plan["schema_scope"]["schema_family"] == "MIXED_SCHEMA_PLAN"


def test_schema_plan_valid_groups_non_empty() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    assert len(plan["valid_schema_groups"]) >= 4


def test_schema_plan_invalid_groups_non_empty() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    assert len(plan["invalid_schema_groups"]) >= 2


def test_schema_plan_not_computable_groups_non_empty() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    assert len(plan["not_computable_schema_groups"]) >= 3


def test_schema_plan_has_unbalanced_not_computable() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    reasons = {g["not_computable_reason"] for g in plan["not_computable_schema_groups"]}
    assert "UNBALANCED_SUPPLY_DEMAND" in reasons


def test_schema_plan_has_negative_supply_not_computable() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    reasons = {g["not_computable_reason"] for g in plan["not_computable_schema_groups"]}
    assert "NEGATIVE_SUPPLY_VALUE" in reasons


def test_schema_plan_has_empty_supply_not_computable() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    reasons = {g["not_computable_reason"] for g in plan["not_computable_schema_groups"]}
    assert "EMPTY_SUPPLY_VECTOR" in reasons


def test_schema_plan_has_single_source_valid_group() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    contracts = {g["expected_input_contract"] for g in plan["valid_schema_groups"]}
    assert any("single_source" in c or "1x" in c for c in contracts)


def test_schema_plan_has_degenerate_1x1_valid_group() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    contracts = {g["expected_input_contract"] for g in plan["valid_schema_groups"]}
    assert any("1x1" in c or "degenerate" in c for c in contracts)


def test_schema_plan_fixture_creation_blocked() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    assert plan["schema_layout_plan"]["fixture_files_added"] is False
    assert plan["schema_constraints"]["fixture_artifacts_generated"] is False
    assert plan["schema_constraints"]["transport_computation_added"] is False
    assert plan["schema_constraints"]["lp_solver_invoked"] is False


def test_schema_plan_deterministic() -> None:
    a = build_transport_test_vector_schema_plan(_schema_plan_payload())
    b = build_transport_test_vector_schema_plan(_schema_plan_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_schema_plan_hash_valid() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    h = plan["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in plan.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_schema_plan_governance_all_false() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    for flag, val in plan["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_schema_plan_group_ids_unique_per_list() -> None:
    plan = build_transport_test_vector_schema_plan(_schema_plan_payload())
    for group_list in (
        plan["valid_schema_groups"],
        plan["invalid_schema_groups"],
        plan["not_computable_schema_groups"],
    ):
        ids = [g["group_id"] for g in group_list]
        assert len(ids) == len(set(ids))


# ── Artifact file presence (post-runner) ──────────────────────────────────────

def test_rank5_candidate_audit_file_written() -> None:
    p = Path("out/metric_operator/metric_operator_rank5_candidate_audit_001.latest.json")
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["recommended_rank5"] == "TRANSPORT"
    assert data["audit_status"] == "RANK5_CANDIDATE_SELECTED"


def test_rank5_selection_plan_file_written() -> None:
    p = Path("out/metric_operator/metric_operator_rank5_selection_plan_001.latest.json")
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["selected_operator_id"] == "TRANSPORT"
    assert data["implementation_gates"]["fixture_creation_blocked"] is True


def test_transport_dossier_file_written() -> None:
    p = Path(
        "out/metric_operator/"
        "transport_distance_implementation_readiness_dossier_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["selected_operator"] == "TRANSPORT"
    assert data["dossier_status"] == "TRANSPORT_READINESS_DOSSIER_DEFINED"


def test_transport_schema_plan_file_written() -> None:
    p = Path(
        "out/metric_operator/transport_test_vector_schema_plan_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["operator_id"] == "TRANSPORT"
    assert data["schema_scope"]["schema_stage"] == "SCHEMA_PLAN_ONLY"
