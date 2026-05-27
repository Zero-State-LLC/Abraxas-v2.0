from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SURFACE_FAMILIES = {
    "MANIFOLD_TRANSPORT","METRIC_DISTANCE_PANEL","HYSTERESIS_MEMORY","COUNTERFACTUAL_BRANCHING",
    "HEAVY_TAIL_ANOMALY","RESERVOIR_STATE_SPACE","HYPERVECTOR_TOPOLOGY","TRUST_GEOMETRY",
    "PHASE_STATE_TRANSITION","YGGDRASIL_ROUTE_OVERLAY",
}
METRIC_PLACEHOLDERS = {
    "WASSERSTEIN","CHAMFER","GEODESIC","NORM_GEOMETRY","TRANSPORT","HYPERVECTOR_BINDING",
    "RESERVOIR_STATE_SPACE","COUNTERFACTUAL_DIFFUSION","HEAVY_TAIL","HYSTERESIS",
    "STOCHASTIC_GEOMETRY","TOPOLOGICAL_PRIMITIVES",
}
ARCH_TARGETS = {
    "AAL_VIZ","ORACLE_SIGNAL_LAYER","YGGDRASIL","PROJECTION_RUNTIME","DRIFT_DETECTION",
    "SIGNAL_COMPRESSION","GEOMETRIC_INTELLIGENCE_RUNTIME","P27_P28_TEMPORAL_CONTINUITY",
}
PROJ_STATUS = {"DECLARED_ONLY","PROJECTION_METADATA_ONLY","SHADOW_READY_PENDING_RENDERER"}
RENDER_STATUS = {"NOT_RENDERED","RENDERER_NOT_IMPLEMENTED","SPEC_ONLY"}
INTERACTION_STATUS = {"NON_INTERACTIVE","OPERATOR_VIEW_ONLY","INTERACTION_NOT_IMPLEMENTED"}
_GOV_FALSE = ("production_activation","canon_promotion","scheduler_mutation","runtime_authority","runtime_mutation","forecast_influence","execution_authority","token_minting_allowed","valid_for_execution","activation_approved","authorization_granted")


def default_projection_surface_entries() -> list[dict[str, Any]]:
    surfaces = []
    for fam in sorted(SURFACE_FAMILIES):
        surfaces.append({
            "surface_id": f"GPS-{fam.lower()}",
            "surface_name": fam.replace("_", " ").title(),
            "surface_family": fam,
            "description": f"Projection metadata surface for {fam}.",
            "source_metric_placeholders": ["WASSERSTEIN", "GEODESIC"],
            "architecture_targets": ["AAL_VIZ", "GEOMETRIC_INTELLIGENCE_RUNTIME"],
            "projection_status": "PROJECTION_METADATA_ONLY",
            "render_status": "SPEC_ONLY",
            "interaction_status": "NON_INTERACTIVE",
            "risk_notes": ["Renderer not implemented in this patch."],
        })
    return surfaces


def compute_geometric_projection_spec_hash(packet_without_hash: dict[str, Any]) -> str:
    body = {k: v for k, v in packet_without_hash.items() if k != "canonical_hash"}
    return canonical_hash(body)


def validate_geometric_projection_spec(packet: dict[str, Any]) -> None:
    if packet.get("projection_type") != "GEOMETRIC_PROJECTION_SPEC":
        raise ValueError("projection_type must be GEOMETRIC_PROJECTION_SPEC")
    surfaces = packet.get("projection_surfaces", [])
    if not surfaces:
        raise ValueError("projection_surfaces must be non-empty")
    seen: set[str] = set()
    for s in surfaces:
        sid = s.get("surface_id")
        if sid in seen:
            raise ValueError("duplicate surface_id")
        seen.add(sid)
        if s.get("surface_family") not in SURFACE_FAMILIES:
            raise ValueError("unknown surface_family")
        if any(m not in METRIC_PLACEHOLDERS for m in s.get("source_metric_placeholders", [])):
            raise ValueError("unknown metric placeholder")
        if any(a not in ARCH_TARGETS for a in s.get("architecture_targets", [])):
            raise ValueError("unknown architecture target")
        if s.get("projection_status") not in PROJ_STATUS:
            raise ValueError("unknown projection_status")
        if s.get("render_status") not in RENDER_STATUS:
            raise ValueError("unknown render_status")
        if s.get("interaction_status") not in INTERACTION_STATUS:
            raise ValueError("unknown interaction_status")

    interaction = packet.get("interaction_model", {})
    required_true = ("operator_view_only", "no_runtime_controls", "no_scheduler_controls", "no_forecast_controls", "no_activation_controls")
    for key in required_true:
        if interaction.get(key) is not True:
            raise ValueError(f"interaction_model.{key} must be true")

    gov = packet.get("governance_flags", {})
    for key in _GOV_FALSE:
        if gov.get(key) is not False:
            raise ValueError(f"governance_flags.{key} must be false")

    expected = compute_geometric_projection_spec_hash(packet)
    if packet.get("canonical_hash") != expected:
        raise ValueError("canonical_hash mismatch")


def build_geometric_projection_spec(*, projection_id: str, source_packet_refs: list[str], source_registry_refs: list[str], visual_encoding: dict[str, str], provenance: dict[str, Any], created_at_utc: str, projection_surfaces: list[dict[str, Any]] | None = None, schema_version: str = "GeometricProjectionSpec.v1") -> dict[str, Any]:
    surfaces = projection_surfaces if projection_surfaces is not None else default_projection_surface_entries()
    packet_no_hash = {
        "schema_version": schema_version,
        "projection_id": projection_id,
        "projection_type": "GEOMETRIC_PROJECTION_SPEC",
        "source_packet_refs": source_packet_refs,
        "source_registry_refs": source_registry_refs,
        "projection_surfaces": sorted(surfaces, key=lambda s: s["surface_id"]),
        "visual_encoding": visual_encoding,
        "interaction_model": {
            "operator_view_only": True,
            "no_runtime_controls": True,
            "no_scheduler_controls": True,
            "no_forecast_controls": True,
            "no_activation_controls": True,
        },
        "governance_flags": {k: False for k in _GOV_FALSE},
        "provenance": provenance,
        "created_at_utc": created_at_utc,
    }
    packet = {**packet_no_hash, "canonical_hash": compute_geometric_projection_spec_hash(packet_no_hash)}
    validate_geometric_projection_spec(packet)
    return json.loads(canonical_dumps(packet))


def serialize_geometric_projection_spec(packet: dict[str, Any]) -> str:
    validate_geometric_projection_spec(packet)
    return canonical_dumps(packet) + "\n"
