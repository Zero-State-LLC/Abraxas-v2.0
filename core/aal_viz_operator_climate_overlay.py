from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P35-AAL-VIZ-OPERATOR-CLIMATE-OVERLAY-001"
SCHEMA_VERSION = "AALVizOperatorClimateOverlay.v1"
OVERLAY_ID = "aal_viz_operator_climate_overlay_001"

NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "render_consumer_only": True,
    "non_authoritative": True,
    "inference_authority": False,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
    "forecast_authority": False,
    "routing_change_allowed": False,
    "queue_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "ui_command_authority": False,
    "adaptive_behavior_allowed": False,
    "psychological_claims_allowed": False,
    "speculative_causation_allowed": False,
    "trend_prediction_allowed": False,
    "readiness_claims_allowed": False,
    "auto_execute": False,
    "auto_approve": False,
    "command_channel": False,
    "bidirectional_control": False,
}


def _load_json(path: str | Path) -> tuple[dict[str, Any] | None, str]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "MISSING"
    except (OSError, json.JSONDecodeError):
        return None, "CORRUPT"
    if not isinstance(payload, dict):
        return None, "CORRUPT"
    return payload, "PRESENT"


def _src_paths(paths: RuntimePaths) -> dict[str, str]:
    return {
        "operator_attention_weather": paths.operator_attention_weather_latest.as_posix(),
        "operator_review_routing_enhancer": paths.operator_review_routing_enhancer_latest.as_posix(),
        "operator_attention_ledger": paths.operator_attention_ledger_latest.as_posix(),
        "operator_fatigue_corridor": paths.operator_fatigue_corridor_latest.as_posix(),
        "continuity_degradation_explainer": paths.continuity_degradation_explainer_latest.as_posix(),
        "operator_climatology_summary": paths.operator_climatology_summary_latest.as_posix(),
    }


def _mk_node(node_id: str, label: str, layer_id: str, posture: str, source_key: str) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "label": label,
        "layer_id": layer_id,
        "posture": posture,
        "source_key": source_key,
    }


def _mk_edge(source: str, target: str, relation: str) -> dict[str, Any]:
    edge_id = canonical_hash({"source": source, "target": target, "relation": relation})
    return {
        "edge_id": edge_id,
        "source_node_id": source,
        "target_node_id": target,
        "relation": relation,
    }


