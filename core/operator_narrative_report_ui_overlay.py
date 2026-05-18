from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P44-OPERATOR-NARRATIVE-REPORT-UI-OVERLAY-001"
SCHEMA_VERSION = "OperatorNarrativeReportUIOverlay.v1"
OVERLAY_ID = "operator_narrative_report_ui_overlay_001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "read_only": True,
    "report_overlay_only": True,
    "render_consumer_only": True,
    "non_authoritative": True,
    "source_linked": True,
    "ui_command_authority": False,
    "action_authority": False,
    "recommendation_authority": False,
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


def build_operator_narrative_report_ui_overlay_packet(*, report_json_path: str | Path | None = None, report_markdown_path: str | Path | None = None, audit_json_path: str | Path | None = None, report_packet: dict[str, Any] | None = None, audit_packet: dict[str, Any] | None = None) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    report_path = Path(report_json_path) if report_json_path is not None else paths.operator_narrative_report_latest
    report_md_path = Path(report_markdown_path) if report_markdown_path is not None else paths.operator_narrative_report_latest.with_suffix(".md")
    audit_path = Path(audit_json_path) if audit_json_path is not None else paths.operator_narrative_report_governance_audit_latest

    source_status: dict[str, str] = {}
    blockers: list[str] = []

    if report_packet is None:
        report, rs = _load_json(report_path)
        source_status["operator_narrative_report_json"] = rs
    else:
        report = deepcopy(report_packet)
        rs = "PRESENT"
        source_status["operator_narrative_report_json"] = rs
    if audit_packet is None:
        audit, aus = _load_json(audit_path)
        source_status["operator_narrative_report_governance_audit_json"] = aus
    else:
        audit = deepcopy(audit_packet)
        aus = "PRESENT"
        source_status["operator_narrative_report_governance_audit_json"] = aus

    if rs != "PRESENT":
        blockers.append(f"source_{rs.lower()}:operator_narrative_report_json")
    if aus != "PRESENT":
        blockers.append(f"source_{aus.lower()}:operator_narrative_report_governance_audit_json")

    report = report or {}
    audit = audit or {}
    blockers.extend(str(b) for b in (report.get("blocker_summary") or []) if str(b).strip())
    blockers.extend(str(b) for b in (audit.get("blocker_summary") or []) if str(b).strip())
    blocker_summary = sorted(set(blockers))

    report_final = str(report.get("final_status", NOT_COMPUTABLE))
    report_posture = str(report.get("report_posture", NOT_COMPUTABLE))
    audit_final = str(audit.get("final_status", NOT_COMPUTABLE))
    audit_posture = str(audit.get("audit_posture", NOT_COMPUTABLE))

    if rs != "PRESENT" or aus != "PRESENT":
        final_status, overlay_posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif audit_final in {"FAIL", "NOT_COMPUTABLE"} or report_final in {"BLOCKED", "NOT_COMPUTABLE"}:
        final_status, overlay_posture = "BLOCKED", "BLOCKED"
    elif audit_final == "WARN" or report_final == "REPORT_DEGRADED":
        final_status, overlay_posture = "PROJECTION_DEGRADED", ("WATCH" if report_posture == "WATCH" else "DEGRADED")
    else:
        final_status, overlay_posture = "PROJECTION_ONLY", ("WATCH" if report_posture == "WATCH" else "CLEAR")

    sections = list(report.get("report_sections") or [])
    section_navigation = []
    overlay_nodes = []
    overlay_cards = []
    overlay_badges = []
    overlay_edges = []
    prev_section = ""
    for i, sec in enumerate(sections):
        if not isinstance(sec, dict):
            continue
        sid = str(sec.get("section_id", ""))
        title = str(sec.get("title", ""))
        status = str(sec.get("status", ""))
        nav_id = f"nav.section.{sid}"
        node_id = f"node.section.{sid}"
        card_id = f"card.section.{sid}"
        section_navigation.append({"nav_id": nav_id, "section_id": sid, "title": title, "status": status, "index": i})
        overlay_nodes.append({"node_id": node_id, "layer_id": "report_sections", "section_id": sid, "status": status})
        overlay_cards.append({"card_id": card_id, "node_id": node_id, "title": title, "status": status, "source_refs": sorted(str(r) for r in sec.get("source_refs", [])), "observed_fields": deepcopy(sec.get("observed_fields", {}))})
        overlay_badges.append({"badge_id": f"badge.section_status.{sid}", "token": f"section_status.{status.lower()}"})
        if prev_section:
            overlay_edges.append({"edge_id": f"edge.section.{prev_section}.to.{sid}", "source_node_id": f"node.section.{prev_section}", "target_node_id": node_id, "relation": "sequence"})
        prev_section = sid

    overlay_badges.extend([
        {"badge_id": f"badge.report_audit.{audit_final.lower()}", "token": f"audit_status.{audit_final.lower()}"},
        {"badge_id": "badge.governance_boundary.locked", "token": "governance.boundary_locked"},
    ])
    overlay_cards.extend([
        {"card_id": "card.report_blockers", "title": "Blocker Summary", "blocker_count": len(blocker_summary), "blocker_summary": blocker_summary},
        {"card_id": "card.governance_boundary", "title": "Governance Boundary", "governance_summary": deepcopy(report.get("governance_summary", {})), "governance_flags": deepcopy(report.get("governance_flags", {}))},
        {"card_id": "card.report_audit", "title": "P43 Governance Audit", "audit_final_status": audit_final, "audit_posture": audit_posture, "finding_counts": deepcopy(audit.get("finding_counts", {}))},
        {"card_id": "card.source_lineage", "title": "Source Lineage", "report_hash": str(report.get("report_hash", NOT_COMPUTABLE)), "audit_hash": str(audit.get("audit_hash", NOT_COMPUTABLE)), "source_hash_lineage": deepcopy(report.get("source_hash_lineage", {}))},
    ])

    render_layers = sorted([
        {"layer_id": "report_audit", "status": "PRESENT"},
        {"layer_id": "report_blockers", "status": "PRESENT"},
        {"layer_id": "report_governance", "status": "PRESENT"},
        {"layer_id": "report_lineage", "status": "PRESENT"},
        {"layer_id": "report_sections", "status": "PRESENT"},
    ], key=lambda x: x["layer_id"])

    source_artifacts = {
        "operator_narrative_report_json": report_path.as_posix(),
        "operator_narrative_report_markdown": report_md_path.as_posix(),
        "operator_narrative_report_governance_audit_json": audit_path.as_posix(),
    }
    source_hashes = {
        "operator_narrative_report_json": canonical_hash(report) if report else NOT_COMPUTABLE,
        "operator_narrative_report_governance_audit_json": canonical_hash(audit) if audit else NOT_COMPUTABLE,
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "overlay_id": OVERLAY_ID,
        "final_status": final_status,
        "overlay_posture": overlay_posture,
        "report_overlay_summary": {
            "report_final_status": report_final,
            "report_posture": report_posture,
            "audit_final_status": audit_final,
            "audit_posture": audit_posture,
            "section_count": len(section_navigation),
            "blocker_count": len(blocker_summary),
        },
        "section_navigation": section_navigation,
        "render_layers": render_layers,
        "overlay_nodes": sorted(overlay_nodes, key=lambda x: str(x["node_id"])),
        "overlay_cards": sorted(overlay_cards, key=lambda x: str(x["card_id"])),
        "overlay_badges": sorted(overlay_badges, key=lambda x: str(x["badge_id"])),
        "overlay_edges": sorted(overlay_edges, key=lambda x: str(x["edge_id"])),
        "passive_references": [{"reference_id": "ref.report_markdown_path", "reference_type": "passive_path", "path": report_md_path.as_posix(), "command_url": ""}],
        "source_artifacts": source_artifacts,
        "source_hashes": source_hashes,
        "source_hash_lineage": deepcopy(report.get("source_hash_lineage", {})),
        "blocker_summary": blocker_summary,
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {"source_packet_presence": source_status, "deterministic": True, "projection_only": True, "read_only": True, "report_overlay_only": True, "render_consumer_only": True, "source_linked": True, "fail_closed": True},
    }
    packet["overlay_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_report_ui_overlay_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P44 Operator Narrative Report UI Overlay",
        "",
        f"- overlay_id: `{packet.get('overlay_id', '')}`",
        f"- final_status: `{packet.get('final_status', '')}`",
        f"- overlay_posture: `{packet.get('overlay_posture', '')}`",
        f"- report_hash_ref: `{packet.get('source_hash_lineage', {}).get('report_hash_ref', packet.get('overlay_hash', ''))}`",
        "",
        "## Section Navigation",
    ]
    for nav in packet.get("section_navigation", []):
        lines.append(f"- `{nav.get('section_id', '')}` :: `{nav.get('status', '')}`")
    lines.extend(["", "## Passive References"])
    for ref in packet.get("passive_references", []):
        lines.append(f"- `{ref.get('reference_type', '')}`: `{ref.get('path', '')}`")
    lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_report_ui_overlay_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_report_ui_overlay_markdown(packet), encoding="utf-8")
