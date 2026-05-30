from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.implementation_authorization_prep import (
    build_implementation_authorization_prep,
    default_locked_constants_required,
    default_readiness_comparison,
    default_recommendation_rationale,
    default_required_operator_decision_fields,
    default_output_contract as prep_output_contract,
)
from core.norm_geometry_implementation_authorization_template import (
    build_norm_geometry_implementation_authorization_template,
    default_locked_constants_required as ng_locked_constants,
    default_output_contract as ng_template_output_contract,
    default_required_operator_decision_fields as ng_decision_fields,
)
from core.transport_implementation_authorization_template import (
    build_transport_implementation_authorization_template,
    default_locked_constants_required as tr_locked_constants,
    default_output_contract as tr_template_output_contract,
    default_required_operator_decision_fields as tr_decision_fields,
)
from core.metric_operator_frontier_recommendation import (
    authorization_prep_complete_ranked_options,
    build_metric_operator_frontier_recommendation,
    default_governance_flags,
    default_output_contract as frontier_output_contract,
)
from core.canonical.json import canonical_hash

_LOCKED_FALSE = {
    "production_activation": False, "canon_promotion": False,
    "scheduler_mutation": False, "runtime_authority": False,
    "runtime_mutation": False, "forecast_influence": False,
    "execution_authority": False, "token_minting_allowed": False,
    "valid_for_execution": False, "activation_approved": False,
    "authorization_granted": False,
}
PATCH_ID = "IMPLEMENTATION_AUTHORIZATION_PREP_BUNDLE_001"