def build_aal_viz_operator_climate_overlay_packet(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    sources = source_artifact_paths or _src_paths(paths)

    loaded: dict[str, dict[str, Any] | None] = {}
    source_status: dict[str, str] = {}
    blockers: list[str] = []

    for key, path in sorted(sources.items()):
        payload, status = _load_json(path)
        loaded[key] = payload
        source_status[key] = status
        if status != "PRESENT":
            blockers.append(f"source_{status.lower()}:{key}")

    if source_packets:
        for key, payload in source_packets.items():
            loaded[key] = deepcopy(payload)
            source_status[key] = "PRESENT"

    weather = loaded.get("operator_attention_weather") or {}
    routing = loaded.get("operator_review_routing_enhancer") or {}
    ledger = loaded.get("operator_attention_ledger") or {}
    corridor = loaded.get("operator_fatigue_corridor") or {}
    explainer = loaded.get("continuity_degradation_explainer") or {}
    climatology = loaded.get("operator_climatology_summary") or {}

    for packet in (weather, routing, ledger, corridor, explainer, climatology):
        blockers.extend(str(b) for b in packet.get("blocker_summary", []) if str(b))
    blocker_summary = sorted(set(str(b).strip() for b in blockers if str(b).strip()))

    missing_or_corrupt = any(v != "PRESENT" for v in source_status.values())

    corridor_status = str(corridor.get("corridor_status", NOT_COMPUTABLE))
    corridor_final_status = str(corridor.get("final_status", NOT_COMPUTABLE))
    explainer_final_status = str(explainer.get("final_status", NOT_COMPUTABLE))
    climatology_final_status = str(climatology.get("final_status", NOT_COMPUTABLE))
    climatology_posture = str(climatology.get("climatology_posture", NOT_COMPUTABLE))

    if missing_or_corrupt:
        final_status = NOT_COMPUTABLE
        overlay_posture = NOT_COMPUTABLE
    elif BLOCKED in {corridor_final_status, explainer_final_status, climatology_final_status}:
        final_status = BLOCKED
        overlay_posture = BLOCKED
    elif corridor_status == "PRESSURE_PERSISTENCE" or corridor_final_status == "ADVISORY_DEGRADED" or climatology_final_status == "ADVISORY_DEGRADED":
        final_status = "PROJECTION_DEGRADED"
        overlay_posture = "PRESSURE_PERSISTENCE" if corridor_status == "PRESSURE_PERSISTENCE" else "DEGRADED"
    elif climatology_posture == "WATCH" or str(weather.get("weather_posture", "")) == "WATCH":
        final_status = "PROJECTION_ONLY"
        overlay_posture = "WATCH"
    else:
        final_status = "PROJECTION_ONLY"
        overlay_posture = "CLEAR"

    render_layers = sorted([
        {"layer_id": "climate_overview", "status": "PRESENT"},
        {"layer_id": "weather_state", "status": "PRESENT"},
        {"layer_id": "routing_state", "status": "PRESENT"},
        {"layer_id": "memory_state", "status": "PRESENT"},
        {"layer_id": "corridor_state", "status": "PRESENT"},
        {"layer_id": "degradation_vectors", "status": "PRESENT"},
        {"layer_id": "climatology_distribution", "status": "PRESENT"},
    ], key=lambda x: str(x["layer_id"]))

    overlay_nodes = sorted([
        _mk_node("node.weather", "Weather", "weather_state", str(weather.get("weather_posture", NOT_COMPUTABLE)), "operator_attention_weather"),
        _mk_node("node.routing", "Routing", "routing_state", str(routing.get("routing_posture", NOT_COMPUTABLE)), "operator_review_routing_enhancer"),
        _mk_node("node.ledger", "Ledger", "memory_state", str(ledger.get("ledger_posture", NOT_COMPUTABLE)), "operator_attention_ledger"),
        _mk_node("node.corridor", "Corridor", "corridor_state", corridor_status, "operator_fatigue_corridor"),
        _mk_node("node.explainer", "Explainer", "degradation_vectors", str(explainer.get("explanation_posture", NOT_COMPUTABLE)), "continuity_degradation_explainer"),
        _mk_node("node.climatology", "Climatology", "climatology_distribution", climatology_posture, "operator_climatology_summary"),
    ], key=lambda x: str(x["node_id"]))

    overlay_cards = sorted([
        {"card_id": "card.weather", "title": "Weather Posture", "value": str(weather.get("weather_posture", NOT_COMPUTABLE))},
        {"card_id": "card.routing", "title": "Routing Posture", "value": str(routing.get("routing_posture", NOT_COMPUTABLE))},
        {"card_id": "card.ledger", "title": "Ledger Posture", "value": str(ledger.get("ledger_posture", NOT_COMPUTABLE))},
        {"card_id": "card.corridor", "title": "Corridor Status", "value": corridor_status},
        {"card_id": "card.explainer", "title": "Degradation Vectors", "value": ",".join(str(v) for v in (explainer.get("dominant_degradation_vectors") or [])) or "none"},
        {"card_id": "card.climatology", "title": "Climatology Posture", "value": climatology_posture},
    ], key=lambda x: str(x["card_id"]))

    overlay_badges = sorted([
        {"badge_id": "badge.weather", "token": f"weather.{str(weather.get('weather_posture', NOT_COMPUTABLE)).lower()}"},
        {"badge_id": "badge.routing", "token": f"routing.{str(routing.get('routing_posture', NOT_COMPUTABLE)).lower()}"},
        {"badge_id": "badge.ledger", "token": f"ledger.{str(ledger.get('ledger_posture', NOT_COMPUTABLE)).lower()}"},
        {"badge_id": "badge.corridor", "token": f"corridor.{corridor_status.lower()}"},
        {"badge_id": "badge.overlay", "token": f"overlay.{overlay_posture.lower()}"},
    ], key=lambda x: str(x["badge_id"]))

    overlay_edges = sorted([
        _mk_edge("node.weather", "node.routing", "influences"),
        _mk_edge("node.routing", "node.ledger", "materializes"),
        _mk_edge("node.ledger", "node.corridor", "feeds"),
        _mk_edge("node.corridor", "node.explainer", "explained_by"),
        _mk_edge("node.explainer", "node.climatology", "aggregated_into"),
    ], key=lambda x: str(x["edge_id"]))

    source_hashes = {k: (str(canonical_hash(v)) if isinstance(v, dict) else NOT_COMPUTABLE) for k, v in sorted(loaded.items())}
    climate_summary = {
        "weather_posture": str(weather.get("weather_posture", NOT_COMPUTABLE)),
        "routing_posture": str(routing.get("routing_posture", NOT_COMPUTABLE)),
        "ledger_posture": str(ledger.get("ledger_posture", NOT_COMPUTABLE)),
        "corridor_status": corridor_status,
        "degradation_vectors": sorted(str(v) for v in (explainer.get("dominant_degradation_vectors") or [])),
        "climatology_counts": {
            "weather_posture_counts": deepcopy(climatology.get("weather_posture_counts", {})),
            "attention_urgency_counts": deepcopy(climatology.get("attention_urgency_counts", {})),
            "routing_posture_counts": deepcopy(climatology.get("routing_posture_counts", {})),
            "review_priority_posture_counts": deepcopy(climatology.get("review_priority_posture_counts", {})),
            "ledger_posture_counts": deepcopy(climatology.get("ledger_posture_counts", {})),
            "corridor_status_counts": deepcopy(climatology.get("corridor_status_counts", {})),
            "degradation_vector_counts": deepcopy(climatology.get("degradation_vector_counts", {})),
            "blocker_class_counts": deepcopy(climatology.get("blocker_class_counts", {})),
        },
        "source_hash_lineage": deepcopy(climatology.get("source_hash_lineage", {})),
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "overlay_id": OVERLAY_ID,
        "final_status": final_status,
        "overlay_posture": overlay_posture,
        "render_layers": render_layers,
        "overlay_nodes": overlay_nodes,
        "overlay_cards": overlay_cards,
        "overlay_badges": overlay_badges,
        "overlay_edges": overlay_edges,
        "climate_summary": climate_summary,
        "source_artifacts": sources,
        "source_hashes": source_hashes,
        "blocker_summary": blocker_summary,
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": source_status,
            "deterministic": True,
            "projection_only": True,
            "advisory_only": True,
            "render_consumer_only": True,
        },
    }
    packet["overlay_hash"] = canonical_hash(packet)
    return packet


def build_aal_viz_operator_climate_overlay_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P35 AAL-Viz Operator Climate Overlay",
        "",
        f"- overlay_id: `{packet['overlay_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- overlay_posture: `{packet['overlay_posture']}`",
        "",
        "## Render Layers",
    ]
    lines.extend(f"- `{item['layer_id']}`" for item in packet.get("render_layers", []))
    lines.append("")
    lines.append("## Blockers")
    blockers = packet.get("blocker_summary", [])
    if blockers:
        lines.extend(f"- `{b}`" for b in blockers)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_aal_viz_operator_climate_overlay_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_aal_viz_operator_climate_overlay_markdown(packet), encoding="utf-8")
