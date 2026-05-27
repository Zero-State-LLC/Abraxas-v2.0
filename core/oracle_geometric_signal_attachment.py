from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SURFACE_TYPES = {"ORACLE_SIGNAL_LAYER","ORACLE_SIGNAL_PACKET","ORACLE_SHADOW_PACKET","ORACLE_REPLAY_PACKET","ORACLE_INTAKE_PACKET","ORACLE_PROJECTION_PACKET"}
SURFACE_SCOPES = {"SHADOW","PROJECTION","REPLAY","INTAKE","OBSERVATION_ONLY"}
ATTACHMENT_MODES = {"SHADOW_METADATA_ONLY","PROJECTION_METADATA_ONLY","REPLAY_CONTEXT_ONLY","INTAKE_CONTEXT_ONLY","NOT_COMPUTABLE"}
_GOV_FALSE = ("production_activation","canon_promotion","scheduler_mutation","runtime_authority","runtime_mutation","forecast_influence","execution_authority","token_minting_allowed","valid_for_execution","activation_approved","authorization_granted")
_ORACLE_EFFECTS_FALSE = ("affects_oracle_scores","affects_forecast_probability","affects_forecast_routing","affects_outcome_binding","affects_pse_outputs","affects_runtime_routing","affects_scheduler","affects_canon","affects_operator_authority")
_SHADOW_TRUE = ("observation_only","promotion_blocked","forecast_lane_blocked","runtime_mutation_blocked","scheduler_mutation_blocked","canon_mutation_blocked","route_mutation_blocked","metric_computation_blocked")
_FORBIDDEN_TEXT = ("callable", "execute", "runtime", "scheduler", "cache", "forecast", "route-selection", "scoring", "outcome-binding")


def default_oracle_effects() -> dict[str, bool]:
    return {k: False for k in _ORACLE_EFFECTS_FALSE}


def default_shadow_constraints() -> dict[str, bool]:
    return {k: True for k in _SHADOW_TRUE}


def compute_oracle_geometric_signal_attachment_hash(packet_without_hash: dict[str, Any]) -> str:
    body = {k: v for k, v in packet_without_hash.items() if k != "canonical_hash"}
    return canonical_hash(body)


def validate_oracle_geometric_signal_attachment(packet: dict[str, Any]) -> None:
    if packet.get("attachment_type") != "ORACLE_GEOMETRIC_SIGNAL_ATTACHMENT":
        raise ValueError("attachment_type must be ORACLE_GEOMETRIC_SIGNAL_ATTACHMENT")
    ref = packet.get("oracle_surface_ref", {})
    if ref.get("surface_type") not in SURFACE_TYPES:
        raise ValueError("unknown surface_type")
    if ref.get("surface_scope") not in SURFACE_SCOPES:
        raise ValueError("unknown surface_scope")
    mode = packet.get("geometric_attachment_mode")
    if mode not in ATTACHMENT_MODES:
        raise ValueError("unknown geometric_attachment_mode")
    if mode != "NOT_COMPUTABLE" and not packet.get("source_signal_packet_refs"):
        raise ValueError("source_signal_packet_refs required unless mode is NOT_COMPUTABLE")

    effects = packet.get("oracle_effects", {})
    for key in _ORACLE_EFFECTS_FALSE:
        if effects.get(key) is not False:
            raise ValueError(f"oracle_effects.{key} must be false")

    shadow = packet.get("shadow_constraints", {})
    for key in _SHADOW_TRUE:
        if shadow.get(key) is not True:
            raise ValueError(f"shadow_constraints.{key} must be true")

    gov = packet.get("governance_flags", {})
    for key in _GOV_FALSE:
        if gov.get(key) is not False:
            raise ValueError(f"governance_flags.{key} must be false")

    prov = packet.get("provenance", {})
    text_fields = []
    for key in ("source", "generated_by"):
        val = prov.get(key)
        if isinstance(val, str):
            text_fields.append(val.lower())
    for item in prov.get("evidence_refs", []):
        if isinstance(item, str):
            text_fields.append(item.lower())
    blob = " ".join(text_fields)
    if any(term in blob for term in _FORBIDDEN_TEXT):
        raise ValueError("forbidden executable/runtime/scheduler/forecast/scoring/outcome-binding references")

    expected = compute_oracle_geometric_signal_attachment_hash(packet)
    if packet.get("canonical_hash") != expected:
        raise ValueError("canonical_hash mismatch")


def build_oracle_geometric_signal_attachment(*, attachment_id: str, oracle_surface_ref: dict[str, str], source_signal_packet_refs: list[str], source_metric_registry_refs: list[str], source_projection_refs: list[str], source_route_metadata_refs: list[str], attachment_summary: str, geometric_attachment_mode: str, provenance: dict[str, Any], created_at_utc: str, schema_version: str = "OracleGeometricSignalAttachment.v1") -> dict[str, Any]:
    packet_no_hash = {
        "schema_version": schema_version,
        "attachment_id": attachment_id,
        "attachment_type": "ORACLE_GEOMETRIC_SIGNAL_ATTACHMENT",
        "oracle_surface_ref": oracle_surface_ref,
        "source_signal_packet_refs": sorted(source_signal_packet_refs),
        "source_metric_registry_refs": sorted(source_metric_registry_refs),
        "source_projection_refs": sorted(source_projection_refs),
        "source_route_metadata_refs": sorted(source_route_metadata_refs),
        "attachment_summary": attachment_summary,
        "geometric_attachment_mode": geometric_attachment_mode,
        "oracle_effects": default_oracle_effects(),
        "shadow_constraints": default_shadow_constraints(),
        "governance_flags": {k: False for k in _GOV_FALSE},
        "provenance": provenance,
        "created_at_utc": created_at_utc,
    }
    packet = {**packet_no_hash, "canonical_hash": compute_oracle_geometric_signal_attachment_hash(packet_no_hash)}
    validate_oracle_geometric_signal_attachment(packet)
    return json.loads(canonical_dumps(packet))


def serialize_oracle_geometric_signal_attachment(packet: dict[str, Any]) -> str:
    validate_oracle_geometric_signal_attachment(packet)
    return canonical_dumps(packet) + "\n"
