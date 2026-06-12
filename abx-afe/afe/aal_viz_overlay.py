from __future__ import annotations

from typing import Any

from afe.oracle_annotation import build_oracle_annotation
from afe.provenance import stable_hash
from afe.real_world_mapping import build_batch004_mapping_packet
from afe.trace import AUTHORITY

OUTPUT_EFFECT = "VISUAL_ANNOTATION_ONLY"
MAX_OVERLAY_OPACITY = 0.6


def build_aal_viz_overlay_packet(
    *,
    batch004_packet: dict[str, Any] | None = None,
    oracle_annotation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    mapping_packet = batch004_packet or build_batch004_mapping_packet()
    annotation = oracle_annotation or build_oracle_annotation(batch004_packet=mapping_packet)
    raw_nodes = _raw_nodes(mapping_packet)
    raw_edges = _raw_edges(raw_nodes)
    packet = {
        "artifact_type": "AFEAALVizOverlayPacket.v1",
        "authority": AUTHORITY,
        "output_effect": OUTPUT_EFFECT,
        "projection_only": True,
        "non_filtering_compliance": True,
        "raw_layer": {
            "always_visible": True,
            "readable_at_all_times": True,
            "nodes": raw_nodes,
            "edges": raw_edges,
        },
        "overlay_layers": _overlay_layers(mapping_packet, annotation),
        "annotation_layer": {
            "required_labels": [
                "Observation Authority: SHADOW_ONLY_TRACE",
                "Output Effect: VISUAL_ANNOTATION_ONLY",
                "Non-Filtering Compliance: TRUE",
            ],
            "labels": annotation["afe_observation"]["labels"],
            "drift_flags": annotation["afe_observation"]["drift_flags"],
        },
        "rendering_locks": {
            "max_overlay_opacity": MAX_OVERLAY_OPACITY,
            "hide_nodes": False,
            "remove_edges": False,
            "collapse_clusters_invisibly": False,
            "auto_filter_high_risk_data": False,
            "visual_demotion_without_annotation": False,
        },
    }
    packet["provenance_hash"] = stable_hash(packet)
    return packet


def _raw_nodes(mapping_packet: dict[str, Any]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for observation in mapping_packet.get("observations", []):
        nodes.append(
            {
                "node_id": str(observation["observation_id"]),
                "label": str(observation["observed_topology"]),
                "source_domain": str(observation["source_domain"]),
                "afe_pattern_match": str(observation["afe_pattern_match"]),
                "raw_visible": True,
            }
        )
    return nodes


def _raw_edges(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for index in range(max(0, len(nodes) - 1)):
        edges.append(
            {
                "edge_id": f"raw-edge-{index + 1:03d}",
                "source": nodes[index]["node_id"],
                "target": nodes[index + 1]["node_id"],
                "raw_visible": True,
            }
        )
    return edges


def _overlay_layers(mapping_packet: dict[str, Any], annotation: dict[str, Any]) -> list[dict[str, Any]]:
    observations = mapping_packet.get("observations", [])
    labels = set(annotation["afe_observation"]["labels"])
    return [
        {
            "overlay_type": "drift heatmap",
            "opacity": 0.55,
            "source_observation_ids": _observation_ids_by_drift(observations, "DRIFT"),
            "annotation_required": True,
            "raw_layer_remains_visible": True,
        },
        {
            "overlay_type": "trust topology graph",
            "opacity": 0.45,
            "source_observation_ids": _observation_ids_by_pattern(
                observations,
                {"distributed_trust_meme", "recovery_meme_repair", "distributed_trust_recovery"},
            ),
            "annotation_required": True,
            "raw_layer_remains_visible": True,
        },
        {
            "overlay_type": "collapse probability shading",
            "opacity": 0.5,
            "source_observation_ids": _observation_ids_by_pattern(
                observations,
                {"authority_deception_meme", "false_alliance_authority", "scarcity_deception"},
            ),
            "annotation_required": True,
            "raw_layer_remains_visible": True,
        },
        {
            "overlay_type": "memetic propagation flow",
            "opacity": 0.4,
            "source_observation_ids": _observation_ids_by_label(labels, observations, "participatory meme loop"),
            "annotation_required": True,
            "raw_layer_remains_visible": True,
        },
        {
            "overlay_type": "alliance clusters",
            "opacity": 0.35,
            "source_observation_ids": _observation_ids_by_pattern(observations, {"false_alliance_authority"}),
            "annotation_required": True,
            "raw_layer_remains_visible": True,
        },
        {
            "overlay_type": "deception vectors",
            "opacity": 0.5,
            "source_observation_ids": _observation_ids_by_pattern(
                observations,
                {"authority_deception_meme", "scarcity_deception"},
            ),
            "annotation_required": True,
            "raw_layer_remains_visible": True,
        },
    ]


def _observation_ids_by_pattern(observations: list[dict[str, Any]], patterns: set[str]) -> list[str]:
    return [
        str(observation["observation_id"])
        for observation in observations
        if str(observation.get("afe_pattern_match")) in patterns
    ]


def _observation_ids_by_drift(observations: list[dict[str, Any]], prefix: str) -> list[str]:
    return [
        str(observation["observation_id"])
        for observation in observations
        if str(observation.get("drift_label", "")).startswith(prefix)
    ]


def _observation_ids_by_label(labels: set[str], observations: list[dict[str, Any]], label: str) -> list[str]:
    if label not in labels:
        return []
    return [str(observation["observation_id"]) for observation in observations]
