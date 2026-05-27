from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

OPERATOR_IDS = (
    "WASSERSTEIN","CHAMFER","GEODESIC","NORM_GEOMETRY","TRANSPORT","HYPERVECTOR_BINDING",
    "RESERVOIR_STATE_SPACE","COUNTERFACTUAL_DIFFUSION","HEAVY_TAIL","HYSTERESIS",
    "STOCHASTIC_GEOMETRY","TOPOLOGICAL_PRIMITIVES",
)
OPERATOR_FAMILIES = {
    "TRANSPORT_METRIC","SPATIAL_ALIGNMENT","GEODESIC_TOPOLOGY","NORM_GEOMETRY","SYMBOLIC_BINDING",
    "STATE_SPACE_DIAGNOSTIC","COUNTERFACTUAL_GEOMETRY","DISTRIBUTION_TAIL_ANALYSIS",
    "PATH_DEPENDENT_MEMORY","STOCHASTIC_SPATIAL_FIELD","TOPOLOGICAL_FEATURE_EXTRACTION",
}
COMPUTATION_STATUSES = {"DECLARED_ONLY","NOT_IMPLEMENTED","SHADOW_STUB_ONLY"}
IMPLEMENTATION_STATUSES = {"RESEARCH_METADATA_ONLY","SCHEMA_DECLARED","SHADOW_READY_PENDING_TESTS"}
ARCH_TARGETS = {
    "ORACLE_SIGNAL_LAYER","AAL_VIZ","YGGDRASIL","ABX_RUNES","P27_P28_TEMPORAL_CONTINUITY",
    "RESERVOIR_RUNTIME","PROJECTION_RUNTIME","DRIFT_DETECTION","SIGNAL_COMPRESSION",
    "MULTI_DOMAIN_ANALYSIS","GEOMETRIC_INTELLIGENCE_RUNTIME",
}
REQ_EVIDENCE = {"RESEARCH_ITEM_REF","GEOMETRIC_SIGNAL_PACKET_REF","PROVENANCE_REF","REPLAY_VALIDATION_REQUIRED","BASELINE_COMPARATOR_REQUIRED","SHADOW_OBSERVATION_REQUIRED"}
_GOV_FALSE = ("production_activation","canon_promotion","scheduler_mutation","runtime_authority","runtime_mutation","forecast_influence","execution_authority","token_minting_allowed","valid_for_execution","activation_approved","authorization_granted")
_FORBIDDEN_TEXT_KEYS = ("callable", "execute", "runtime", "scheduler", "forecast", "route")


def default_metric_operator_entries() -> list[dict[str, Any]]:
    mapping = {
        "WASSERSTEIN": "TRANSPORT_METRIC", "CHAMFER": "SPATIAL_ALIGNMENT", "GEODESIC": "GEODESIC_TOPOLOGY",
        "NORM_GEOMETRY": "NORM_GEOMETRY", "TRANSPORT": "TRANSPORT_METRIC", "HYPERVECTOR_BINDING": "SYMBOLIC_BINDING",
        "RESERVOIR_STATE_SPACE": "STATE_SPACE_DIAGNOSTIC", "COUNTERFACTUAL_DIFFUSION": "COUNTERFACTUAL_GEOMETRY",
        "HEAVY_TAIL": "DISTRIBUTION_TAIL_ANALYSIS", "HYSTERESIS": "PATH_DEPENDENT_MEMORY",
        "STOCHASTIC_GEOMETRY": "STOCHASTIC_SPATIAL_FIELD", "TOPOLOGICAL_PRIMITIVES": "TOPOLOGICAL_FEATURE_EXTRACTION",
    }
    ops = []
    for op in sorted(OPERATOR_IDS):
        ops.append({
            "operator_id": op,
            "operator_name": op.title().replace("_", " "),
            "operator_family": mapping[op],
            "description": f"Metadata declaration for {op} operator.",
            "allowed_domains": ["geometric_intelligence_runtime"],
            "input_shape_descriptor": "metadata-only",
            "output_descriptor": "metadata-only declaration",
            "computation_status": "DECLARED_ONLY",
            "shadow_only": True,
            "allowed_architecture_targets": ["ORACLE_SIGNAL_LAYER", "GEOMETRIC_INTELLIGENCE_RUNTIME"],
            "required_evidence": ["RESEARCH_ITEM_REF", "GEOMETRIC_SIGNAL_PACKET_REF", "SHADOW_OBSERVATION_REQUIRED"],
            "risk_notes": ["No computation implemented in this registry."],
            "implementation_status": "SCHEMA_DECLARED",
        })
    return ops


