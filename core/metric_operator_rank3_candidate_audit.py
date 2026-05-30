from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "MetricOperatorRank3CandidateAudit.v1"
AUDIT_TYPE = "METRIC_OPERATOR_RANK3_CANDIDATE_AUDIT"
ALLOWED_LEVEL = ("LOW", "MEDIUM", "HIGH")
ALLOWED_SELECTION_STATUS = ("SELECTED_RANK3", "REJECTED")
ALLOWED_AUDIT_STATUS = ("RANK3_CANDIDATE_SELECTED", "AUDIT_INCOMPLETE", "NO_VIABLE_CANDIDATE")
LOCKED_FALSE_FLAGS = (
    "production_activation", "canon_promotion", "scheduler_mutation",
    "runtime_authority", "runtime_mutation", "forecast_influence",
    "execution_authority", "token_minting_allowed", "valid_for_execution",
    "activation_approved", "authorization_granted",
)
FORBIDDEN = (
    "executable", "callable", "runtime", "scheduler", "cache", "forecast",
    "scoring", "metric-computation", "metric-value", "geodesic-distance",
    "numpy", "scipy", "gpu-kernel",
)


class MetricOperatorRank3CandidateAuditValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_candidate_entries() -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": "cand_001_geodesic",
            "operator_id": "GEODESIC",
            "proximity_to_completed_operators": "HIGH",
            "deterministic_fixture_feasibility": "HIGH",
            "schema_complexity": "LOW",
            "numerical_stability_risk": "MEDIUM",
            "aal_viz_value": "HIGH",
            "composite_rank": 1,
            "selection_status": "SELECTED_RANK3",
        },
        {
            "candidate_id": "cand_002_norm_geometry",
            "operator_id": "NORM_GEOMETRY",
            "proximity_to_completed_operators": "HIGH",
            "deterministic_fixture_feasibility": "HIGH",
            "schema_complexity": "LOW",
            "numerical_stability_risk": "LOW",
            "aal_viz_value": "MEDIUM",
            "composite_rank": 2,
            "selection_status": "REJECTED",
            "rejection_reason": "Lower AAL-Viz novelty; Lp-norm distances underlie Chamfer internals and add less substrate value than geodesic graph distance.",
        },
        {
            "candidate_id": "cand_003_transport",
            "operator_id": "TRANSPORT",
            "proximity_to_completed_operators": "HIGH",
            "deterministic_fixture_feasibility": "MEDIUM",
            "schema_complexity": "MEDIUM",
            "numerical_stability_risk": "MEDIUM",
            "aal_viz_value": "MEDIUM",
            "composite_rank": 3,
            "selection_status": "REJECTED",
            "rejection_reason": "Conceptually redundant with WASSERSTEIN (both OT-based); adds less marginal coverage than a distinct geometric primitive.",
        },
        {
            "candidate_id": "cand_004_topological_primitives",
            "operator_id": "TOPOLOGICAL_PRIMITIVES",
            "proximity_to_completed_operators": "MEDIUM",
            "deterministic_fixture_feasibility": "MEDIUM",
            "schema_complexity": "HIGH",
            "numerical_stability_risk": "HIGH",
            "aal_viz_value": "HIGH",
            "composite_rank": 4,
            "selection_status": "REJECTED",
            "rejection_reason": "High schema complexity and numerical stability risk (persistent homology); deferred until lower-risk operators are completed.",
        },
        {
            "candidate_id": "cand_005_heavy_tail",
            "operator_id": "HEAVY_TAIL",
            "proximity_to_completed_operators": "MEDIUM",
            "deterministic_fixture_feasibility": "MEDIUM",
            "schema_complexity": "MEDIUM",
            "numerical_stability_risk": "MEDIUM",
            "aal_viz_value": "LOW",
            "composite_rank": 5,
            "selection_status": "REJECTED",
            "rejection_reason": "Low AAL-Viz substrate value at current substrate maturity; deferred.",
        },
        {
            "candidate_id": "cand_006_hysteresis",
            "operator_id": "HYSTERESIS",
            "proximity_to_completed_operators": "LOW",
            "deterministic_fixture_feasibility": "MEDIUM",
            "schema_complexity": "MEDIUM",
            "numerical_stability_risk": "MEDIUM",
            "aal_viz_value": "LOW",
            "composite_rank": 6,
            "selection_status": "REJECTED",
            "rejection_reason": "Time-series memory operator; distant from spatial/transport substrate; deferred.",
        },
        {
            "candidate_id": "cand_007_stochastic_geometry",
            "operator_id": "STOCHASTIC_GEOMETRY",
            "proximity_to_completed_operators": "MEDIUM",
            "deterministic_fixture_feasibility": "LOW",
            "schema_complexity": "HIGH",
            "numerical_stability_risk": "HIGH",
            "aal_viz_value": "MEDIUM",
            "composite_rank": 7,
            "selection_status": "REJECTED",
            "rejection_reason": "Low deterministic fixture feasibility (stochastic nature requires seeded RNG policy); high schema complexity.",
        },
        {
            "candidate_id": "cand_008_reservoir_state_space",
            "operator_id": "RESERVOIR_STATE_SPACE",
            "proximity_to_completed_operators": "LOW",
            "deterministic_fixture_feasibility": "LOW",
            "schema_complexity": "HIGH",
            "numerical_stability_risk": "HIGH",
            "aal_viz_value": "LOW",
            "composite_rank": 8,
            "selection_status": "REJECTED",
            "rejection_reason": "Echo-state / liquid-state architecture; low proximity to completed spatial operators; very high schema and numerical complexity.",
        },
        {
            "candidate_id": "cand_009_hypervector_binding",
            "operator_id": "HYPERVECTOR_BINDING",
            "proximity_to_completed_operators": "LOW",
            "deterministic_fixture_feasibility": "MEDIUM",
            "schema_complexity": "HIGH",
            "numerical_stability_risk": "MEDIUM",
            "aal_viz_value": "LOW",
            "composite_rank": 9,
            "selection_status": "REJECTED",
            "rejection_reason": "Hyperdimensional computing operator; specialized domain with low substrate coverage value at current maturity.",
        },
        {
            "candidate_id": "cand_010_counterfactual_diffusion",
            "operator_id": "COUNTERFACTUAL_DIFFUSION",
            "proximity_to_completed_operators": "LOW",
            "deterministic_fixture_feasibility": "LOW",
            "schema_complexity": "HIGH",
            "numerical_stability_risk": "HIGH",
            "aal_viz_value": "LOW",
            "composite_rank": 10,
            "selection_status": "REJECTED",
            "rejection_reason": "Diffusion-based counterfactual operator; lowest feasibility and highest complexity; deferred until substrate is sufficiently mature.",
        },
    ]


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_metric_values": False,
        "emits_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_candidate_ranking": True,
    }


