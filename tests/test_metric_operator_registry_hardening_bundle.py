from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_registry_hardening import (
    ALLOWED_CHECK_RESULT,
    ALLOWED_COMPUTATION_STATUS,
    ALLOWED_GUARD_STATUS,
    ALLOWED_PLANNING_SCOPE,
    MetricOperatorRegistryHardeningError,
    build_metric_operator_registry_hardening,
    default_drift_guards,
    default_governance_flags,
    default_hardening_checks,
    default_operator_state_vector,
    default_output_contract,
)
from core.metric_operator_frontier_recommendation import (
    build_metric_operator_frontier_recommendation,
    default_governance_flags as frontier_gov_flags,
    default_output_contract as frontier_output_contract,
    four_operator_planned_ranked_options,
)
from core.canonical.json import canonical_hash

PATCH_ID = "METRIC_OPERATOR_REGISTRY_HARDENING_BUNDLE_001"

_HARDENING_ARTIFACT = Path(
    "out/metric_operator/metric_operator_registry_hardening_001.latest.json"
)
_FRONTIER_003_ARTIFACT = Path(
    "out/metric_operator/metric_operator_frontier_recommendation_003.latest.json"
)


def _hardening_payload() -> dict:
    return {
        "hardening_id": "metric_operator_registry_hardening_001",
        "hardening_status": "STABLE",
        "operator_state_vector": default_operator_state_vector(),
        "drift_guards": default_drift_guards(),
        "hardening_checks": default_hardening_checks(),
        "source_refs": [
            "MetricOperatorRegistryStabilization.v1:"
            "metric_operator_registry_stabilization_002",
        ],
        "output_contract": default_output_contract(),
        "governance_flags": default_governance_flags(),
        "provenance": {
            "source": "METRIC_OPERATOR_REGISTRY_HARDENING_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _frontier_payload() -> dict:
    return {
        "recommendation_id": "metric_operator_frontier_recommendation_003",
        "recommendation_status": "ADVISORY_ONLY",
        "ranked_options": four_operator_planned_ranked_options(),
        "recommended_next_step": "G_SEALED_PAUSE",
        "required_operator_decision": True,
        "stop_boundary_reason": "Test stop boundary.",
        "output_contract": frontier_output_contract(),
        "governance_flags": frontier_gov_flags(),
        "provenance": {
            "source": "METRIC_OPERATOR_REGISTRY_HARDENING_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ── Operator State Vector ─────────────────────────────────────────────────────

def test_operator_state_vector_count() -> None:
    osv = default_operator_state_vector()
    assert len(osv) == 12


def test_operator_state_vector_ids_unique() -> None:
    osv = default_operator_state_vector()
    ids = [e["operator_id"] for e in osv]
    assert len(ids) == len(set(ids))


def test_operator_state_vector_shadow_count() -> None:
    osv = default_operator_state_vector()
    shadow = [e for e in osv if e["computation_status"] == "SHADOW_STUB_ONLY"]
    assert len(shadow) == 3


def test_operator_state_vector_shadow_operators() -> None:
    osv = {e["operator_id"]: e for e in default_operator_state_vector()}
    for op in ("WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC"):
        assert osv[op]["computation_status"] == "SHADOW_STUB_ONLY"
        assert osv[op]["planning_scope"] == "SHADOW_STUB_ONLY_COMPLETE"


def test_operator_state_vector_not_implemented_count() -> None:
    osv = default_operator_state_vector()
    not_impl = [e for e in osv if e["computation_status"] == "NOT_IMPLEMENTED"]
    assert len(not_impl) == 9


def test_operator_state_vector_norm_geometry_state() -> None:
    osv = {e["operator_id"]: e for e in default_operator_state_vector()}
    ng = osv["NORM_GEOMETRY"]
    assert ng["computation_status"] == "NOT_IMPLEMENTED"
    assert ng["planning_scope"] == "CPU_BASELINE_PLANNING_COMPLETE"
    assert ng["execution_blocked"] is True
    assert ng["metric_emission_blocked"] is True
    assert ng["implementation_authorized"] is False


def test_operator_state_vector_remaining_not_implemented_no_planning() -> None:
    osv = {e["operator_id"]: e for e in default_operator_state_vector()}
    no_planning = (
        "TRANSPORT", "HYPERVECTOR_BINDING", "RESERVOIR_STATE_SPACE",
        "COUNTERFACTUAL_DIFFUSION", "HEAVY_TAIL", "HYSTERESIS",
        "STOCHASTIC_GEOMETRY", "TOPOLOGICAL_PRIMITIVES",
    )
    for op in no_planning:
        assert osv[op]["computation_status"] == "NOT_IMPLEMENTED", op
        assert osv[op]["planning_scope"] == "NONE", op


def test_all_operators_execution_blocked() -> None:
    osv = default_operator_state_vector()
    for entry in osv:
        assert entry["execution_blocked"] is True, entry["operator_id"]


def test_all_operators_metric_emission_blocked() -> None:
    osv = default_operator_state_vector()
    for entry in osv:
        assert entry["metric_emission_blocked"] is True, entry["operator_id"]


def test_all_operators_implementation_not_authorized() -> None:
    osv = default_operator_state_vector()
    for entry in osv:
        assert entry["implementation_authorized"] is False, entry["operator_id"]


def test_computation_status_values_valid() -> None:
    osv = default_operator_state_vector()
    for entry in osv:
        assert entry["computation_status"] in ALLOWED_COMPUTATION_STATUS, entry["operator_id"]


def test_planning_scope_values_valid() -> None:
    osv = default_operator_state_vector()
    for entry in osv:
        assert entry["planning_scope"] in ALLOWED_PLANNING_SCOPE, entry["operator_id"]


# ── Drift Guards ──────────────────────────────────────────────────────────────

def test_drift_guards_count() -> None:
    guards = default_drift_guards()
    assert len(guards) == 4


def test_drift_guard_ids_unique() -> None:
    guards = default_drift_guards()
    ids = [g["guard_id"] for g in guards]
    assert len(ids) == len(set(ids))


def test_drift_guards_all_active() -> None:
    guards = default_drift_guards()
    for g in guards:
        assert g["guard_status"] == "ACTIVE", g["guard_id"]


def test_drift_guard_001_covers_shadow_operators() -> None:
    guards = {g["guard_id"]: g for g in default_drift_guards()}
    g1 = guards["drift-guard-001"]
    assert "WASSERSTEIN" in g1["operators_in_scope"]
    assert "CHAMFER_DISTANCE" in g1["operators_in_scope"]
    assert "GEODESIC" in g1["operators_in_scope"]


def test_drift_guard_002_covers_norm_geometry() -> None:
    guards = {g["guard_id"]: g for g in default_drift_guards()}
    g2 = guards["drift-guard-002"]
    assert "NORM_GEOMETRY" in g2["operators_in_scope"]


def test_drift_guard_003_covers_all_operators() -> None:
    guards = {g["guard_id"]: g for g in default_drift_guards()}
    g3 = guards["drift-guard-003"]
    assert len(g3["operators_in_scope"]) == 12


def test_drift_guard_status_values_valid() -> None:
    guards = default_drift_guards()
    for g in guards:
        assert g["guard_status"] in ALLOWED_GUARD_STATUS, g["guard_id"]


# ── Hardening Checks ──────────────────────────────────────────────────────────

def test_hardening_checks_count() -> None:
    checks = default_hardening_checks()
    assert len(checks) == 10


def test_hardening_check_ids_unique() -> None:
    checks = default_hardening_checks()
    ids = [c["check_id"] for c in checks]
    assert len(ids) == len(set(ids))


def test_all_hardening_checks_pass() -> None:
    checks = default_hardening_checks()
    for c in checks:
        assert c["check_result"] == "PASS", c["check_id"]


def test_hardening_check_result_values_valid() -> None:
    checks = default_hardening_checks()
    for c in checks:
        assert c["check_result"] in ALLOWED_CHECK_RESULT, c["check_id"]


def test_check_007_shadow_count() -> None:
    checks = {c["check_id"]: c for c in default_hardening_checks()}
    c7 = checks["check-007"]
    assert c7["expected_count"] == 3
    assert c7["observed_count"] == 3


def test_check_008_not_implemented_count() -> None:
    checks = {c["check_id"]: c for c in default_hardening_checks()}
    c8 = checks["check-008"]
    assert c8["expected_count"] == 9
    assert c8["observed_count"] == 9


# ── Output Contract and Governance ────────────────────────────────────────────

def test_output_contract_no_metric_emission() -> None:
    oc = default_output_contract()
    assert oc["emits_metric_values"] is False
    assert oc["emits_scores"] is False
    assert oc["emits_authority_tokens"] is False
    assert oc["emits_hardening_record"] is True


def test_governance_flags_all_false() -> None:
    flags = default_governance_flags()
    for k, v in flags.items():
        assert v is False, f"governance_flags.{k} must be False"


# ── Build / Validate ──────────────────────────────────────────────────────────

def test_hardening_builds() -> None:
    record = build_metric_operator_registry_hardening(_hardening_payload())
    assert record["schema_version"] == "MetricOperatorRegistryHardening.v1"
    assert record["hardening_status"] == "STABLE"


def test_hardening_deterministic() -> None:
    a = build_metric_operator_registry_hardening(_hardening_payload())
    b = build_metric_operator_registry_hardening(_hardening_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_hardening_hash_valid() -> None:
    record = build_metric_operator_registry_hardening(_hardening_payload())
    h = record["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in record.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_hardening_governance_all_false() -> None:
    record = build_metric_operator_registry_hardening(_hardening_payload())
    for flag, val in record["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_hardening_invalid_status_raises() -> None:
    p = _hardening_payload()
    p["hardening_status"] = "RUNNING"
    with pytest.raises(MetricOperatorRegistryHardeningError, match="invalid_hardening_status"):
        build_metric_operator_registry_hardening(p)


def test_hardening_duplicate_operator_raises() -> None:
    p = _hardening_payload()
    dup = dict(p["operator_state_vector"][0])
    p["operator_state_vector"].append(dup)
    with pytest.raises(MetricOperatorRegistryHardeningError, match="duplicate_operator_id"):
        build_metric_operator_registry_hardening(p)


def test_hardening_implementation_authorized_true_raises() -> None:
    p = _hardening_payload()
    p["operator_state_vector"][0]["implementation_authorized"] = True
    with pytest.raises(MetricOperatorRegistryHardeningError,
                       match="implementation_authorized_must_be_false"):
        build_metric_operator_registry_hardening(p)


def test_hardening_metric_emission_unblocked_raises() -> None:
    p = _hardening_payload()
    p["operator_state_vector"][0]["metric_emission_blocked"] = False
    with pytest.raises(MetricOperatorRegistryHardeningError,
                       match="metric_emission_blocked_must_be_true"):
        build_metric_operator_registry_hardening(p)


def test_hardening_authority_flag_true_raises() -> None:
    p = _hardening_payload()
    p["governance_flags"]["forecast_influence"] = True
    with pytest.raises(MetricOperatorRegistryHardeningError,
                       match="authority_lock_must_be_false"):
        build_metric_operator_registry_hardening(p)


def test_hardening_forbidden_provenance_raises() -> None:
    p = _hardening_payload()
    p["provenance"]["generated_by"] = "callable-system-003"
    with pytest.raises(MetricOperatorRegistryHardeningError,
                       match="forbidden_provenance_reference_detected"):
        build_metric_operator_registry_hardening(p)


def test_hardening_operator_state_vector_sorted() -> None:
    record = build_metric_operator_registry_hardening(_hardening_payload())
    ids = [e["operator_id"] for e in record["operator_state_vector"]]
    assert ids == sorted(ids)


def test_hardening_drift_guards_sorted() -> None:
    record = build_metric_operator_registry_hardening(_hardening_payload())
    gids = [g["guard_id"] for g in record["drift_guards"]]
    assert gids == sorted(gids)


def test_hardening_checks_sorted() -> None:
    record = build_metric_operator_registry_hardening(_hardening_payload())
    cids = [c["check_id"] for c in record["hardening_checks"]]
    assert cids == sorted(cids)


# ── Frontier Recommendation 003 ───────────────────────────────────────────────

def test_four_operator_ranked_options_count() -> None:
    opts = four_operator_planned_ranked_options()
    assert len(opts) == 5


def test_four_operator_ranked_options_ids_unique() -> None:
    opts = four_operator_planned_ranked_options()
    ids = [o["option_id"] for o in opts]
    assert len(ids) == len(set(ids))


def test_four_operator_rank_1_is_sealed_pause() -> None:
    opts = {o["rank"]: o for o in four_operator_planned_ranked_options()}
    assert opts[1]["option_id"] == "G_SEALED_PAUSE"


def test_four_operator_rank_2_is_rank5_selection() -> None:
    opts = {o["rank"]: o for o in four_operator_planned_ranked_options()}
    assert opts[2]["option_id"] == "I_RANK5_OPERATOR_SELECTION"
    assert opts[2]["authority_posture"] == "ADVISORY_ONLY"


def test_four_operator_norm_geometry_auth_blocked() -> None:
    opts = {o["option_id"]: o for o in four_operator_planned_ranked_options()}
    assert opts["J_NORM_GEOMETRY_IMPLEMENTATION_AUTHORIZATION"]["authority_posture"] == "BLOCKED"


def test_four_operator_metric_emission_blocked() -> None:
    opts = {o["option_id"]: o for o in four_operator_planned_ranked_options()}
    assert opts["C_METRIC_EMISSION_AUTHORIZATION_REVIEW"]["authority_posture"] == "BLOCKED"


def test_four_operator_p43_blocked() -> None:
    opts = {o["option_id"]: o for o in four_operator_planned_ranked_options()}
    assert opts["E_P43_SURFACE_LANE_READINESS"]["authority_posture"] == "BLOCKED"


def test_frontier_003_builds() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    assert rec["recommendation_status"] == "ADVISORY_ONLY"
    assert rec["recommended_next_step"] == "G_SEALED_PAUSE"
    assert rec["required_operator_decision"] is True


def test_frontier_003_deterministic() -> None:
    a = build_metric_operator_frontier_recommendation(_frontier_payload())
    b = build_metric_operator_frontier_recommendation(_frontier_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_frontier_003_hash_valid() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    h = rec["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in rec.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_frontier_003_governance_all_false() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    for flag, val in rec["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── Artifact file presence (post-runner) ─────────────────────────────────────

def test_hardening_artifact_written() -> None:
    if not _HARDENING_ARTIFACT.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(_HARDENING_ARTIFACT.read_text())
    assert data["schema_version"] == "MetricOperatorRegistryHardening.v1"
    assert data["hardening_status"] == "STABLE"
    assert all(
        e["implementation_authorized"] is False
        for e in data["operator_state_vector"]
    )
    all_pass = all(
        c["check_result"] == "PASS"
        for c in data["hardening_checks"]
    )
    assert all_pass


def test_hardening_artifact_shadow_count() -> None:
    if not _HARDENING_ARTIFACT.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(_HARDENING_ARTIFACT.read_text())
    shadow = [
        e for e in data["operator_state_vector"]
        if e["computation_status"] == "SHADOW_STUB_ONLY"
    ]
    assert len(shadow) == 3


def test_frontier_003_artifact_written() -> None:
    if not _FRONTIER_003_ARTIFACT.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(_FRONTIER_003_ARTIFACT.read_text())
    assert data["schema_version"] == "MetricOperatorFrontierRecommendation.v1"
    assert data["recommendation_status"] == "ADVISORY_ONLY"
    opts = {o["option_id"]: o for o in data["ranked_options"]}
    assert opts["J_NORM_GEOMETRY_IMPLEMENTATION_AUTHORIZATION"]["authority_posture"] == "BLOCKED"
    assert opts["I_RANK5_OPERATOR_SELECTION"]["authority_posture"] == "ADVISORY_ONLY"


def test_frontier_003_artifact_governance_all_false() -> None:
    if not _FRONTIER_003_ARTIFACT.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(_FRONTIER_003_ARTIFACT.read_text())
    for v in data["governance_flags"].values():
        assert v is False
