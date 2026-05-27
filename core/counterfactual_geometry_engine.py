from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

INTENDED_LANES = {"SHADOW", "REPLAY", "PROJECTION", "OBSERVATION_ONLY"}
BRANCH_FAMILIES = {"TEMPORAL_BRANCH", "CAUSAL_BRANCH", "SYMBOLIC_BRANCH", "GEOMETRIC_BRANCH", "MULTI_DOMAIN_BRANCH", "NOT_COMPUTABLE_BRANCH"}
BRANCH_TYPES = {"COUNTERFACTUAL_REFERENCE", "BASELINE_BRANCH", "PERTURBATION_BRANCH", "DIVERGENCE_BRANCH", "REPLAY_BRANCH", "PROJECTION_BRANCH", "NOT_COMPUTABLE_BRANCH"}
DECLARED_USES = {"BRANCH_CONTEXT", "DIVERGENCE_CONTEXT", "TEMPORAL_CONTEXT", "CAUSAL_CONTEXT", "PROJECTION_CONTEXT", "BASELINE_COMPARISON_CONTEXT", "NOT_COMPUTABLE_CONTEXT"}
EVIDENCE_REQUIRED = {"BASELINE_COMPARATOR_REQUIRED", "SOURCE_PACKET_REF_REQUIRED", "REPLAY_VALIDATION_REQUIRED", "PROVENANCE_REF_REQUIRED", "SHADOW_OBSERVATION_REQUIRED", "NO_RUNTIME_EFFECT_REQUIRED"}
IMPLEMENTATION_STATUSES = {"DECLARED_ONLY", "METADATA_ONLY", "NOT_IMPLEMENTED", "SHADOW_STUB_ONLY"}
COMPUTATION_STATUSES = IMPLEMENTATION_STATUSES
_GOV_FALSE = ("production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation", "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted")
_GEOMETRY_POLICY = {"geometry_declared": True, "geometry_computed": False, "metric_distance_computed": False, "route_geometry_computed": False, "manifold_projection_computed": False}
_DIFFUSION_POLICY = {"diffusion_declared": True, "diffusion_computed": False, "smoothing_computed": False, "generated_scenarios": False, "probability_updated": False}
_COMPARISON_POLICY = {"comparison_declared": True, "comparison_computed": False, "baseline_required": True, "replay_validation_required": True, "affects_forecast": False, "affects_runtime": False, "affects_routing": False, "affects_scheduler": False}
_OUTPUT_CONTRACT = {"emits_branch_scores": False, "emits_scenario_outputs": False, "emits_probability_updates": False, "emits_context_labels": True, "emits_observation_notes": True, "emits_forecast_inputs": False, "emits_runtime_controls": False, "emits_authority_tokens": False}
_FORBIDDEN_TEXT = ("callable", "execute", "runtime", "scheduler", "cache", "forecast", "scoring", "probability", "route-selection", "scenario-generation")


def default_branch_declarations() -> list[dict[str, Any]]:
    return [
        {
            "branch_id": "CGE-BRANCH-BASELINE",
            "branch_type": "BASELINE_BRANCH",
            "description": "Baseline branch declaration for metadata-only counterfactual context.",
            "declared_use": "BASELINE_COMPARISON_CONTEXT",
            "evidence_required": ["BASELINE_COMPARATOR_REQUIRED", "NO_RUNTIME_EFFECT_REQUIRED"],
            "implementation_status": "DECLARED_ONLY",
        }
    ]


def default_geometry_policy() -> dict[str, bool]:
    return dict(_GEOMETRY_POLICY)


def default_diffusion_policy() -> dict[str, bool]:
    return dict(_DIFFUSION_POLICY)


def default_comparison_policy() -> dict[str, bool]:
    return dict(_COMPARISON_POLICY)


def default_output_contract() -> dict[str, bool]:
    return dict(_OUTPUT_CONTRACT)


def compute_counterfactual_geometry_engine_hash(packet_without_hash: dict[str, Any]) -> str:
    body = {k: v for k, v in packet_without_hash.items() if k != "canonical_hash"}
    return canonical_hash(body)