def compute_metric_operator_registry_hash(packet_without_hash: dict[str, Any]) -> str:
    body = {k: v for k, v in packet_without_hash.items() if k != "canonical_hash"}
    return canonical_hash(body)


def validate_metric_operator_registry(packet: dict[str, Any]) -> None:
    if packet.get("registry_type") != "METRIC_OPERATOR_REGISTRY":
        raise ValueError("registry_type must be METRIC_OPERATOR_REGISTRY")
    seen: set[str] = set()
    for op in packet.get("operators", []):
        op_id = op.get("operator_id")
        if op_id not in OPERATOR_IDS:
            raise ValueError("unknown operator_id")
        if op_id in seen:
            raise ValueError("duplicate operator_id")
        seen.add(op_id)
        if op.get("operator_family") not in OPERATOR_FAMILIES:
            raise ValueError("unknown operator_family")
        if op.get("computation_status") not in COMPUTATION_STATUSES:
            raise ValueError("unknown computation_status")
        if op.get("implementation_status") not in IMPLEMENTATION_STATUSES:
            raise ValueError("unknown implementation_status")
        if op.get("shadow_only") is not True:
            raise ValueError("shadow_only must be true")
        if any(t not in ARCH_TARGETS for t in op.get("allowed_architecture_targets", [])):
            raise ValueError("unknown architecture target")
        if any(e not in REQ_EVIDENCE for e in op.get("required_evidence", [])):
            raise ValueError("unknown required evidence")
        for key in _FORBIDDEN_TEXT_KEYS:
            if key in json.dumps(op, sort_keys=True).lower() and key in (op.get("description","")+" "+" ".join(op.get("risk_notes",[]))).lower():
                raise ValueError("forbidden executable/runtime/scheduler/forecast/route reference")
    if seen != set(OPERATOR_IDS):
        raise ValueError("default registry must contain exactly all allowed operator IDs")

    gov = packet.get("governance_flags", {})
    for key in _GOV_FALSE:
        if gov.get(key) is not False:
            raise ValueError(f"governance_flags.{key} must be false")

    expected = compute_metric_operator_registry_hash(packet)
    if packet.get("canonical_hash") != expected:
        raise ValueError("canonical_hash mismatch")


def build_metric_operator_registry(*, registry_id: str, provenance: dict[str, Any], created_at_utc: str, operators: list[dict[str, Any]] | None = None, schema_version: str = "MetricOperatorRegistry.v1") -> dict[str, Any]:
    ops = operators if operators is not None else default_metric_operator_entries()
    packet_no_hash = {
        "schema_version": schema_version,
        "registry_id": registry_id,
        "registry_type": "METRIC_OPERATOR_REGISTRY",
        "operators": sorted(ops, key=lambda x: x["operator_id"]),
        "governance_flags": {k: False for k in _GOV_FALSE},
        "provenance": provenance,
        "created_at_utc": created_at_utc,
    }
    packet = {**packet_no_hash, "canonical_hash": compute_metric_operator_registry_hash(packet_no_hash)}
    validate_metric_operator_registry(packet)
    return json.loads(canonical_dumps(packet))


def serialize_metric_operator_registry(packet: dict[str, Any]) -> str:
    validate_metric_operator_registry(packet)
    return canonical_dumps(packet) + "\n"
