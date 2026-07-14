from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

from core.status_result import (
    STATUS_BLOCKED as BLOCKED,
    STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE,
)

PATCH_ID = "PATCH-P42-OPERATOR-NARRATIVE-REPORT-001"
SCHEMA_VERSION = "OperatorNarrativeReport.v1"
REPORT_ID = "operator_narrative_report_001"


_SECTION_ORDER: tuple[tuple[str, str], ...] = (
    ("executive_signal_state", "Executive Signal State"),
    ("weather_routing", "Weather + Routing"),
    ("memory_corridor", "Memory + Corridor"),
    ("degradation_climatology", "Degradation + Climatology"),
    ("motifs_motif_governance", "Motifs + Motif Governance"),
    ("seasonality", "Seasonality"),
    ("fusion_overlay_fusion_governance", "Fusion Overlay + Fusion Governance"),
    ("blockers", "Blockers"),
    ("governance_boundary", "Governance Boundary"),
    ("source_lineage", "Source Lineage"),
)

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "report_only": True,
    "advisory_only": True,
    "non_authoritative": True,
    "source_linked": True,
    "deterministic_template_only": True,
    "inference_authority": False,
    "prediction_allowed": False,
    "forecast_authority": False,
    "trend_prediction_allowed": False,
    "readiness_claims_allowed": False,
    "recommendation_authority": False,
    "action_authority": False,
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
        "operator_attention_weather": paths.operator_attention_weather_latest.as_posix(),
        "operator_review_routing_enhancer": paths.operator_review_routing_enhancer_latest.as_posix(),
        "operator_attention_ledger": paths.operator_attention_ledger_latest.as_posix(),
        "operator_fatigue_corridor": paths.operator_fatigue_corridor_latest.as_posix(),
        "continuity_degradation_explainer": paths.continuity_degradation_explainer_latest.as_posix(),
        "operator_climatology_summary": paths.operator_climatology_summary_latest.as_posix(),
        "pressure_motif_registry": paths.pressure_motif_registry_latest.as_posix(),
        "motif_governance_audit": paths.motif_governance_audit_latest.as_posix(),
        "operator_load_seasonality": paths.operator_load_seasonality_latest.as_posix(),
        "aal_viz_climate_motif_fusion_overlay": paths.aal_viz_climate_motif_fusion_overlay_latest.as_posix(),
        "fusion_governance_audit": paths.fusion_governance_audit_latest.as_posix(),
    }


def _stable(values: list[Any]) -> list[str]:
    return sorted(set(str(v).strip() for v in values if str(v).strip()))


def _section(section_id: str, title: str, status: str, observed_fields: dict[str, Any], source_refs: list[str]) -> dict[str, Any]:
    return {
        "section_id": section_id,
        "title": title,
        "status": status,
        "observed_fields": {k: observed_fields[k] for k in sorted(observed_fields)},
        "source_refs": sorted(source_refs),
    }


