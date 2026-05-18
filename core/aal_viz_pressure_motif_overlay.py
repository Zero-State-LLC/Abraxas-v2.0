from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P37-AAL-VIZ-PRESSURE-MOTIF-OVERLAY-001"
SCHEMA_VERSION = "AALVizPressureMotifOverlay.v1"
OVERLAY_ID = "aal_viz_pressure_motif_overlay_001"

NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "render_consumer_only": True,
    "motif_overlay_only": True,
    "non_authoritative": True,
    "inference_authority": False,
    "prediction_allowed": False,
    "forecast_authority": False,
    "readiness_claims_allowed": False,
    "motif_learning_authority": False,
    "adaptive_ontology_mutation_allowed": False,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
    "routing_change_allowed": False,
    "queue_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "ui_command_authority": False,
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
        "pressure_motif_registry": paths.pressure_motif_registry_latest.as_posix(),
        "aal_viz_operator_climate_overlay": paths.aal_viz_operator_climate_overlay_latest.as_posix(),
    }


def _stable(values: list[str]) -> list[str]:
    return sorted(set(v for v in values if v))


def _stable_evidence_edge_id(motif_id: str, evidence_ref: str) -> str:
    digest = hashlib.sha256(f"{motif_id}|{evidence_ref}".encode("utf-8")).hexdigest()[:12]
    return f"edge.motif.{motif_id}.evidence.{digest}"


