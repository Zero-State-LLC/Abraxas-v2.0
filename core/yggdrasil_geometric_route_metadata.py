from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

ROUTE_SCOPES = {"ROUTE_GRAPH","ROUTE_NODE","ROUTE_EDGE","ROUTE_PACKET","REPLAY_TRACE","SHADOW_ANALYSIS"}
ANNOTATION_VALUES = {"ABSENT","DECLARED","OBSERVED","SHADOW_ONLY","PROJECTION_ONLY","NOT_COMPUTABLE"}
METRIC_OPERATOR_IDS = {"WASSERSTEIN","CHAMFER","GEODESIC","NORM_GEOMETRY","TRANSPORT","HYPERVECTOR_BINDING","RESERVOIR_STATE_SPACE","COUNTERFACTUAL_DIFFUSION","HEAVY_TAIL","HYSTERESIS","STOCHASTIC_GEOMETRY","TOPOLOGICAL_PRIMITIVES"}
_GEO_KEYS = ("manifold_context","transport_context","phase_state_context","uncertainty_context","curvature_context")
_TOPO_KEYS = ("node_topology","edge_topology","graph_topology","defect_topology","hysteresis_topology","hypervector_topology")
_GOV_FALSE = ("production_activation","canon_promotion","scheduler_mutation","runtime_authority","runtime_mutation","forecast_influence","execution_authority","token_minting_allowed","valid_for_execution","activation_approved","authorization_granted")
_ROUTE_EFFECTS_FALSE = ("affects_route_selection","affects_route_scoring","affects_scheduler","affects_cache","affects_runtime_dispatch","affects_forecast","affects_operator_authority")
_FORBIDDEN_TEXT = ("callable", "execute", "runtime dispatch", "scheduler", "cache mutation", "forecast", "route selection", "route scoring")


def default_absent_geometric_annotations() -> dict[str, str]:
    return {k: "ABSENT" for k in _GEO_KEYS}


def default_absent_topology_annotations() -> dict[str, str]:
    return {k: "ABSENT" for k in _TOPO_KEYS}


def compute_yggdrasil_geometric_route_metadata_hash(packet_without_hash: dict[str, Any]) -> str:
    body = {k: v for k, v in packet_without_hash.items() if k != "canonical_hash"}
    return canonical_hash(body)


def _all_absent_or_not_computable(values: list[str]) -> bool:
    return all(v in {"ABSENT", "NOT_COMPUTABLE"} for v in values)


def validate_yggdrasil_geometric_route_metadata(packet: dict[str, Any]) -> None:
    if packet.get("metadata_type") != "YGGDRASIL_GEOMETRIC_ROUTE_METADATA":
        raise ValueError("metadata_type must be YGGDRASIL_GEOMETRIC_ROUTE_METADATA")

    route_ref = packet.get("route_ref", {})
    if route_ref.get("route_scope") not in ROUTE_SCOPES:
        raise ValueError("unknown route_scope")

    geo = packet.get("geometric_annotations", {})
    topo = packet.get("topology_annotations", {})
    for key in _GEO_KEYS:
        if geo.get(key) not in ANNOTATION_VALUES:
            raise ValueError("unknown geometric annotation enum")
    for key in _TOPO_KEYS:
        if topo.get(key) not in ANNOTATION_VALUES:
            raise ValueError("unknown topology annotation enum")

    refs = packet.get("metric_operator_refs", [])
    if any(r not in METRIC_OPERATOR_IDS for r in refs):
        raise ValueError("unknown metric operator ref")
    annotation_values = [geo[k] for k in _GEO_KEYS] + [topo[k] for k in _TOPO_KEYS]
    if not refs and not _all_absent_or_not_computable(annotation_values):
        raise ValueError("non-absent annotations require metric_operator_refs")

    route_effects = packet.get("route_effects", {})
    for key in _ROUTE_EFFECTS_FALSE:
        if route_effects.get(key) is not False:
            raise ValueError(f"route_effects.{key} must be false")

    gov = packet.get("governance_flags", {})
    for key in _GOV_FALSE:
        if gov.get(key) is not False:
            raise ValueError(f"governance_flags.{key} must be false")

    text_fields = []
    prov = packet.get("provenance", {})
    for key in ("source", "generated_by"):
        val = prov.get(key)
        if isinstance(val, str):
            text_fields.append(val.lower())
    for item in prov.get("evidence_refs", []):
        if isinstance(item, str):
            text_fields.append(item.lower())
    blob = " ".join(text_fields)
    if any(term in blob for term in _FORBIDDEN_TEXT):
        raise ValueError("forbidden executable/callable/runtime/scheduler/cache/forecast/route-selection references")

    expected = compute_yggdrasil_geometric_route_metadata_hash(packet)
    if packet.get("canonical_hash") != expected:
        raise ValueError("canonical_hash mismatch")


def build_yggdrasil_geometric_route_metadata(*, metadata_id: str, route_ref: dict[str, str], source_packet_refs: list[str], source_registry_refs: list[str], geometric_annotations: dict[str, str] | None, topology_annotations: dict[str, str] | None, metric_operator_refs: list[str], projection_refs: list[str], provenance: dict[str, Any], created_at_utc: str, schema_version: str = "YggdrasilGeometricRouteMetadata.v1") -> dict[str, Any]:
    packet_no_hash = {
        "schema_version": schema_version,
        "metadata_id": metadata_id,
        "metadata_type": "YGGDRASIL_GEOMETRIC_ROUTE_METADATA",
        "route_ref": route_ref,
        "source_packet_refs": sorted(source_packet_refs),
        "source_registry_refs": sorted(source_registry_refs),
        "geometric_annotations": geometric_annotations if geometric_annotations is not None else default_absent_geometric_annotations(),
        "topology_annotations": topology_annotations if topology_annotations is not None else default_absent_topology_annotations(),
        "metric_operator_refs": sorted(metric_operator_refs),
        "projection_refs": sorted(projection_refs),
        "route_effects": {k: False for k in _ROUTE_EFFECTS_FALSE},
        "governance_flags": {k: False for k in _GOV_FALSE},
        "provenance": provenance,
        "created_at_utc": created_at_utc,
    }
    packet = {**packet_no_hash, "canonical_hash": compute_yggdrasil_geometric_route_metadata_hash(packet_no_hash)}
    validate_yggdrasil_geometric_route_metadata(packet)
    return json.loads(canonical_dumps(packet))


def serialize_yggdrasil_geometric_route_metadata(packet: dict[str, Any]) -> str:
    validate_yggdrasil_geometric_route_metadata(packet)
    return canonical_dumps(packet) + "\n"