def build_operator_narrative_report_packet(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
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

    p29 = loaded.get("operator_attention_weather") or {}
    p30 = loaded.get("operator_review_routing_enhancer") or {}
    p31 = loaded.get("operator_attention_ledger") or {}
    p32 = loaded.get("operator_fatigue_corridor") or {}
    p33 = loaded.get("continuity_degradation_explainer") or {}
    p34 = loaded.get("operator_climatology_summary") or {}
    p36 = loaded.get("pressure_motif_registry") or {}
    p38 = loaded.get("motif_governance_audit") or {}
    p39 = loaded.get("operator_load_seasonality") or {}
    p40 = loaded.get("aal_viz_climate_motif_fusion_overlay") or {}
    p41 = loaded.get("fusion_governance_audit") or {}

    for packet in (p29, p30, p31, p32, p33, p34, p36, p38, p39, p40, p41):
        blockers.extend(str(b) for b in (packet.get("blocker_summary") or []) if str(b).strip())
    blocker_summary = _stable(blockers)

    missing_or_corrupt = any(v != "PRESENT" for v in source_status.values())
    blocked = str(p41.get("final_status", NOT_COMPUTABLE)) == "FAIL" or any(str((pkt or {}).get("final_status", "")) in {"BLOCKED", "FAIL"} for pkt in (p32, p38, p39, p41))
    degraded = str(p41.get("final_status", NOT_COMPUTABLE)) == "WARN" or any(str((pkt or {}).get("final_status", "")) in {"ADVISORY_DEGRADED", "WARN"} for pkt in (p31, p32, p33, p34, p36, p38, p39))

    if missing_or_corrupt:
        final_status = NOT_COMPUTABLE
        report_posture = NOT_COMPUTABLE
    elif blocked:
        final_status = BLOCKED
        report_posture = BLOCKED
    elif degraded:
        final_status = "REPORT_DEGRADED"
        report_posture = "DEGRADED"
    elif any(str((pkt or {}).get("final_status", "")) == "ADVISORY_ONLY" and "WATCH" in str((pkt or {}).get("weather_posture", "")) + str((pkt or {}).get("routing_posture", "")) + str((pkt or {}).get("ledger_posture", "")) + str((pkt or {}).get("seasonality_posture", "")) for pkt in (p29, p30, p31, p39)):
        final_status = "REPORT_ONLY"
        report_posture = "WATCH"
    else:
        final_status = "REPORT_ONLY"
        report_posture = "CLEAR"

    source_hashes = {k: (canonical_hash(v) if isinstance(v, dict) else NOT_COMPUTABLE) for k, v in sorted(loaded.items())}
    source_hash_lineage = {
        "weather_hash": str(p29.get("weather_hash", NOT_COMPUTABLE)),
        "enhancer_hash": str(p30.get("enhancer_hash", NOT_COMPUTABLE)),
        "ledger_hash": str(p31.get("ledger_hash", NOT_COMPUTABLE)),
        "corridor_hash": str(p32.get("corridor_hash", NOT_COMPUTABLE)),
        "explainer_hash": str(p33.get("explainer_hash", NOT_COMPUTABLE)),
        "summary_hash": str(p34.get("summary_hash", NOT_COMPUTABLE)),
        "registry_hash": str(p36.get("registry_hash", NOT_COMPUTABLE)),
        "motif_audit_hash": str(p38.get("audit_hash", NOT_COMPUTABLE)),
        "seasonality_hash": str(p39.get("seasonality_hash", NOT_COMPUTABLE)),
        "fusion_hash": str(p40.get("fusion_hash", NOT_COMPUTABLE)),
        "fusion_audit_hash": str(p41.get("audit_hash", NOT_COMPUTABLE)),
    }

    sections = [
        _section("executive_signal_state", "Executive Signal State", final_status, {"final_status": final_status, "report_posture": report_posture, "p41_final_status": str(p41.get("final_status", NOT_COMPUTABLE))}, ["fusion_governance_audit"]),
        _section("weather_routing", "Weather + Routing", "OBSERVED", {"weather_posture": str(p29.get("weather_posture", NOT_COMPUTABLE)), "attention_urgency": str(p29.get("attention_urgency", NOT_COMPUTABLE)), "routing_posture": str(p30.get("routing_posture", NOT_COMPUTABLE)), "review_priority_posture": str(p30.get("review_priority_posture", NOT_COMPUTABLE))}, ["operator_attention_weather", "operator_review_routing_enhancer"]),
        _section("memory_corridor", "Memory + Corridor", "OBSERVED", {"ledger_posture": str(p31.get("ledger_posture", NOT_COMPUTABLE)), "ledger_final_status": str(p31.get("final_status", NOT_COMPUTABLE)), "corridor_status": str(p32.get("corridor_status", NOT_COMPUTABLE)), "corridor_final_status": str(p32.get("final_status", NOT_COMPUTABLE))}, ["operator_attention_ledger", "operator_fatigue_corridor"]),
        _section("degradation_climatology", "Degradation + Climatology", "OBSERVED", {"explanation_posture": str(p33.get("explanation_posture", NOT_COMPUTABLE)), "dominant_degradation_vectors": list(p33.get("dominant_degradation_vectors") or []), "climatology_posture": str(p34.get("climatology_posture", NOT_COMPUTABLE)), "observed_distribution_summary": p34.get("observed_distribution_summary", {})}, ["continuity_degradation_explainer", "operator_climatology_summary"]),
        _section("motifs_motif_governance", "Motifs + Motif Governance", "OBSERVED", {"registry_posture": str(p36.get("registry_posture", NOT_COMPUTABLE)), "motif_count": int(p36.get("motif_count", 0)), "motif_governance_final_status": str(p38.get("final_status", NOT_COMPUTABLE)), "motif_governance_posture": str(p38.get("audit_posture", NOT_COMPUTABLE))}, ["pressure_motif_registry", "motif_governance_audit"]),
        _section("seasonality", "Seasonality", "OBSERVED", {"seasonality_posture": str(p39.get("seasonality_posture", NOT_COMPUTABLE)), "seasonality_final_status": str(p39.get("final_status", NOT_COMPUTABLE)), "recurrence_summary": p39.get("recurrence_summary", {})}, ["operator_load_seasonality"]),
        _section("fusion_overlay_fusion_governance", "Fusion Overlay + Fusion Governance", "OBSERVED", {"fusion_final_status": str(p40.get("final_status", NOT_COMPUTABLE)), "fusion_posture": str(p40.get("fusion_posture", NOT_COMPUTABLE)), "fusion_audit_final_status": str(p41.get("final_status", NOT_COMPUTABLE)), "fusion_audit_posture": str(p41.get("audit_posture", NOT_COMPUTABLE))}, ["aal_viz_climate_motif_fusion_overlay", "fusion_governance_audit"]),
        _section("blockers", "Blockers", "OBSERVED", {"blocker_count": len(blocker_summary), "blocker_summary": blocker_summary}, sorted(sources.keys())),
        _section("governance_boundary", "Governance Boundary", "BOUNDARY_LOCKED", {"governance_summary": {"report_only": True, "advisory_only": True, "non_authoritative": True, "mutation_allowed": False, "forecast_authority": False, "readiness_claims_allowed": False}}, sorted(sources.keys())),
        _section("source_lineage", "Source Lineage", "OBSERVED", {"source_hash_lineage": source_hash_lineage, "source_hashes": source_hashes}, sorted(sources.keys())),
    ]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "report_id": REPORT_ID,
        "final_status": final_status,
        "report_posture": report_posture,
        "report_sections": sections,
        "source_artifacts": sources,
        "source_hashes": source_hashes,
        "source_hash_lineage": source_hash_lineage,
        "blocker_summary": blocker_summary,
        "governance_summary": {
            "report_only": True,
            "advisory_only": True,
            "non_authoritative": True,
            "source_linked": True,
            "deterministic_template_only": True,
        },
        "provenance": {
            "source_packet_presence": source_status,
            "deterministic": True,
            "advisory_only": True,
            "report_only": True,
            "source_linked": True,
            "fail_closed": True,
            "section_order": [s[0] for s in _SECTION_ORDER],
        },
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
    }
    packet["report_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_report_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P42 Operator Narrative Report",
        "",
        f"- report_id: `{packet['report_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- report_posture: `{packet['report_posture']}`",
        "",
    ]
    for section in packet.get("report_sections", []):
        lines.append(f"## {section.get('title', '')}")
        lines.append(f"- section_id: `{section.get('section_id', '')}`")
        lines.append(f"- status: `{section.get('status', '')}`")
        lines.append("- source_refs: " + ", ".join(f"`{r}`" for r in section.get("source_refs", [])))
        for key, value in (section.get("observed_fields") or {}).items():
            lines.append(f"- {key}: `{value}`")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_report_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_report_markdown(packet), encoding="utf-8")
