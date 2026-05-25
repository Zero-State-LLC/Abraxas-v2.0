from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths
from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths

PATCH_ID = "PATCH-P43-OPERATOR-NARRATIVE-REPORT-GOVERNANCE-AUDIT-001"
SCHEMA_VERSION = "OperatorNarrativeReportGovernanceAudit.v1"
AUDIT_ID = "operator_narrative_report_governance_audit_001"

_ALLOWED_STATUSES = {"PASS", "WARN", "FAIL", "NOT_COMPUTABLE"}
_ALLOWED_POSTURES = {"CLEAN", "WARNING", "FAILED", "NOT_COMPUTABLE"}

_EXPECTED_SECTION_ORDER = [
    "executive_signal_state",
    "weather_routing",
    "memory_corridor",
    "degradation_climatology",
    "motifs_motif_governance",
    "seasonality",
    "fusion_overlay_fusion_governance",
    "blockers",
    "governance_boundary",
    "source_lineage",
]
_REQUIRED_SOURCE_KEYS = [
    "operator_attention_weather",
    "operator_review_routing_enhancer",
    "operator_attention_ledger",
    "operator_fatigue_corridor",
    "continuity_degradation_explainer",
    "operator_climatology_summary",
    "pressure_motif_registry",
    "motif_governance_audit",
    "operator_load_seasonality",
    "aal_viz_climate_motif_fusion_overlay",
    "fusion_governance_audit",
]

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "audit_only": True,
    "advisory_only": True,
    "non_authoritative": True,
    "report_governance_audit_only": True,
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

_REPORT_AFFIRM = ["report_only", "advisory_only", "non_authoritative", "source_linked", "deterministic_template_only"]
_REPORT_DENY = [
    "inference_authority",
    "prediction_allowed",
    "forecast_authority",
    "trend_prediction_allowed",
    "readiness_claims_allowed",
    "recommendation_authority",
    "action_authority",
    "mutation_allowed",
    "authority_granted",
    "execution_authority",
    "routing_change_allowed",
    "queue_mutation_allowed",
    "canon_mutation_allowed",
    "runtime_mutation_allowed",
    "ui_command_authority",
    "adaptive_behavior_allowed",
    "psychological_claims_allowed",
    "speculative_causation_allowed",
    "auto_execute",
    "auto_approve",
    "command_channel",
    "bidirectional_control",
]

_FORBIDDEN_FIELD_TOKENS = {
    "recommendation",
    "recommendations",
    "action",
    "actions",
    "execute",
    "approval",
    "approve",
    "readiness",
    "forecast",
    "prediction",
    "route_change",
    "mutation",
    "command",
}
_FORBIDDEN_MD_PHRASES = [
    "recommend",
    "recommendation",
    "should do",
    "forecast",
    "will happen",
    "readiness",
    "take action",
    "execute",
    "approve",
    "route",
    "mutate",
    "prediction",
    "predicted",
    "next move",
]


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


def _load_text(path: str | Path) -> tuple[str | None, str]:
    try:
        return Path(path).read_text(encoding="utf-8"), "PRESENT"
    except FileNotFoundError:
        return None, "MISSING"
    except OSError:
        return None, "CORRUPT"


def _paths(paths: RuntimePaths) -> tuple[Path, Path]:
    return paths.operator_narrative_report_latest, paths.operator_narrative_report_latest.with_suffix(".md")


def _finding(severity: str, category: str, message: str, evidence_refs: list[str]) -> dict[str, Any]:
    refs = sorted(str(r) for r in evidence_refs)
    nid = hashlib.sha256(f"{category}|{message.strip().lower()}|{'|'.join(refs)}".encode("utf-8")).hexdigest()
    return {
        "finding_id": f"finding.{category.lower()}.{nid[:16]}",
        "severity": severity,
        "category": category,
        "message": message.strip(),
        "evidence_refs": refs,
    }


def _extract_md_section_ids(markdown: str) -> list[str]:
    return re.findall(r"^- section_id: `([^`]+)`", markdown, flags=re.MULTILINE)


def _scan_keys(value: Any, out: set[str]) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            out.add(str(k).lower())
            _scan_keys(v, out)
    elif isinstance(value, list):
        for v in value:
            _scan_keys(v, out)