def _prov_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _prov_safe(x)
    elif isinstance(v, list):
        for x in v:
            _prov_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise MetricOperatorRank3CandidateAuditValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_metric_operator_rank3_candidate_audit(packet: dict[str, Any]) -> None:
    req = {
        "schema_version", "audit_id", "audit_type", "completed_operators",
        "candidate_entries", "recommended_rank3", "audit_status",
        "output_contract", "governance_flags", "provenance", "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise MetricOperatorRank3CandidateAuditValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise MetricOperatorRank3CandidateAuditValidationError("invalid_schema_version")
    if packet["audit_type"] != AUDIT_TYPE:
        raise MetricOperatorRank3CandidateAuditValidationError("invalid_audit_type")
    if packet["audit_status"] not in ALLOWED_AUDIT_STATUS:
        raise MetricOperatorRank3CandidateAuditValidationError("unknown_audit_status")
    if not packet.get("completed_operators"):
        raise MetricOperatorRank3CandidateAuditValidationError(
            "completed_operators_must_be_non_empty"
        )
    if not packet.get("candidate_entries"):
        raise MetricOperatorRank3CandidateAuditValidationError(
            "candidate_entries_must_be_non_empty"
        )

    seen_ids: set[str] = set()
    selected_count = 0
    for entry in packet["candidate_entries"]:
        cid = entry.get("candidate_id")
        if cid in seen_ids:
            raise MetricOperatorRank3CandidateAuditValidationError("duplicate_candidate_id")
        seen_ids.add(cid)
        for level_field in (
            "proximity_to_completed_operators", "deterministic_fixture_feasibility",
            "schema_complexity", "numerical_stability_risk", "aal_viz_value",
        ):
            if entry.get(level_field) not in ALLOWED_LEVEL:
                raise MetricOperatorRank3CandidateAuditValidationError(
                    f"unknown_level_value:{level_field}"
                )
        if entry.get("selection_status") not in ALLOWED_SELECTION_STATUS:
            raise MetricOperatorRank3CandidateAuditValidationError("unknown_selection_status")
        if entry.get("selection_status") == "SELECTED_RANK3":
            selected_count += 1

    if selected_count != 1:
        raise MetricOperatorRank3CandidateAuditValidationError(
            "exactly_one_candidate_must_be_selected_rank3"
        )

    selected = next(
        e for e in packet["candidate_entries"] if e.get("selection_status") == "SELECTED_RANK3"
    )
    if selected.get("operator_id") != packet["recommended_rank3"]:
        raise MetricOperatorRank3CandidateAuditValidationError(
            "recommended_rank3_must_match_selected_candidate_operator_id"
        )

    if packet["output_contract"] != default_output_contract():
        raise MetricOperatorRank3CandidateAuditValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise MetricOperatorRank3CandidateAuditValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_metric_operator_rank3_candidate_audit_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_metric_operator_rank3_candidate_audit(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_metric_operator_rank3_candidate_audit(payload: dict[str, Any]) -> dict[str, Any]:
    entries = sorted(
        payload.get("candidate_entries", default_candidate_entries()),
        key=lambda x: x["composite_rank"],
    )
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "audit_type": AUDIT_TYPE,
        "completed_operators": sorted(payload.get("completed_operators", [])),
        "candidate_entries": entries,
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_metric_operator_rank3_candidate_audit_hash(base)
    validate_metric_operator_rank3_candidate_audit(base)
    return _finalize(base)
