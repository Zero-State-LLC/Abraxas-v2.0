from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths
from core.operator_narrative_static_preview_bundle import PREVIEW_SECTIONS

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "OperatorNarrativeStaticPreviewGovernanceAudit.v1"
PATCH_ID = "PATCH-P49-OPERATOR-NARRATIVE-STATIC-PREVIEW-GOVERNANCE-AUDIT-001"
AUDIT_ID = "operator_narrative_static_preview_governance_audit_001"

_AFFIRM = ["preview_only", "static_only", "passive_preview_only", "read_only", "non_interactive", "non_authoritative", "source_linked", "advisory_only"]
_DENY = [
    "command_authority", "ui_command_authority", "action_authority", "recommendation_authority", "inference_authority",
    "prediction_allowed", "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed", "mutation_allowed",
    "authority_granted", "execution_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed",
    "runtime_mutation_allowed", "adaptive_behavior_allowed", "psychological_claims_allowed", "speculative_causation_allowed",
    "auto_execute", "auto_approve", "command_channel", "bidirectional_control", "script_allowed", "html_script_allowed",
    "external_fetch_allowed", "form_allowed", "button_allowed",
]
_ACTIVE_FIELDS = ["command_url", "action_url", "href", "onclick"]
_ACTIVE_SURFACE_FLAGS = ["script_allowed", "html_script_allowed", "external_fetch_allowed", "form_allowed", "button_allowed"]
_EXECUTABLE_SCHEMES = ["javascript:", "data:", "http://", "https://"]
_FORBIDDEN_PHRASES = [
    "recommend", "should do", "forecast", "will happen", "readiness", "take action", "execute", "approve", "route",
    "mutate", "prediction", "next move", "button", "form", "script", "javascript", "fetch",
]
_REGISTRY_PATHS = ["out/previews/operator_narrative_static_preview_001.latest.json", "out/previews/operator_narrative_static_preview_001.latest.md"]
_GOVERNANCE_FLAGS: dict[str, Any] = {
    "audit_only": True,
    "advisory_only": True,
    "non_authoritative": True,
    "static_preview_governance_audit_only": True,
    "read_only": True,
    "source_linked": True,
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
    "command_authority": False,
    "ui_command_authority": False,
    "adaptive_behavior_allowed": False,
    "routing_change_allowed": False,
    "queue_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "psychological_claims_allowed": False,
    "speculative_causation_allowed": False,
    "auto_execute": False,
    "auto_approve": False,
    "command_channel": False,
    "bidirectional_control": False,
    "script_allowed": False,
    "html_script_allowed": False,
    "external_fetch_allowed": False,
    "form_allowed": False,
    "button_allowed": False,
}


def _read_text(path: Path) -> tuple[str | None, str]:
    try:
        return path.read_text(encoding="utf-8"), "PRESENT"
    except FileNotFoundError:
        return None, "MISSING"
    except OSError:
        return None, "CORRUPT"


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    text, status = _read_text(path)
    if status != "PRESENT" or text is None:
        return None, status
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None, "CORRUPT"
    return (payload, "PRESENT") if isinstance(payload, dict) else (None, "CORRUPT")


def _finding(severity: str, category: str, message: str, refs: list[str]) -> dict[str, Any]:
    refs_sorted = sorted(set(r for r in refs if r))
    fid = hashlib.sha256(f"{category}|{message.strip().lower()}|{'|'.join(refs_sorted)}".encode("utf-8")).hexdigest()
    return {"finding_id": fid, "severity": severity, "category": category, "message": message, "evidence_refs": refs_sorted}


def _collect_string_values(obj: Any) -> list[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, list):
        out: list[str] = []
        for item in obj:
            out.extend(_collect_string_values(item))
        return out
    if isinstance(obj, dict):
        out = []
        for value in obj.values():
            out.extend(_collect_string_values(value))
        return out
    return []


def _collect_keys(obj: Any, prefix: str = "") -> list[tuple[str, str]]:
    if isinstance(obj, dict):
        out: list[tuple[str, str]] = []
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            out.append((str(key), path))
            out.extend(_collect_keys(value, path))
        return out
    if isinstance(obj, list):
        out = []
        for idx, value in enumerate(obj):
            out.extend(_collect_keys(value, f"{prefix}[{idx}]"))
        return out
    return []


def _markdown_without_governance_boundary(md_text: str) -> str:
    lines = md_text.splitlines()
    kept: list[str] = []
    skipping = False
    for line in lines:
        if line.startswith("## governance_boundary"):
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            kept.append(line)
    return "\n".join(kept)


def _markdown_section_order(md_text: str) -> list[str]:
    headings = []
    for line in md_text.splitlines():
        if line.startswith("## "):
            headings.append(line.removeprefix("## ").strip())
    return [heading for heading in headings if heading in PREVIEW_SECTIONS]


