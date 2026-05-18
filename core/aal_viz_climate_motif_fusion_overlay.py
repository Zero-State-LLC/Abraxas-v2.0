from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P40-AAL-VIZ-CLIMATE-MOTIF-FUSION-OVERLAY-001"
SCHEMA_VERSION = "AALVizClimateMotifFusionOverlay.v1"
OVERLAY_ID = "aal_viz_climate_motif_fusion_overlay_001"

NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "fusion_overlay_only": True,
    "render_consumer_only": True,
    "non_authoritative": True,
    "inference_authority": False,
    "prediction_allowed": False,
    "forecast_authority": False,
    "trend_prediction_allowed": False,
    "readiness_claims_allowed": False,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
    "routing_change_allowed": False,
    "queue_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "ui_command_authority": False,
    "adaptive_behavior_allowed": False,
    "psychological_claims_allowed": False,
    "speculative_causation_allowed": False,
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
        "aal_viz_operator_climate_overlay": paths.aal_viz_operator_climate_overlay_latest.as_posix(),
        "aal_viz_pressure_motif_overlay": paths.aal_viz_pressure_motif_overlay_latest.as_posix(),
        "operator_load_seasonality": paths.operator_load_seasonality_latest.as_posix(),
    }


def _prefixed_items(items: list[dict[str, Any]], *, id_key: str, prefix: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        copied = deepcopy(item)
        raw_id = str(copied.get(id_key, "")).strip()
        if not raw_id:
            continue
        copied[id_key] = f"{prefix}{raw_id}"
        for fk in ("layer_id", "node_id", "source_node_id", "target_node_id"):
            if fk in copied and isinstance(copied[fk], str):
                copied[fk] = f"{prefix}{copied[fk]}"
        out.append(copied)
    return out


def _mk_fusion_edge(edge_id: str, source: str, target: str, relation: str) -> dict[str, str]:
    return {
        "edge_id": edge_id,
        "source_node_id": source,
        "target_node_id": target,
        "relation": relation,
    }


def _stable_unique_sorted(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    uniq: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        k = str(item.get(key, "")).strip()
        if not k:
            continue
        uniq[k] = item
    return sorted(uniq.values(), key=lambda x: str(x.get(key, "")))


def build_aal_viz_climate_motif_fusion_overlay_packet(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
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

    climate = loaded.get("aal_viz_operator_climate_overlay") or {}
    motif = loaded.get("aal_viz_pressure_motif_overlay") or {}
    seasonality = loaded.get("operator_load_seasonality") or {}

    blockers.extend(str(b).strip() for b in climate.get("blocker_summary", []) if str(b).strip())
    blockers.extend(str(b).strip() for b in motif.get("blocker_summary", []) if str(b).strip())
    blockers.extend(str(b).strip() for b in seasonality.get("blocker_summary", []) if str(b).strip())
    blocker_summary = sorted(set(blockers))

    missing_or_corrupt = any(v != "PRESENT" for v in source_status.values())

    source_finals = {
        "climate": str(climate.get("final_status", NOT_COMPUTABLE)),
        "motif": str(motif.get("final_status", NOT_COMPUTABLE)),
        "seasonality": str(seasonality.get("final_status", NOT_COMPUTABLE)),
    }
    climate_posture = str(climate.get("overlay_posture", NOT_COMPUTABLE))
    motif_posture = str(motif.get("overlay_posture", NOT_COMPUTABLE))
    seasonality_posture = str(seasonality.get("seasonality_posture", NOT_COMPUTABLE))

    if missing_or_corrupt:
        final_status = NOT_COMPUTABLE
        fusion_posture = NOT_COMPUTABLE
    elif BLOCKED in set(source_finals.values()):
        final_status = BLOCKED
        fusion_posture = BLOCKED
    elif any(
        x in {"PROJECTION_DEGRADED", "ADVISORY_DEGRADED"}
        for x in [*source_finals.values(), climate_posture, motif_posture, seasonality_posture]
    ) or seasonality_posture in {"PRESSURE_PERSISTENCE", "RECURRENCE_OBSERVED", "DEGRADED"}:
        final_status = "PROJECTION_DEGRADED"
        if seasonality_posture == "PRESSURE_PERSISTENCE":
            fusion_posture = "PRESSURE_PERSISTENCE"
        elif seasonality_posture == "RECURRENCE_OBSERVED":
            fusion_posture = "RECURRENCE_OBSERVED"
        else:
            fusion_posture = "DEGRADED"
    else:
        final_status = "PROJECTION_ONLY"
        fusion_posture = "WATCH" if "WATCH" in {climate_posture, motif_posture, seasonality_posture} else "CLEAR"

    climate_layers = _prefixed_items(list(climate.get("render_layers", [])), id_key="layer_id", prefix="climate.")
    motif_layers = _prefixed_items(list(motif.get("render_layers", [])), id_key="layer_id", prefix="motif.")
    seasonality_layer = [{"layer_id": "seasonality.recurrence_summary", "status": "PRESENT"}]
    render_layers = _stable_unique_sorted([*climate_layers, *motif_layers, *seasonality_layer], "layer_id")

    climate_nodes = _prefixed_items(list(climate.get("overlay_nodes", [])), id_key="node_id", prefix="climate.")
    motif_nodes = _prefixed_items(list(motif.get("overlay_nodes", [])), id_key="node_id", prefix="motif.")
    seasonality_nodes = [{
        "node_id": "seasonality.node.recurrence",
        "layer_id": "seasonality.recurrence_summary",
        "label": "Seasonality Recurrence",
        "posture": seasonality_posture,
        "source_key": "operator_load_seasonality",
    }]
    overlay_nodes = _stable_unique_sorted([*climate_nodes, *motif_nodes, *seasonality_nodes], "node_id")

    climate_cards = _prefixed_items(list(climate.get("overlay_cards", [])), id_key="card_id", prefix="climate.")
    motif_cards = _prefixed_items(list(motif.get("overlay_cards", [])), id_key="card_id", prefix="motif.")
    seasonality_cards = [{
        "card_id": "seasonality.card.recurrence_summary",
        "title": "Seasonality Summary",
        "value": str((seasonality.get("recurrence_summary") or {}).get("repeated_class_count", 0)),
        "seasonality_posture": seasonality_posture,
        "seasonality_final_status": source_finals["seasonality"],
    }]
    overlay_cards = _stable_unique_sorted([*climate_cards, *motif_cards, *seasonality_cards], "card_id")

    climate_badges = _prefixed_items(list(climate.get("overlay_badges", [])), id_key="badge_id", prefix="climate.")
    motif_badges = _prefixed_items(list(motif.get("overlay_badges", [])), id_key="badge_id", prefix="motif.")
    seasonality_badges = [{"badge_id": "seasonality.badge.posture", "token": f"seasonality.{seasonality_posture.lower()}"}]
    overlay_badges = _stable_unique_sorted([*climate_badges, *motif_badges, *seasonality_badges], "badge_id")

    climate_edges = _prefixed_items(list(climate.get("overlay_edges", [])), id_key="edge_id", prefix="climate.")
    motif_edges = _prefixed_items(list(motif.get("overlay_edges", [])), id_key="edge_id", prefix="motif.")
    fusion_edges = [
        _mk_fusion_edge("fusion.edge.climate_to_seasonality", "climate.node.climatology", "seasonality.node.recurrence", "summarized_by"),
        _mk_fusion_edge("fusion.edge.motif_to_seasonality", "motif.node.motif.motif.degradation_vector.corridor_pressure_persistence", "seasonality.node.recurrence", "recurs_with"),
        _mk_fusion_edge("fusion.edge.climate_to_motif", "climate.node.explainer", "motif.node.motif.motif.degradation_vector.corridor_pressure_persistence", "projects_into"),
    ]
    overlay_edges = _stable_unique_sorted([*climate_edges, *motif_edges, *fusion_edges], "edge_id")

    source_hashes = {k: (str(canonical_hash(v)) if isinstance(v, dict) else NOT_COMPUTABLE) for k, v in sorted(loaded.items())}
    source_hash_lineage = {
        "p35_overlay_hash": str(climate.get("overlay_hash", NOT_COMPUTABLE)),
        "p37_overlay_hash": str(motif.get("overlay_hash", NOT_COMPUTABLE)),
        "p39_seasonality_hash": str(seasonality.get("seasonality_hash", NOT_COMPUTABLE)),
    }
    if isinstance(seasonality.get("source_hash_lineage"), dict):
        source_hash_lineage.update({f"p39.{k}": str(v) for k, v in sorted(seasonality["source_hash_lineage"].items())})

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "overlay_id": OVERLAY_ID,
        "final_status": final_status,
        "fusion_posture": fusion_posture,
        "fusion_summary": {
            "source_final_statuses": source_finals,
            "source_postures": {
                "climate_overlay_posture": climate_posture,
                "motif_overlay_posture": motif_posture,
                "seasonality_posture": seasonality_posture,
            },
            "recurrence_summary": deepcopy(seasonality.get("recurrence_summary", {})),
            "motif_governance_audit_status": str((seasonality.get("audit_status_counts") or {}).get("FAIL", "UNKNOWN")),
        },
        "render_layers": render_layers,
        "overlay_nodes": overlay_nodes,
        "overlay_cards": overlay_cards,
        "overlay_badges": overlay_badges,
        "overlay_edges": overlay_edges,
        "source_artifacts": sources,
        "source_hashes": source_hashes,
        "source_hash_lineage": source_hash_lineage,
        "blocker_summary": blocker_summary,
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": source_status,
            "deterministic": True,
            "projection_only": True,
            "advisory_only": True,
            "render_consumer_only": True,
            "fusion_overlay_only": True,
        },
    }
    packet["fusion_hash"] = canonical_hash(packet)
    return packet


def build_aal_viz_climate_motif_fusion_overlay_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P40 AAL-Viz Climate + Motif Fusion Overlay",
        "",
        f"- overlay_id: `{packet['overlay_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- fusion_posture: `{packet['fusion_posture']}`",
        f"- fusion_hash: `{packet['fusion_hash']}`",
        "",
        "## Layer Count",
        f"- `{len(packet.get('render_layers', []))}`",
        "",
        "## Blockers",
    ]
    blockers = packet.get("blocker_summary", [])
    if blockers:
        lines.extend(f"- `{b}`" for b in blockers)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_aal_viz_climate_motif_fusion_overlay_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_aal_viz_climate_motif_fusion_overlay_markdown(packet), encoding="utf-8")