def validate_counterfactual_geometry_engine(packet: dict[str, Any]) -> None:
    if packet.get("engine_type") != "COUNTERFACTUAL_GEOMETRY_ENGINE":
        raise ValueError("engine_type must be COUNTERFACTUAL_GEOMETRY_ENGINE")

    scope = packet.get("counterfactual_scope", {})
    if scope.get("intended_lane") not in INTENDED_LANES:
        raise ValueError("unknown intended_lane")
    if scope.get("branch_family") not in BRANCH_FAMILIES:
        raise ValueError("unknown branch_family")

    declarations = packet.get("branch_declarations", [])
    if not declarations:
        raise ValueError("branch_declarations must be non-empty")
    branch_ids = [d.get("branch_id") for d in declarations]
    if len(branch_ids) != len(set(branch_ids)):
        raise ValueError("duplicate branch_id")
    for declaration in declarations:
        if declaration.get("branch_type") not in BRANCH_TYPES:
            raise ValueError("unknown branch_type")
        if declaration.get("declared_use") not in DECLARED_USES:
            raise ValueError("unknown declared_use")
        if declaration.get("implementation_status") not in IMPLEMENTATION_STATUSES:
            raise ValueError("unknown implementation_status")
        for evidence in declaration.get("evidence_required", []):
            if evidence not in EVIDENCE_REQUIRED:
                raise ValueError("unknown evidence_required")

    for policy_name, policy_value, expected in (
        ("geometry_policy", packet.get("geometry_policy", {}), _GEOMETRY_POLICY),
        ("diffusion_policy", packet.get("diffusion_policy", {}), _DIFFUSION_POLICY),
        ("comparison_policy", packet.get("comparison_policy", {}), _COMPARISON_POLICY),
        ("output_contract", packet.get("output_contract", {}), _OUTPUT_CONTRACT),
    ):
        for key, expected_value in expected.items():
            if policy_value.get(key) is not expected_value:
                raise ValueError(f"{policy_name}.{key} must be {str(expected_value).lower()}")

    if packet.get("computation_status") not in COMPUTATION_STATUSES:
        raise ValueError("unknown computation_status")

    gov = packet.get("governance_flags", {})
    for key in _GOV_FALSE:
        if gov.get(key) is not False:
            raise ValueError(f"governance_flags.{key} must be false")

    prov = packet.get("provenance", {})
    blob_parts: list[str] = []
    for key in ("source", "generated_by"):
        value = prov.get(key)
        if isinstance(value, str):
            blob_parts.append(value.lower())
    for item in prov.get("evidence_refs", []):
        if isinstance(item, str):
            blob_parts.append(item.lower())
    blob = " ".join(blob_parts)
    if any(term in blob for term in _FORBIDDEN_TEXT):
        raise ValueError("forbidden executable/runtime/scheduler/forecast/scoring/probability/route-selection/scenario-generation references")

    expected_hash = compute_counterfactual_geometry_engine_hash(packet)
    if packet.get("canonical_hash") != expected_hash:
        raise ValueError("canonical_hash mismatch")


def build_counterfactual_geometry_engine(*, engine_id: str, source_attachment_refs: list[str], source_signal_packet_refs: list[str], source_metric_registry_refs: list[str], source_projection_refs: list[str], source_route_metadata_refs: list[str], counterfactual_scope: dict[str, str], branch_declarations: list[dict[str, Any]], computation_status: str, provenance: dict[str, Any], created_at_utc: str, schema_version: str = "CounterfactualGeometryEngine.v1") -> dict[str, Any]:
    normalized_branches = []
    for branch in branch_declarations:
        normalized_branches.append({**branch, "evidence_required": sorted(branch.get("evidence_required", []))})

    packet_no_hash = {
        "schema_version": schema_version,
        "engine_id": engine_id,
        "engine_type": "COUNTERFACTUAL_GEOMETRY_ENGINE",
        "source_attachment_refs": sorted(source_attachment_refs),
        "source_signal_packet_refs": sorted(source_signal_packet_refs),
        "source_metric_registry_refs": sorted(source_metric_registry_refs),
        "source_projection_refs": sorted(source_projection_refs),
        "source_route_metadata_refs": sorted(source_route_metadata_refs),
        "counterfactual_scope": counterfactual_scope,
        "branch_declarations": sorted(normalized_branches, key=lambda item: str(item.get("branch_id", ""))),
        "geometry_policy": default_geometry_policy(),
        "diffusion_policy": default_diffusion_policy(),
        "comparison_policy": default_comparison_policy(),
        "output_contract": default_output_contract(),
        "computation_status": computation_status,
        "governance_flags": {k: False for k in _GOV_FALSE},
        "provenance": provenance,
        "created_at_utc": created_at_utc,
    }
    packet = {**packet_no_hash, "canonical_hash": compute_counterfactual_geometry_engine_hash(packet_no_hash)}
    validate_counterfactual_geometry_engine(packet)
    return json.loads(canonical_dumps(packet))


def serialize_counterfactual_geometry_engine(packet: dict[str, Any]) -> str:
    validate_counterfactual_geometry_engine(packet)
    return canonical_dumps(packet) + "\n"