def _prep_payload() -> dict:
    return {
        "prep_id": "implementation_authorization_prep_001",
        "operators_compared": ["NORM_GEOMETRY", "TRANSPORT"],
        "readiness_comparison": default_readiness_comparison(),
        "recommended_first_implementation_path": "NORM_GEOMETRY",
        "recommendation_rationale": default_recommendation_rationale(),
        "required_operator_decision_fields": default_required_operator_decision_fields(),
        "locked_constants_required": default_locked_constants_required(),
        "output_contract": prep_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "IMPLEMENTATION_AUTHORIZATION_PREP_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "NormGeometryCpuBaselineActualPrGateReview.v1:"
                "norm_geometry_cpu_baseline_actual_pr_gate_review_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/implementation_authorization_prep.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _ng_template_payload() -> dict:
    return {
        "template_id": "norm_geometry_implementation_authorization_template_001",
        "required_operator_decision_fields": ng_decision_fields(),
        "locked_constants_required": ng_locked_constants(),
        "activation_blocked_reason": (
            "Template only; explicit operator authorization instruction required."
        ),
        "output_contract": ng_template_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "IMPLEMENTATION_AUTHORIZATION_PREP_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "ImplementationAuthorizationPrep.v1:"
                "implementation_authorization_prep_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/"
                "norm_geometry_implementation_authorization_template.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _tr_template_payload() -> dict:
    return {
        "template_id": "transport_implementation_authorization_template_001",
        "required_operator_decision_fields": tr_decision_fields(),
        "locked_constants_required": tr_locked_constants(),
        "activation_blocked_reason": (
            "Template only; explicit operator authorization instruction required."
        ),
        "output_contract": tr_template_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "IMPLEMENTATION_AUTHORIZATION_PREP_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "ImplementationAuthorizationPrep.v1:"
                "implementation_authorization_prep_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/"
                "transport_implementation_authorization_template.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _frontier_payload() -> dict:
    return {
        "recommendation_id": "metric_operator_frontier_recommendation_004",
        "recommendation_status": "ADVISORY_ONLY",
        "ranked_options": authorization_prep_complete_ranked_options(),
        "recommended_next_step": (
            "Operator emits NORM_GEOMETRY implementation authorization instruction."
        ),
        "required_operator_decision": True,
        "stop_boundary_reason": (
            "No self-authorizing step exists. Operator instruction required."
        ),
        "output_contract": frontier_output_contract(),
        "governance_flags": default_governance_flags(),
        "provenance": {
            "source": "IMPLEMENTATION_AUTHORIZATION_PREP_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "ImplementationAuthorizationPrep.v1:"
                "implementation_authorization_prep_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/"
                "metric_operator_frontier_recommendation.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ── ImplementationAuthorizationPrep ──────────────────────────────────────────

def test_prep_builds() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    assert prep["prep_type"] == "IMPLEMENTATION_AUTHORIZATION_PREP"
    assert prep["authorization_granted"] is False
    assert prep["authorization_prep_complete"] is True


def test_prep_operators_compared() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    ops = prep["operators_compared"]
    assert "NORM_GEOMETRY" in ops
    assert "TRANSPORT" in ops


def test_prep_recommended_first_is_norm_geometry() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    assert prep["recommended_first_implementation_path"] == "NORM_GEOMETRY"


def test_prep_readiness_comparison_has_both_operators() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    rc = prep["readiness_comparison"]
    assert "NORM_GEOMETRY" in rc
    assert "TRANSPORT" in rc


def test_prep_norm_geometry_no_solver_dependency() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    assert prep["readiness_comparison"]["NORM_GEOMETRY"]["solver_dependency_risk"] == "NONE"


def test_prep_transport_high_solver_dependency() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    assert prep["readiness_comparison"]["TRANSPORT"]["solver_dependency_risk"] == "HIGH"


def test_prep_norm_geometry_closed_form_path() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    path = prep["readiness_comparison"]["NORM_GEOMETRY"]["fastest_safe_implementation_path"]
    assert path == "CPU_REFERENCE_CLOSED_FORM"


def test_prep_transport_degenerate_first_path() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    path = prep["readiness_comparison"]["TRANSPORT"]["fastest_safe_implementation_path"]
    assert path == "DEGENERATE_CASES_FIRST_THEN_LP"


def test_prep_norm_geometry_low_deterministic_risk() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    risk = prep["readiness_comparison"]["NORM_GEOMETRY"]["deterministic_implementation_risk"]
    assert risk == "LOW"


def test_prep_transport_medium_deterministic_risk() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    risk = prep["readiness_comparison"]["TRANSPORT"]["deterministic_implementation_risk"]
    assert risk == "MEDIUM"


def test_prep_required_decision_fields_non_empty() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    assert len(prep["required_operator_decision_fields"]) == 2


def test_prep_norm_geometry_has_five_decisions() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    entry = next(
        e for e in prep["required_operator_decision_fields"]
        if e["operator_id"] == "NORM_GEOMETRY"
    )
    assert len(entry["required_decisions"]) == 5


def test_prep_transport_has_seven_decisions() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    entry = next(
        e for e in prep["required_operator_decision_fields"]
        if e["operator_id"] == "TRANSPORT"
    )
    assert len(entry["required_decisions"]) == 7


def test_prep_transport_decisions_include_lp_solver() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    entry = next(
        e for e in prep["required_operator_decision_fields"]
        if e["operator_id"] == "TRANSPORT"
    )
    field_names = [d["field_name"] for d in entry["required_decisions"]]
    assert "lp_solver_variant_declaration" in field_names
    assert "pivot_rule_declaration" in field_names
    assert "tie_breaking_rule_declaration" in field_names
    assert "balance_tolerance_declaration" in field_names


def test_prep_norm_geometry_locked_constants_count() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    assert len(prep["locked_constants_required"]["NORM_GEOMETRY"]) == 5


def test_prep_transport_locked_constants_count() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    assert len(prep["locked_constants_required"]["TRANSPORT"]) == 7


def test_prep_output_contract_no_auth_granted() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    oc = prep["output_contract"]
    assert oc["emits_prep_artifact"] is True
    assert oc["authorization_granted"] is False
    assert oc["emits_metric_values"] is False
    assert oc["emits_authority_tokens"] is False


def test_prep_deterministic() -> None:
    a = build_implementation_authorization_prep(_prep_payload())
    b = build_implementation_authorization_prep(_prep_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_prep_hash_valid() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    h = prep["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in prep.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_prep_governance_all_false() -> None:
    prep = build_implementation_authorization_prep(_prep_payload())
    for flag, val in prep["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── NormGeometry Authorization Template ──────────────────────────────────────

def test_ng_template_builds() -> None:
    tmpl = build_norm_geometry_implementation_authorization_template(_ng_template_payload())
    assert tmpl["operator_id"] == "NORM_GEOMETRY"
    assert tmpl["template_status"] == "TEMPLATE_ONLY"
    assert tmpl["active"] is False
    assert tmpl["valid_for_execution"] is False
    assert tmpl["authorization_granted"] is False


def test_ng_template_decision_fields_non_empty() -> None:
    tmpl = build_norm_geometry_implementation_authorization_template(_ng_template_payload())
    assert len(tmpl["required_operator_decision_fields"]) == 5


def test_ng_template_includes_p_inf_sentinel() -> None:
    tmpl = build_norm_geometry_implementation_authorization_template(_ng_template_payload())
    field_names = [d["field_name"] for d in tmpl["required_operator_decision_fields"]]
    assert "p_inf_sentinel_value_declaration" in field_names


def test_ng_template_includes_not_computable_confirmation() -> None:
    tmpl = build_norm_geometry_implementation_authorization_template(_ng_template_payload())
    field_names = [d["field_name"] for d in tmpl["required_operator_decision_fields"]]
    assert "not_computable_branch_enumeration_confirmation" in field_names


def test_ng_template_locked_constants_five() -> None:
    tmpl = build_norm_geometry_implementation_authorization_template(_ng_template_payload())
    assert len(tmpl["locked_constants_required"]) == 5


def test_ng_template_all_decisions_locked_false() -> None:
    tmpl = build_norm_geometry_implementation_authorization_template(_ng_template_payload())
    for d in tmpl["required_operator_decision_fields"]:
        assert d["locked"] is False


def test_ng_template_output_contract() -> None:
    tmpl = build_norm_geometry_implementation_authorization_template(_ng_template_payload())
    oc = tmpl["output_contract"]
    assert oc["emits_template"] is True
    assert oc["authorization_granted"] is False
    assert oc["emits_metric_values"] is False


def test_ng_template_deterministic() -> None:
    a = build_norm_geometry_implementation_authorization_template(_ng_template_payload())
    b = build_norm_geometry_implementation_authorization_template(_ng_template_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_ng_template_hash_valid() -> None:
    tmpl = build_norm_geometry_implementation_authorization_template(_ng_template_payload())
    h = tmpl["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in tmpl.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_ng_template_governance_all_false() -> None:
    tmpl = build_norm_geometry_implementation_authorization_template(_ng_template_payload())
    for flag, val in tmpl["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── Transport Authorization Template ─────────────────────────────────────────

def test_tr_template_builds() -> None:
    tmpl = build_transport_implementation_authorization_template(_tr_template_payload())
    assert tmpl["operator_id"] == "TRANSPORT"
    assert tmpl["template_status"] == "TEMPLATE_ONLY"
    assert tmpl["active"] is False
    assert tmpl["valid_for_execution"] is False
    assert tmpl["authorization_granted"] is False


def test_tr_template_decision_fields_non_empty() -> None:
    tmpl = build_transport_implementation_authorization_template(_tr_template_payload())
    assert len(tmpl["required_operator_decision_fields"]) == 7


def test_tr_template_includes_lp_solver_variant() -> None:
    tmpl = build_transport_implementation_authorization_template(_tr_template_payload())
    field_names = [d["field_name"] for d in tmpl["required_operator_decision_fields"]]
    assert "lp_solver_variant_declaration" in field_names


def test_tr_template_includes_pivot_rule() -> None:
    tmpl = build_transport_implementation_authorization_template(_tr_template_payload())
    field_names = [d["field_name"] for d in tmpl["required_operator_decision_fields"]]
    assert "pivot_rule_declaration" in field_names


def test_tr_template_includes_tie_breaking_rule() -> None:
    tmpl = build_transport_implementation_authorization_template(_tr_template_payload())
    field_names = [d["field_name"] for d in tmpl["required_operator_decision_fields"]]
    assert "tie_breaking_rule_declaration" in field_names


def test_tr_template_includes_balance_tolerance() -> None:
    tmpl = build_transport_implementation_authorization_template(_tr_template_payload())
    field_names = [d["field_name"] for d in tmpl["required_operator_decision_fields"]]
    assert "balance_tolerance_declaration" in field_names


def test_tr_template_locked_constants_seven() -> None:
    tmpl = build_transport_implementation_authorization_template(_tr_template_payload())
    assert len(tmpl["locked_constants_required"]) == 7


def test_tr_template_all_decisions_locked_false() -> None:
    tmpl = build_transport_implementation_authorization_template(_tr_template_payload())
    for d in tmpl["required_operator_decision_fields"]:
        assert d["locked"] is False


def test_tr_template_output_contract() -> None:
    tmpl = build_transport_implementation_authorization_template(_tr_template_payload())
    oc = tmpl["output_contract"]
    assert oc["emits_template"] is True
    assert oc["authorization_granted"] is False
    assert oc["emits_metric_values"] is False


def test_tr_template_deterministic() -> None:
    a = build_transport_implementation_authorization_template(_tr_template_payload())
    b = build_transport_implementation_authorization_template(_tr_template_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_tr_template_hash_valid() -> None:
    tmpl = build_transport_implementation_authorization_template(_tr_template_payload())
    h = tmpl["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in tmpl.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_tr_template_governance_all_false() -> None:
    tmpl = build_transport_implementation_authorization_template(_tr_template_payload())
    for flag, val in tmpl["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── Frontier Recommendation _004 ─────────────────────────────────────────────

def test_frontier_004_builds() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    assert rec["recommendation_id"] == "metric_operator_frontier_recommendation_004"
    assert rec["recommendation_status"] == "ADVISORY_ONLY"
    assert rec["required_operator_decision"] is True


def test_frontier_004_has_seven_options() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    assert len(rec["ranked_options"]) == 7


def test_frontier_004_rank1_sealed_pause_advisory() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    opt = next(o for o in rec["ranked_options"] if o["rank"] == 1)
    assert opt["option_id"] == "G_SEALED_PAUSE"
    assert opt["authority_posture"] == "ADVISORY_ONLY"


def test_frontier_004_norm_geometry_rank2_advisory() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    opt = next(o for o in rec["ranked_options"] if o["rank"] == 2)
    assert opt["option_id"] == "J_NORM_GEOMETRY_IMPLEMENTATION_AUTHORIZATION"
    assert opt["authority_posture"] == "ADVISORY_ONLY"


def test_frontier_004_transport_rank3_blocked() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    opt = next(o for o in rec["ranked_options"] if o["rank"] == 3)
    assert opt["option_id"] == "K_TRANSPORT_IMPLEMENTATION_AUTHORIZATION"
    assert opt["authority_posture"] == "BLOCKED"


def test_frontier_004_rank6_operator_selection_present() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    ids = [o["option_id"] for o in rec["ranked_options"]]
    assert "L_RANK6_OPERATOR_SELECTION" in ids


def test_frontier_004_registry_hardening_present() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    ids = [o["option_id"] for o in rec["ranked_options"]]
    assert "M_REGISTRY_HARDENING" in ids


def test_frontier_004_metric_emission_blocked() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    opt = next(
        o for o in rec["ranked_options"]
        if o["option_id"] == "C_METRIC_EMISSION_AUTHORIZATION_REVIEW"
    )
    assert opt["authority_posture"] == "BLOCKED"


def test_frontier_004_p43_blocked() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    opt = next(
        o for o in rec["ranked_options"]
        if o["option_id"] == "E_P43_SURFACE_LANE_READINESS"
    )
    assert opt["authority_posture"] == "BLOCKED"


def test_frontier_004_advisory_posture_upgraded_from_prev() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    ng_opt = next(
        o for o in rec["ranked_options"]
        if o["option_id"] == "J_NORM_GEOMETRY_IMPLEMENTATION_AUTHORIZATION"
    )
    assert ng_opt["authority_posture"] == "ADVISORY_ONLY"


def test_frontier_004_ranks_unique() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    ranks = [o["rank"] for o in rec["ranked_options"]]
    assert len(ranks) == len(set(ranks))


def test_frontier_004_option_ids_unique() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    ids = [o["option_id"] for o in rec["ranked_options"]]
    assert len(ids) == len(set(ids))


def test_frontier_004_deterministic() -> None:
    a = build_metric_operator_frontier_recommendation(_frontier_payload())
    b = build_metric_operator_frontier_recommendation(_frontier_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_frontier_004_hash_valid() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    h = rec["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in rec.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_frontier_004_governance_all_false() -> None:
    rec = build_metric_operator_frontier_recommendation(_frontier_payload())
    for flag, val in rec["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── Artifact file presence (post-runner) ──────────────────────────────────────

def test_prep_file_written() -> None:
    p = Path("out/metric_operator/implementation_authorization_prep_001.latest.json")
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["prep_type"] == "IMPLEMENTATION_AUTHORIZATION_PREP"
    assert data["recommended_first_implementation_path"] == "NORM_GEOMETRY"
    assert data["authorization_granted"] is False


def test_ng_template_file_written() -> None:
    p = Path(
        "out/metric_operator/"
        "norm_geometry_implementation_authorization_template_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["operator_id"] == "NORM_GEOMETRY"
    assert data["template_status"] == "TEMPLATE_ONLY"
    assert data["active"] is False
    assert data["authorization_granted"] is False


def test_tr_template_file_written() -> None:
    p = Path(
        "out/metric_operator/"
        "transport_implementation_authorization_template_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["operator_id"] == "TRANSPORT"
    assert data["template_status"] == "TEMPLATE_ONLY"
    assert data["active"] is False
    assert data["authorization_granted"] is False


def test_frontier_004_file_written() -> None:
    p = Path(
        "out/metric_operator/metric_operator_frontier_recommendation_004.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["recommendation_id"] == "metric_operator_frontier_recommendation_004"
    assert len(data["ranked_options"]) == 7
    ng_opt = next(
        o for o in data["ranked_options"]
        if o["option_id"] == "J_NORM_GEOMETRY_IMPLEMENTATION_AUTHORIZATION"
    )
    assert ng_opt["authority_posture"] == "ADVISORY_ONLY"