def build_aal_viz_pressure_motif_overlay_packet(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    sources = source_artifact_paths or _src_paths(paths)

    loaded: dict[str, dict[str, Any] | None] = {}
    source_status: dict[str, str] = {}
    blockers: list[str] = []
    for key, path in sorted(sources.items()):
        payload, status = _load_json(path)
        loaded[key] = payload
        source_status[key] = status
        if key == "pressure_motif_registry" and status != "PRESENT":
            blockers.append(f"source_{status.lower()}:{key}")

    if source_packets:
        for key, payload in source_packets.items():
            loaded[key] = deepcopy(payload)
            source_status[key] = "PRESENT"

    registry = loaded.get("pressure_motif_registry") or {}
    climate = loaded.get("aal_viz_operator_climate_overlay") or {}

    blockers.extend(str(b).strip() for b in registry.get("blocker_summary", []) if str(b).strip())
    blockers.extend(str(b).strip() for b in climate.get("blocker_summary", []) if str(b).strip())
    blocker_summary = _stable(blockers)

    reg_status = str(source_status.get("pressure_motif_registry", "MISSING"))
    reg_final_status = str(registry.get("final_status", NOT_COMPUTABLE))
    reg_posture = str(registry.get("registry_posture", NOT_COMPUTABLE))

    motifs = sorted(
        [m for m in registry.get("motif_catalog", []) if isinstance(m, dict)],
        key=lambda item: str(item.get("motif_id", "")),
    )

    if reg_status != "PRESENT":
        final_status = NOT_COMPUTABLE
        overlay_posture = NOT_COMPUTABLE
    elif reg_final_status == BLOCKED:
        final_status = BLOCKED
        overlay_posture = BLOCKED
    elif reg_final_status == "ADVISORY_DEGRADED" or reg_posture in {"PRESSURE_PERSISTENCE", "DEGRADED"}:
        final_status = "PROJECTION_DEGRADED"
        overlay_posture = "PRESSURE_PERSISTENCE" if reg_posture == "PRESSURE_PERSISTENCE" else "DEGRADED"
    elif not motifs:
        final_status = "PROJECTION_ONLY"
        overlay_posture = "WATCH"
    elif reg_posture == "WATCH":
        final_status = "PROJECTION_ONLY"
        overlay_posture = "WATCH"
    else:
        final_status = "PROJECTION_ONLY"
        overlay_posture = "CLEAR"

    render_layers = sorted([
        {"layer_id": "motif_overview", "status": "PRESENT"},
        {"layer_id": "motif_classes", "status": "PRESENT"},
        {"layer_id": "blocker_class_motifs", "status": "PRESENT"},
        {"layer_id": "degradation_vector_motifs", "status": "PRESENT"},
        {"layer_id": "corridor_pressure_motifs", "status": "PRESENT"},
        {"layer_id": "climatology_count_motifs", "status": "PRESENT"},
        {"layer_id": "overlay_lineage_motifs", "status": "PRESENT"},
    ], key=lambda x: str(x["layer_id"]))

    class_to_layer = {
        "BLOCKER_CLASS": "blocker_class_motifs",
        "DEGRADATION_VECTOR": "degradation_vector_motifs",
        "CORRIDOR_PRESSURE": "corridor_pressure_motifs",
        "CLIMATOLOGY_COUNT": "climatology_count_motifs",
        "OVERLAY_LINEAGE": "overlay_lineage_motifs",
    }

    overlay_nodes: list[dict[str, Any]] = []
    overlay_cards: list[dict[str, Any]] = []
    overlay_edges: list[dict[str, Any]] = []

    for motif in motifs:
        motif_id = str(motif.get("motif_id", ""))
        motif_class = str(motif.get("motif_class", ""))
        layer_id = class_to_layer.get(motif_class, "motif_classes")
        node_id = f"node.motif.{motif_id}"
        card_id = f"card.motif.{motif_id}"

        overlay_nodes.append({
            "node_id": node_id,
            "layer_id": layer_id,
            "motif_id": motif_id,
            "motif_class": motif_class,
            "motif_label": str(motif.get("motif_label", "")),
            "observed_count": int(motif.get("observed_count", 0)),
            "source_surfaces": sorted(str(x) for x in motif.get("source_surfaces", [])),
        })
        overlay_cards.append({
            "card_id": card_id,
            "node_id": node_id,
            "title": str(motif.get("motif_label", "")),
            "motif_class": motif_class,
            "observed_count": int(motif.get("observed_count", 0)),
            "evidence_refs": sorted(str(x) for x in motif.get("evidence_refs", [])),
            "motif_hash": str(motif.get("motif_hash", NOT_COMPUTABLE)),
        })

        for evidence_ref in sorted(str(x) for x in motif.get("evidence_refs", [])):
            overlay_edges.append({
                "edge_id": _stable_evidence_edge_id(motif_id, evidence_ref),
                "source_node_id": node_id,
                "target_node_id": f"node.evidence.{canonical_hash({"ref": evidence_ref})[:12]}",
                "relation": "supported_by",
                "evidence_ref": evidence_ref,
            })

    overlay_badges = [
        {"badge_id": f"badge.motif_class.{klass}", "motif_class": klass, "count": int(count)}
        for klass, count in sorted((registry.get("motif_class_counts") or {}).items())
    ]

    motif_overlay_summary = {
        "motif_count": int(registry.get("motif_count", 0)),
        "motif_class_counts": deepcopy(registry.get("motif_class_counts", {})),
        "motif_evidence_refs": sorted(str(x) for x in registry.get("motif_evidence_refs", [])),
        "registry_posture": reg_posture,
    }

    source_hash_lineage = deepcopy(registry.get("source_hash_lineage", {})) if isinstance(registry.get("source_hash_lineage"), dict) else {}
    if isinstance(climate, dict) and climate:
        source_hash_lineage["optional_p35_overlay_hash"] = str(climate.get("overlay_hash", NOT_COMPUTABLE))

    source_hashes = {
        key: (str(canonical_hash(value)) if isinstance(value, dict) else NOT_COMPUTABLE)
        for key, value in sorted(loaded.items())
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "overlay_id": OVERLAY_ID,
        "final_status": final_status,
        "overlay_posture": overlay_posture,
        "motif_overlay_summary": motif_overlay_summary,
        "render_layers": render_layers,
        "overlay_nodes": sorted(overlay_nodes, key=lambda x: str(x["node_id"])),
        "overlay_cards": sorted(overlay_cards, key=lambda x: str(x["card_id"])),
        "overlay_badges": sorted(overlay_badges, key=lambda x: str(x["badge_id"])),
        "overlay_edges": sorted(overlay_edges, key=lambda x: str(x["edge_id"])),
        "source_artifacts": sources,
        "source_hashes": source_hashes,
        "source_hash_lineage": source_hash_lineage,
        "blocker_summary": blocker_summary,
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": source_status,
            "deterministic": True,
            "advisory_only": True,
            "projection_only": True,
            "render_consumer_only": True,
            "motif_overlay_only": True,
            "optional_climate_context_used": bool(climate),
        },
    }
    packet["overlay_hash"] = canonical_hash(packet)
    return packet


def build_aal_viz_pressure_motif_overlay_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P37 AAL-Viz Pressure Motif Overlay",
        "",
        f"- overlay_id: `{packet['overlay_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- overlay_posture: `{packet['overlay_posture']}`",
        f"- motif_count: `{packet.get('motif_overlay_summary', {}).get('motif_count', 0)}`",
        "",
        "## Motif Class Counts",
    ]
    counts = packet.get("motif_overlay_summary", {}).get("motif_class_counts", {})
    if counts:
        lines.extend(f"- `{k}`: `{v}`" for k, v in sorted(counts.items()))
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_aal_viz_pressure_motif_overlay_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_aal_viz_pressure_motif_overlay_markdown(packet), encoding="utf-8")