def build_operator_narrative_report_governance_audit(*, report_json_path: str | Path | None = None, report_markdown_path: str | Path | None = None, report_packet: dict[str, Any] | None = None, report_markdown: str | None = None) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    default_json, default_md = _paths(paths)
    jp = Path(report_json_path) if report_json_path is not None else default_json
    mp = Path(report_markdown_path) if report_markdown_path is not None else default_md

    findings: list[dict[str, Any]] = []
    source_presence: dict[str, str] = {}

    if report_packet is None:
        packet, status = _load_json(jp)
        source_presence["operator_narrative_report_json"] = status
        if status != "PRESENT":
            findings.append(_finding("FAIL", "SOURCE", f"required source operator_narrative_report_json is {status.lower()}", [jp.as_posix()]))
    else:
        packet = deepcopy(report_packet)
        source_presence["operator_narrative_report_json"] = "PRESENT"

    if report_markdown is None:
        md_text, md_status = _load_text(mp)
        source_presence["operator_narrative_report_markdown"] = md_status
        if md_status != "PRESENT":
            findings.append(_finding("FAIL", "SOURCE", f"required source operator_narrative_report_markdown is {md_status.lower()}", [mp.as_posix()]))
    else:
        md_text = str(report_markdown)
        source_presence["operator_narrative_report_markdown"] = "PRESENT"

    packet = packet or {}
    md_text = md_text or ""

    sections = packet.get("report_sections") if isinstance(packet, dict) else None
    if not isinstance(sections, list):
        findings.append(_finding("FAIL", "SECTION_INTEGRITY", "report_sections missing or not list", ["report_sections"]))
        section_ids = []
    else:
        section_ids = [str(s.get("section_id", "")) for s in sections if isinstance(s, dict)]
        if section_ids != _EXPECTED_SECTION_ORDER:
            findings.append(_finding("FAIL", "SECTION_INTEGRITY", "report_sections order mismatch", ["report_sections.section_id"]))
        if len(section_ids) != len(set(section_ids)):
            findings.append(_finding("FAIL", "SECTION_INTEGRITY", "report section_id values must be unique", ["report_sections.section_id"]))
        for idx, sec in enumerate(sections):
            if not isinstance(sec, dict):
                findings.append(_finding("FAIL", "SECTION_INTEGRITY", f"report section at index {idx} is not object", [f"report_sections[{idx}]"]))
                continue
            for rk in ("section_id", "title", "status", "source_refs", "observed_fields"):
                if rk not in sec:
                    findings.append(_finding("FAIL", "SECTION_INTEGRITY", f"report section missing required field {rk}", [f"report_sections[{idx}]::{rk}"]))

    md_section_ids = _extract_md_section_ids(md_text)
    if md_section_ids != section_ids:
        findings.append(_finding("FAIL", "MARKDOWN_PARITY", "markdown section order does not mirror json report_sections", ["markdown.section_id", "report_sections.section_id"]))
    if not md_text.endswith("\n"):
        findings.append(_finding("FAIL", "MARKDOWN_PARITY", "markdown must end with newline", [mp.as_posix()]))

    if isinstance(packet, dict) and "report_hash" in packet:
        clone = deepcopy(packet)
        claimed = str(clone.pop("report_hash", ""))
        recomputed = canonical_hash(clone)
        if claimed != recomputed:
            findings.append(_finding("FAIL", "HASH_INTEGRITY", "report_hash mismatch", ["report_hash"]))
    else:
        findings.append(_finding("WARN", "HASH_INTEGRITY", "report_hash missing; recomputation unavailable", ["report_hash"]))

    source_lineage = packet.get("source_hash_lineage", {}) if isinstance(packet, dict) else {}
    if not isinstance(source_lineage, dict) or not source_lineage:
        findings.append(_finding("FAIL", "SOURCE_LINEAGE", "source_hash_lineage missing or empty", ["source_hash_lineage"]))

    source_artifacts = packet.get("source_artifacts", {}) if isinstance(packet, dict) else {}
    if not isinstance(source_artifacts, dict):
        findings.append(_finding("FAIL", "SOURCE_LINEAGE", "source_artifacts missing or not object", ["source_artifacts"]))
        source_artifacts = {}
    for key in _REQUIRED_SOURCE_KEYS:
        if key not in source_artifacts:
            findings.append(_finding("FAIL", "SOURCE_LINEAGE", f"missing required source artifact {key}", ["source_artifacts", key]))

    g = packet.get("governance_flags", {}) if isinstance(packet, dict) else {}
    if not isinstance(g, dict):
        findings.append(_finding("FAIL", "GOVERNANCE", "governance_flags missing or not object", ["governance_flags"]))
        g = {}
    for key in _REPORT_AFFIRM:
        if not bool(g.get(key, False)):
            findings.append(_finding("FAIL", "GOVERNANCE", f"governance flag {key} must be true", [f"governance_flags.{key}"]))
    for key in _REPORT_DENY:
        if bool(g.get(key, False)):
            findings.append(_finding("FAIL", "GOVERNANCE", f"governance flag {key} must be false", [f"governance_flags.{key}"]))

    all_keys: set[str] = set()
    _scan_keys(packet, all_keys)
    for token in sorted(_FORBIDDEN_FIELD_TOKENS):
        if token in all_keys:
            findings.append(_finding("FAIL", "LANGUAGE_BOUNDARY", f"forbidden field token present: {token}", ["report_json.keys"]))

    for line_no, line in enumerate(md_text.splitlines(), start=1):
        lower_line = line.lower()
        if "governance_summary" in lower_line:
            continue
        for phrase in _FORBIDDEN_MD_PHRASES:
            if phrase in lower_line:
                findings.append(
                    _finding(
                        "FAIL",
                        "LANGUAGE_BOUNDARY",
                        f"forbidden markdown phrase present: {phrase}",
                        [f"{mp.as_posix()}:{line_no}"],
                    )
                )

    reg = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    entry_map = {e.artifact_path: e for e in reg.entries}
    required_paths = [
        "out/reports/operator_narrative_report_001.latest.json",
        "out/reports/operator_narrative_report_001.latest.md",
        "out/audit/operator_narrative_report_governance_audit_001.latest.json",
        "out/audit/operator_narrative_report_governance_audit_001.latest.md",
    ]
    ci_targets = set(list_ci_drift_artifact_paths(reg))
    for rp in required_paths:
        entry = entry_map.get(rp)
        if entry is None:
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"missing generated artifact registry entry: {rp}", [rp]))
            continue
        if entry.determinism_class != "DERIVED_OPTIONAL":
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"unexpected determinism class for {rp}: {entry.determinism_class}", [rp]))
        if rp in {
            "out/reports/operator_narrative_report_001.latest.json",
            "out/reports/operator_narrative_report_001.latest.md",
        } and rp in ci_targets:
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"p42 report artifact should not be ci-drift-enforced: {rp}", [rp]))

    nc = any(v != "PRESENT" for v in source_presence.values())
    fail_count = sum(1 for f in findings if f["severity"] == "FAIL")
    warn_count = sum(1 for f in findings if f["severity"] == "WARN")
    if nc:
        final_status, posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif fail_count:
        final_status, posture = "FAIL", "FAILED"
    elif warn_count:
        final_status, posture = "WARN", "WARNING"
    else:
        final_status, posture = "PASS", "CLEAN"
        findings.append(_finding("PASS", "SOURCE", "all required operator narrative report audit sources were readable", [jp.as_posix(), mp.as_posix()]))

    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    findings = sorted(findings, key=lambda x: (order.get(str(x["severity"]), 9), str(x["category"]), str(x["finding_id"])))

    out: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "audit_id": AUDIT_ID,
        "final_status": final_status,
        "audit_posture": posture,
        "checked_artifacts": {
            "operator_narrative_report_json": jp.as_posix(),
            "operator_narrative_report_markdown": mp.as_posix(),
        },
        "findings": findings,
        "finding_counts": {
            "PASS": sum(1 for f in findings if f["severity"] == "PASS"),
            "WARN": sum(1 for f in findings if f["severity"] == "WARN"),
            "FAIL": sum(1 for f in findings if f["severity"] == "FAIL"),
        },
        "section_integrity_summary": {"expected_section_order": _EXPECTED_SECTION_ORDER},
        "markdown_integrity_summary": {"markdown_section_ids": md_section_ids, "matches_json_order": md_section_ids == section_ids},
        "source_lineage_summary": {"required_source_keys": _REQUIRED_SOURCE_KEYS, "source_hash_lineage_present": isinstance(source_lineage, dict) and bool(source_lineage)},
        "language_boundary_summary": {"forbidden_field_tokens": sorted(_FORBIDDEN_FIELD_TOKENS), "forbidden_markdown_phrases": _FORBIDDEN_MD_PHRASES},
        "governance_integrity_summary": {"required_affirm_flags": sorted(_REPORT_AFFIRM), "required_deny_flags": sorted(_REPORT_DENY)},
        "registry_classification_summary": {"expected_non_ci_drift_enforced": ["out/reports/operator_narrative_report_001.latest.json", "out/reports/operator_narrative_report_001.latest.md"], "checked_registry_paths": required_paths},
        "source_hashes": {
            "operator_narrative_report_json": canonical_hash(packet) if isinstance(packet, dict) and packet else "NOT_COMPUTABLE",
            "operator_narrative_report_markdown": hashlib.sha256(md_text.encode("utf-8")).hexdigest() if md_text else "NOT_COMPUTABLE",
        },
        "blocker_summary": sorted(f["message"] for f in findings if f["severity"] == "FAIL"),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": source_presence,
            "deterministic": True,
            "audit_only": True,
            "advisory_only": True,
            "non_authoritative": True,
            "fail_closed": True,
        },
    }
    if out["final_status"] not in _ALLOWED_STATUSES or out["audit_posture"] not in _ALLOWED_POSTURES:
        raise ValueError("invalid audit status/posture")
    out["audit_hash"] = canonical_hash(out)
    return out


def build_operator_narrative_report_governance_audit_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P43 Operator Narrative Report Governance Audit",
        "",
        f"- audit_id: `{packet['audit_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- audit_posture: `{packet['audit_posture']}`",
        f"- findings_fail: `{packet.get('finding_counts', {}).get('FAIL', 0)}`",
        f"- findings_warn: `{packet.get('finding_counts', {}).get('WARN', 0)}`",
        "",
        "## Findings",
    ]
    findings = packet.get("findings", [])
    if findings:
        for f in findings:
            lines.append(f"- `{f['severity']}` `{f['category']}` {f['message']}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_operator_narrative_report_governance_audit(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_report_governance_audit_markdown(packet), encoding="utf-8")
