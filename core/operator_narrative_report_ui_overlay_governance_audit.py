from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths
from core.generated_artifact_registry import build_generated_artifact_registry

PATCH_ID = "PATCH-P45-OPERATOR-NARRATIVE-REPORT-UI-OVERLAY-GOVERNANCE-AUDIT-001"
SCHEMA_VERSION = "OperatorNarrativeReportUIOverlayGovernanceAudit.v1"
AUDIT_ID = "operator_narrative_report_ui_overlay_governance_audit_001"

_ALLOWED_STATUS = {"PASS", "WARN", "FAIL", "NOT_COMPUTABLE"}
_GOVERNANCE_TRUE = ["advisory_only", "projection_only", "read_only", "report_overlay_only", "render_consumer_only", "non_authoritative", "source_linked"]
_GOVERNANCE_FALSE = ["inference_authority", "prediction_allowed", "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed", "adaptive_behavior_allowed", "psychological_claims_allowed", "speculative_causation_allowed"]
_FORBIDDEN_FIELDS = ["command_channel", "action_authority", "recommendation_authority", "execution_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "authority_granted", "auto_execute", "auto_approve", "bidirectional_control"]
_FORBIDDEN_PHRASES = ["recommend", "should do", "forecast", "prediction", "will happen", "readiness", "take action", "execute", "approve", "route", "mutate", "next move"]

_GOV_FLAGS = {
    "audit_only": True,
    "advisory_only": True,
    "non_authoritative": True,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
    "inference_authority": False,
    "prediction_allowed": False,
    "forecast_authority": False,
    "trend_prediction_allowed": False,
    "readiness_claims_allowed": False,
    "recommendation_authority": False,
    "action_authority": False,
    "adaptive_behavior_allowed": False,
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
    return (payload, "PRESENT") if isinstance(payload, dict) else (None, "CORRUPT")


def _finding(severity: str, category: str, message: str, evidence_refs: list[str]) -> dict[str, Any]:
    refs = sorted(str(r) for r in evidence_refs)
    norm = message.strip().lower()
    fid = hashlib.sha256(f"{category}|{norm}|{'|'.join(refs)}".encode("utf-8")).hexdigest()
    return {"finding_id": fid, "severity": severity, "category": category, "message": message.strip(), "evidence_refs": refs}


def build_operator_narrative_report_ui_overlay_governance_audit(*, overlay_packet: dict[str, Any] | None = None, report_packet: dict[str, Any] | None = None, report_audit_packet: dict[str, Any] | None = None, overlay_path: str | Path | None = None, report_path: str | Path | None = None, report_audit_path: str | Path | None = None) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    overlay_path = Path(overlay_path) if overlay_path else paths.operator_narrative_report_ui_overlay_latest
    report_path = Path(report_path) if report_path else paths.operator_narrative_report_latest
    report_audit_path = Path(report_audit_path) if report_audit_path else paths.operator_narrative_report_governance_audit_latest

    findings: list[dict[str, Any]] = []
    src_presence: dict[str, str] = {}

    if overlay_packet is None:
        overlay, s = _load_json(overlay_path)
        src_presence["p44_overlay_json"] = s
    else:
        overlay, s = deepcopy(overlay_packet), "PRESENT"
        src_presence["p44_overlay_json"] = s
    if report_packet is None:
        report, s2 = _load_json(report_path)
        src_presence["p42_report_json"] = s2
    else:
        report, s2 = deepcopy(report_packet), "PRESENT"
        src_presence["p42_report_json"] = s2
    if report_audit_packet is None:
        report_audit, s3 = _load_json(report_audit_path)
        src_presence["p43_audit_json"] = s3
    else:
        report_audit, s3 = deepcopy(report_audit_packet), "PRESENT"
        src_presence["p43_audit_json"] = s3

    for key, st, p in [("p44_overlay_json", src_presence["p44_overlay_json"], overlay_path), ("p42_report_json", src_presence["p42_report_json"], report_path), ("p43_audit_json", src_presence["p43_audit_json"], report_audit_path)]:
        if st != "PRESENT":
            findings.append(_finding("FAIL", "SOURCE", f"required source {key} is {st.lower()}", [str(p)]))

    overlay = overlay or {}
    report = report or {}
    report_audit = report_audit or {}

    report_ids = [str(x.get("section_id", "")) for x in report.get("report_sections", []) if isinstance(x, dict)]
    nav_ids = [str(x.get("section_id", "")) for x in overlay.get("section_navigation", []) if isinstance(x, dict)]
    if nav_ids != report_ids:
        findings.append(_finding("FAIL", "SECTION_PARITY", "section_navigation must mirror report_sections order exactly", ["p44.section_navigation", "p42.report_sections"]))

    for key, id_key in [("render_layers", "layer_id"), ("overlay_nodes", "node_id"), ("overlay_cards", "card_id"), ("overlay_badges", "badge_id"), ("overlay_edges", "edge_id")]:
        vals = overlay.get(key, [])
        if isinstance(vals, list):
            ids = [str(v.get(id_key, "")) for v in vals if isinstance(v, dict)]
            if ids != sorted(ids):
                findings.append(_finding("FAIL", "ORDERING", f"{key} must be sorted by {id_key}", [f"p44.{key}"]))

    for ref in overlay.get("passive_references", []) if isinstance(overlay.get("passive_references", []), list) else []:
        if not isinstance(ref, dict):
            continue
        if str(ref.get("reference_type", "")) != "passive_path":
            findings.append(_finding("FAIL", "PASSIVE_REFERENCE", "passive_references must use passive_path", ["p44.passive_references.reference_type"]))
        if str(ref.get("command_url", "")).strip() != "":
            findings.append(_finding("FAIL", "PASSIVE_REFERENCE", "command_url must be blank", ["p44.passive_references.command_url"]))

    for k in _FORBIDDEN_FIELDS:
        if bool(overlay.get("governance_flags", {}).get(k, False)):
            findings.append(_finding("FAIL", "GOVERNANCE", f"forbidden field must be absent/false: {k}", [f"p44.governance_flags.{k}"]))

    text_scan = json.dumps(overlay, sort_keys=True).lower()
    for phrase in _FORBIDDEN_PHRASES:
        if phrase in text_scan:
            findings.append(_finding("FAIL", "LANGUAGE", f"forbidden phrase present: {phrase}", ["p44_overlay_json"]))

    if "overlay_hash" in overlay:
        c = deepcopy(overlay)
        claimed = str(c.pop("overlay_hash", ""))
        if claimed != canonical_hash(c):
            findings.append(_finding("FAIL", "HASH_INTEGRITY", "overlay_hash mismatch", ["p44.overlay_hash"]))
    else:
        findings.append(_finding("WARN", "HASH_INTEGRITY", "overlay_hash missing; recomputation unavailable", ["p44.overlay_hash"]))

    if overlay.get("source_hash_lineage", {}).get("report_hash_ref") != report.get("report_hash"):
        findings.append(_finding("FAIL", "LINEAGE", "overlay report hash lineage mismatch", ["p44.source_hash_lineage.report_hash_ref", "p42.report_hash"]))

    g = overlay.get("governance_flags", {}) if isinstance(overlay.get("governance_flags", {}), dict) else {}
    for k in _GOVERNANCE_TRUE:
        if not bool(g.get(k, False)):
            findings.append(_finding("FAIL", "GOVERNANCE", f"governance flag {k} must be true", [f"p44.governance_flags.{k}"]))
    for k in _GOVERNANCE_FALSE:
        if bool(g.get(k, False)):
            findings.append(_finding("FAIL", "GOVERNANCE", f"governance flag {k} must be false", [f"p44.governance_flags.{k}"]))

    reg = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in reg.entries}
    for p in ["out/projections/operator_narrative_report_ui_overlay_001.latest.json", "out/projections/operator_narrative_report_ui_overlay_001.latest.md", "out/audit/operator_narrative_report_ui_overlay_governance_audit_001.latest.json", "out/audit/operator_narrative_report_ui_overlay_governance_audit_001.latest.md"]:
        e = emap.get(p)
        if e is None:
            findings.append(_finding("FAIL", "REGISTRY", f"missing generated artifact registry entry: {p}", [p]))
        elif e.determinism_class != "DERIVED_OPTIONAL":
            findings.append(_finding("FAIL", "REGISTRY", f"unexpected determinism class for {p}: {e.determinism_class}", [p]))

    findings = sorted(findings, key=lambda f: (f["severity"], f["category"], f["finding_id"]))
    counts = {"FAIL": sum(1 for f in findings if f["severity"] == "FAIL"), "WARN": sum(1 for f in findings if f["severity"] == "WARN")}
    nc = any(v != "PRESENT" for v in src_presence.values())
    if nc:
        final_status = "NOT_COMPUTABLE"
    elif counts["FAIL"]:
        final_status = "FAIL"
    elif counts["WARN"]:
        final_status = "WARN"
    else:
        final_status = "PASS"
    posture = {"PASS": "CLEAN", "WARN": "WARNING", "FAIL": "FAILED", "NOT_COMPUTABLE": "NOT_COMPUTABLE"}[final_status]

    out = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "audit_id": AUDIT_ID,
        "final_status": final_status,
        "audit_posture": posture,
        "findings": findings,
        "finding_counts": {"by_severity": {"FAIL": counts["FAIL"], "WARN": counts["WARN"], "INFO": 0}, "total": len(findings)},
        "overlay_integrity_summary": {"overlay_hash_present": "overlay_hash" in overlay},
        "overlay_governance_summary": {"affirmed_true_flags": _GOVERNANCE_TRUE, "affirmed_false_flags": _GOVERNANCE_FALSE},
        "section_parity_summary": {"overlay_section_ids": nav_ids, "report_section_ids": report_ids},
        "lineage_summary": {"report_hash_ref": overlay.get("source_hash_lineage", {}).get("report_hash_ref", ""), "report_hash": report.get("report_hash", "")},
        "registry_summary": {"overlay_class_expected": "DERIVED_OPTIONAL", "audit_class_expected": "DERIVED_OPTIONAL"},
        "source_artifacts": {"p42_report_json": str(report_path), "p43_audit_json": str(report_audit_path), "p44_overlay_json": str(overlay_path)},
        "source_hashes": {"p42_report_json": canonical_hash(report) if report else "NOT_COMPUTABLE", "p43_audit_json": canonical_hash(report_audit) if report_audit else "NOT_COMPUTABLE", "p44_overlay_json": canonical_hash(overlay) if overlay else "NOT_COMPUTABLE"},
        "source_hash_lineage": {"p42_report_hash": report.get("report_hash", "NOT_COMPUTABLE"), "p43_audit_hash": report_audit.get("audit_hash", "NOT_COMPUTABLE"), "p44_overlay_hash": overlay.get("overlay_hash", "NOT_COMPUTABLE")},
        "blocker_summary": sorted(set(str(f["message"]) for f in findings if f["severity"] == "FAIL")),
        "governance_flags": deepcopy(_GOV_FLAGS),
        "provenance": {"source_packet_presence": src_presence, "deterministic": True, "audit_only": True, "fail_closed": True},
    }
    out["audit_hash"] = canonical_hash(out)
    return out


def build_operator_narrative_report_ui_overlay_governance_audit_markdown(packet: dict[str, Any]) -> str:
    lines = ["# P45 Operator Narrative Report UI Overlay Governance Audit", "", f"- audit_id: `{packet.get('audit_id','')}`", f"- final_status: `{packet.get('final_status','')}`", f"- audit_posture: `{packet.get('audit_posture','')}`", "", "## Findings"]
    for f in packet.get("findings", []):
        lines.append(f"- `{f.get('severity','')}` `{f.get('category','')}` {f.get('message','')}")
    lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_report_ui_overlay_governance_audit(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_report_ui_overlay_governance_audit_markdown(packet), encoding="utf-8")