def _is_passive_reference(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    low = value.strip().lower()
    if any(scheme in low for scheme in _EXECUTABLE_SCHEMES):
        return False
    return value.startswith("out/") and value.endswith((".json", ".md"))


def build_operator_narrative_static_preview_governance_audit_packet(
    *,
    preview_path: str | Path = "out/previews/operator_narrative_static_preview_001.latest.json",
    preview_markdown_path: str | Path = "out/previews/operator_narrative_static_preview_001.latest.md",
    preview_packet: dict[str, Any] | None = None,
    preview_markdown_text: str | None = None,
) -> dict[str, Any]:
    json_path = Path(preview_path)
    md_path = Path(preview_markdown_path)
    findings: list[dict[str, Any]] = []

    if preview_packet is None:
        preview, preview_status = _read_json(json_path)
    else:
        preview, preview_status = deepcopy(preview_packet), "PRESENT"
    if preview_markdown_text is None:
        md_text, md_status = _read_text(md_path)
    else:
        md_text, md_status = preview_markdown_text, "PRESENT"

    presence = {"static_preview_json": preview_status, "static_preview_markdown": md_status}
    if preview_status != "PRESENT":
        findings.append(_finding("FAIL", "SOURCE", f"required source not readable: static_preview_json ({preview_status})", [json_path.as_posix()]))
    if md_status != "PRESENT":
        findings.append(_finding("FAIL", "SOURCE", f"required source not readable: static_preview_markdown ({md_status})", [md_path.as_posix()]))

    preview = preview or {}
    md_text = md_text or ""

    observed_sections = preview.get("preview_sections") if isinstance(preview.get("preview_sections"), list) else []
    if observed_sections != PREVIEW_SECTIONS:
        findings.append(_finding("FAIL", "SECTION_ORDER", "preview_sections fixed order mismatch", ["preview_sections", *PREVIEW_SECTIONS]))

    md_sections = _markdown_section_order(md_text)
    if md_sections != PREVIEW_SECTIONS:
        findings.append(_finding("FAIL", "SECTION_ORDER", "markdown preview section order mismatch", [md_path.as_posix(), *PREVIEW_SECTIONS]))

    recompute = deepcopy(preview)
    recompute.pop("preview_hash", None)
    recomputed_preview_hash = canonical_hash(recompute) if preview else NOT_COMPUTABLE
    observed_preview_hash = str(preview.get("preview_hash", ""))
    if preview_status == "PRESENT" and observed_preview_hash != recomputed_preview_hash:
        findings.append(_finding("FAIL", "PREVIEW_HASH", "preview_hash mismatch from canonical packet-minus-preview_hash recomputation", ["preview_hash"]))

    passive_refs = preview.get("passive_references")
    passive_ref_count = 0
    if not isinstance(passive_refs, dict) or not passive_refs:
        findings.append(_finding("FAIL", "PASSIVE_REFERENCES", "passive_references missing or not object-shaped", ["passive_references"]))
        passive_refs = {}
    for key, value in passive_refs.items():
        passive_ref_count += 1
        if not _is_passive_reference(value):
            findings.append(_finding("FAIL", "PASSIVE_REFERENCES", f"passive reference must be local passive artifact path: {key}", [f"passive_references.{key}"]))

    for key, path in _collect_keys(preview):
        if key in _ACTIVE_FIELDS:
            findings.append(_finding("FAIL", "ACTIVE_SURFACE", f"active field is forbidden: {key}", [path]))
    for text in _collect_string_values(passive_refs):
        low = text.lower()
        for scheme in _EXECUTABLE_SCHEMES:
            if scheme in low:
                findings.append(_finding("FAIL", "ACTIVE_SURFACE", f"executable URL scheme is forbidden: {scheme}", [text]))

    flags = preview.get("governance_flags") if isinstance(preview.get("governance_flags"), dict) else {}
    for flag in _AFFIRM:
        if flags.get(flag) is not True:
            findings.append(_finding("FAIL", "GOVERNANCE", f"governance affirm flag must be true: {flag}", [f"governance_flags.{flag}"]))
    for flag in _DENY:
        if flags.get(flag) is not False:
            findings.append(_finding("FAIL", "GOVERNANCE", f"governance deny flag must be false: {flag}", [f"governance_flags.{flag}"]))
    for flag in _ACTIVE_SURFACE_FLAGS:
        if flags.get(flag) is True:
            findings.append(_finding("FAIL", "ACTIVE_SURFACE", f"active surface flag must not be enabled: {flag}", [f"governance_flags.{flag}"]))

    scan_payload = deepcopy(preview)
    if isinstance(scan_payload, dict):
        scan_payload["governance_flags"] = {}
        scan_payload["governance_preview"] = {}
        scan_payload["preview_sections"] = []
        scan_payload["source_hashes"] = {}
        scan_payload["source_artifacts"] = {}
        scan_payload["passive_references"] = {}
    scan_text = "\n".join(_collect_string_values(scan_payload)).lower() + "\n" + _markdown_without_governance_boundary(md_text).lower()
    forbidden_hits = []
    for phrase in _FORBIDDEN_PHRASES:
        if phrase in scan_text:
            forbidden_hits.append(phrase)
            findings.append(_finding("FAIL", "LANGUAGE_BOUNDARY", f"forbidden phrase present: {phrase}", [json_path.as_posix(), md_path.as_posix()]))

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    ci_targets = set(list_ci_drift_artifact_paths(registry))
    emap = {entry.artifact_path: entry for entry in registry.entries}
    registry_observed: dict[str, dict[str, Any]] = {}
    for artifact_path in _REGISTRY_PATHS:
        entry = emap.get(artifact_path)
        registry_observed[artifact_path] = {
            "present": entry is not None,
            "determinism_class": entry.determinism_class if entry else NOT_COMPUTABLE,
            "authority_granted": entry.authority_granted if entry else NOT_COMPUTABLE,
            "ci_drift_enforced": artifact_path in ci_targets,
        }
        if entry is None:
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"missing registry entry: {artifact_path}", [artifact_path]))
            continue
        if entry.determinism_class != "DERIVED_OPTIONAL":
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"unexpected determinism_class for {artifact_path}: {entry.determinism_class}", [artifact_path]))
        if entry.authority_granted is not False:
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"registry entry must be non-authoritative: {artifact_path}", [artifact_path]))
        if artifact_path in ci_targets:
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"preview artifact should not be ci-drift-enforced: {artifact_path}", [artifact_path]))

    missing_source = any(status != "PRESENT" for status in presence.values())
    fail_count = sum(1 for finding in findings if finding["severity"] == "FAIL")
    warn_count = sum(1 for finding in findings if finding["severity"] == "WARN")
    if missing_source:
        final_status, posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif fail_count:
        final_status, posture = "FAIL", "FAILED"
    elif warn_count:
        final_status, posture = "WARN", "WARNING"
    else:
        final_status, posture = "PASS", "CLEAN"
        findings.append(_finding("PASS", "SOURCE", "all required static preview sources were readable", [json_path.as_posix(), md_path.as_posix()]))

    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    findings = sorted(findings, key=lambda item: (order.get(str(item["severity"]), 9), str(item["category"]), str(item["finding_id"])))

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "audit_id": AUDIT_ID,
        "final_status": final_status,
        "audit_posture": posture,
        "checked_artifacts": {"operator_narrative_static_preview_json": json_path.as_posix(), "operator_narrative_static_preview_markdown": md_path.as_posix()},
        "findings": findings,
        "finding_counts": {"PASS": sum(1 for f in findings if f["severity"] == "PASS"), "WARN": sum(1 for f in findings if f["severity"] == "WARN"), "FAIL": sum(1 for f in findings if f["severity"] == "FAIL")},
        "preview_section_summary": {"expected_sections": PREVIEW_SECTIONS, "observed_sections": observed_sections, "markdown_sections": md_sections},
        "preview_hash_summary": {"observed_preview_hash": observed_preview_hash or NOT_COMPUTABLE, "recomputed_preview_hash": recomputed_preview_hash, "matches": observed_preview_hash == recomputed_preview_hash},
        "passive_reference_summary": {"reference_count": passive_ref_count, "required_passive_local_paths": True, "forbidden_url_schemes": _EXECUTABLE_SCHEMES, "forbidden_active_fields": _ACTIVE_FIELDS},
        "governance_flag_summary": {"required_affirm_flags": _AFFIRM, "required_deny_flags": _DENY, "active_surface_flags": _ACTIVE_SURFACE_FLAGS},
        "language_boundary_summary": {"forbidden_phrases": _FORBIDDEN_PHRASES, "forbidden_hits": sorted(forbidden_hits), "markdown_scan_exclusion": "governance_boundary"},
        "registry_classification_summary": {"checked_registry_paths": _REGISTRY_PATHS, "expected_determinism_class": "DERIVED_OPTIONAL", "observed": registry_observed},
        "source_hashes": {"operator_narrative_static_preview_json": canonical_hash(preview) if preview else NOT_COMPUTABLE, "operator_narrative_static_preview_markdown": hashlib.sha256(md_text.encode("utf-8")).hexdigest() if md_text else NOT_COMPUTABLE},
        "blocker_summary": sorted(f["message"] for f in findings if f["severity"] == "FAIL"),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {"source_packet_presence": presence, "deterministic": True, "audit_only": True, "advisory_only": True, "non_authoritative": True, "read_only": True, "source_linked": True, "fail_closed": True},
    }
    packet["audit_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_static_preview_governance_audit_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P49 Operator Narrative Static Preview Governance Audit",
        "",
        f"- audit_id: `{packet.get('audit_id', '')}`",
        f"- final_status: `{packet.get('final_status', '')}`",
        f"- audit_posture: `{packet.get('audit_posture', '')}`",
        f"- findings_fail: `{packet.get('finding_counts', {}).get('FAIL', 0)}`",
        f"- findings_warn: `{packet.get('finding_counts', {}).get('WARN', 0)}`",
        "",
        "## Findings",
    ]
    findings = packet.get("findings", [])
    if findings:
        for finding in findings:
            lines.append(f"- `{finding['severity']}` `{finding['category']}` `{finding['finding_id']}`")
    else:
        lines.append("- none")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_static_preview_governance_audit(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_static_preview_governance_audit_markdown(packet), encoding="utf-8")
