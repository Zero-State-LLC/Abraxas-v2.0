from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_hash, canonical_dumps

CLASSIFICATIONS = {
    "SHADOW_ONLY",
    "PROJECTION_ONLY",
    "VISUALIZATION_READY",
    "GOVERNANCE_SENSITIVE",
    "THEORY_ONLY",
}

ARCHITECTURE_TARGETS = {
    "ORACLE_SIGNAL_LAYER",
    "AAL_VIZ",
    "YGGDRASIL",
    "ABX_RUNES",
    "P27_P28_TEMPORAL_CONTINUITY",
    "RESERVOIR_RUNTIME",
    "PROJECTION_RUNTIME",
    "DRIFT_DETECTION",
    "SIGNAL_COMPRESSION",
    "MULTI_DOMAIN_ANALYSIS",
    "GEOMETRIC_INTELLIGENCE_RUNTIME",
}

METRIC_PLACEHOLDERS = {
    "WASSERSTEIN",
    "CHAMFER",
    "GEODESIC",
    "NORM_GEOMETRY",
    "TRANSPORT",
    "HYPERVECTOR_BINDING",
    "RESERVOIR_STATE_SPACE",
    "COUNTERFACTUAL_DIFFUSION",
    "HEAVY_TAIL",
    "HYSTERESIS",
    "STOCHASTIC_GEOMETRY",
    "TOPOLOGICAL_PRIMITIVES",
}

_GOV_FALSE = (
    "production_activation",
    "canon_promotion",
    "scheduler_mutation",
    "runtime_authority",
    "runtime_mutation",
    "forecast_influence",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "activation_approved",
    "authorization_granted",
)



def _validate(packet: dict[str, Any]) -> None:
    if packet.get("packet_type") != "GEOMETRIC_SIGNAL_PACKET":
        raise ValueError("packet_type must be GEOMETRIC_SIGNAL_PACKET")
    if packet.get("classification") not in CLASSIFICATIONS:
        raise ValueError("unknown classification")
    if not packet.get("source_research_item_ids"):
        raise ValueError("source_research_item_ids must be non-empty")
    if any(t not in ARCHITECTURE_TARGETS for t in packet.get("architecture_targets", [])):
        raise ValueError("unknown architecture target")
    if any(m not in METRIC_PLACEHOLDERS for m in packet.get("metric_placeholders", [])):
        raise ValueError("unknown metric placeholder")

    shadow = packet.get("shadow_observation", {})
    required_shadow = {
        "observation_only": True,
        "forecast_eligible": False,
        "affects_runtime_routing": False,
        "affects_scheduler": False,
        "affects_canon": False,
        "affects_operator_authority": False,
    }
    for key, expected in required_shadow.items():
        if shadow.get(key) is not expected:
            raise ValueError(f"shadow_observation.{key} must be {expected}")

    gov = packet.get("governance_flags", {})
    for key in _GOV_FALSE:
        if gov.get(key) is not False:
            raise ValueError(f"governance_flags.{key} must be false")


def compute_geometric_signal_packet_hash(packet_without_hash: dict[str, Any]) -> str:
    body = {k: v for k, v in packet_without_hash.items() if k != "canonical_hash"}
    return canonical_hash(body)


def canonicalize_geometric_signal_packet(packet: dict[str, Any]) -> dict[str, Any]:
    _validate(packet)
    body = {k: v for k, v in packet.items() if k != "canonical_hash"}
    hashed = {**body, "canonical_hash": compute_geometric_signal_packet_hash(body)}
    return json.loads(canonical_dumps(hashed))


def build_geometric_signal_packet(*, packet_id: str, source_research_item_ids: list[str], observed_signal_summary: str, geometric_concepts: list[str], metric_placeholders: list[str], architecture_targets: list[str], classification: str, provenance: dict[str, Any], created_at_utc: str, schema_version: str = "GeometricSignalPacket.v1") -> dict[str, Any]:
    packet = {
        "schema_version": schema_version,
        "packet_id": packet_id,
        "packet_type": "GEOMETRIC_SIGNAL_PACKET",
        "source_research_item_ids": source_research_item_ids,
        "observed_signal_summary": observed_signal_summary,
        "geometric_concepts": geometric_concepts,
        "metric_placeholders": metric_placeholders,
        "architecture_targets": architecture_targets,
        "classification": classification,
        "shadow_observation": {
            "observation_only": True,
            "forecast_eligible": False,
            "affects_runtime_routing": False,
            "affects_scheduler": False,
            "affects_canon": False,
            "affects_operator_authority": False,
        },
        "governance_flags": {k: False for k in _GOV_FALSE},
        "provenance": provenance,
        "created_at_utc": created_at_utc,
    }
    return canonicalize_geometric_signal_packet(packet)


def validate_geometric_signal_packet(packet: dict[str, Any]) -> None:
    _validate(packet)
    expected = compute_geometric_signal_packet_hash(packet)
    if packet.get("canonical_hash") != expected:
        raise ValueError("canonical_hash mismatch")


def serialize_geometric_signal_packet(packet: dict[str, Any]) -> str:
    validate_geometric_signal_packet(packet)
    return canonical_dumps(packet) + "\n"
