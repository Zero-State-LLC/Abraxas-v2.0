from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "OperatorNarrativeExportBundleGovernanceAudit.v1"
PATCH_ID = "PATCH-P47-OPERATOR-NARRATIVE-EXPORT-BUNDLE-GOVERNANCE-AUDIT-001"
AUDIT_ID = "operator_narrative_export_bundle_governance_audit_001"

_EXPECTED_ROLES = [
    "report_json",
    "report_markdown",
    "report_governance_audit_json",
    "report_governance_audit_markdown",
    "ui_overlay_json",
    "ui_overlay_markdown",
    "ui_overlay_governance_audit_json",
    "ui_overlay_governance_audit_markdown",
]
_REQUIRED_MANIFEST_FIELDS = ["artifact_id", "role", "path", "exists", "readable", "sha256", "classification", "passive_reference_only"]
_FORBIDDEN_PHRASES = [
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
    "next move",
    "command url",
    "action url",
    "executable",
]
_JSON_SCAN_EXCLUSIONS = {
    "command_authority", "ui_command_authority", "action_authority", "recommendation_authority", "inference_authority", "prediction_allowed",
    "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed", "mutation_allowed", "execution_authority", "routing_change_allowed",
    "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "adaptive_behavior_allowed", "auto_execute", "auto_approve", "command_channel",
}

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "audit_only": True,
    "advisory_only": True,
    "non_authoritative": True,
    "export_governance_audit_only": True,
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
}
_AFFIRM = ["export_only", "passive_bundle_only", "read_only", "advisory_only", "non_authoritative", "source_linked", "deterministic_manifest"]
_DENY = ["command_authority", "ui_command_authority", "action_authority", "recommendation_authority", "inference_authority", "prediction_allowed", "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed", "mutation_allowed", "authority_granted", "execution_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "adaptive_behavior_allowed", "psychological_claims_allowed", "speculative_causation_allowed", "auto_execute", "auto_approve", "command_channel", "bidirectional_control"]


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
    normalized = message.strip().lower()
    refs_sorted = sorted(set(r for r in refs if r))
    fid = hashlib.sha256(f"{category}|{normalized}|{'|'.join(refs_sorted)}".encode("utf-8")).hexdigest()
    return {"finding_id": fid, "severity": severity, "category": category, "message": message, "evidence_refs": refs_sorted}


def _collect_string_values(obj: Any) -> list[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, list):
        out: list[str] = []
        for x in obj:
            out.extend(_collect_string_values(x))
        return out
    if isinstance(obj, dict):
        out = []
        for v in obj.values():
            out.extend(_collect_string_values(v))
        return out
    return []


def build_operator_narrative_export_bundle_governance_audit_packet(*, export_bundle_path: str | Path = "out/exports/operator_narrative_export_bundle_001.latest.json", export_bundle_markdown_path: str | Path = "out/exports/operator_narrative_export_bundle_001.latest.md", export_bundle_packet: dict[str, Any] | None = None, export_bundle_markdown_text: str | None = None) -> dict[str, Any]:
    json_path = Path(export_bundle_path)
    md_path = Path(export_bundle_markdown_path)
    findings: list[dict[str, Any]] = []

    if export_bundle_packet is None:
        bundle, bundle_status = _read_json(json_path)
    else:
        bundle, bundle_status = deepcopy(export_bundle_packet), "PRESENT"
    if export_bundle_markdown_text is None:
        md_text, md_status = _read_text(md_path)
    else:
        md_text, md_status = export_bundle_markdown_text, "PRESENT"

    presence = {"export_bundle_json": bundle_status, "export_bundle_markdown": md_status}
    if bundle_status != "PRESENT":
        findings.append(_finding("FAIL", "SOURCE", f"required source not readable: export_bundle_json ({bundle_status})", [json_path.as_posix()]))
    if md_status != "PRESENT":
        findings.append(_finding("FAIL", "SOURCE", f"required source not readable: export_bundle_markdown ({md_status})", [md_path.as_posix()]))

    bundle = bundle or {}
    manifest = bundle.get("artifact_manifest", []) if isinstance(bundle.get("artifact_manifest"), list) else []
    roles = [str(m.get("role", "")) for m in manifest if isinstance(m, dict)]
    missing_roles = [r for r in _EXPECTED_ROLES if r not in roles]
    duplicate_roles = sorted({r for r in roles if roles.count(r) > 1})
    extra_roles = [r for r in roles if r not in _EXPECTED_ROLES]
    if roles != _EXPECTED_ROLES:
        findings.append(_finding("FAIL", "MANIFEST", "artifact_manifest role sequence mismatch", ["artifact_manifest", *_EXPECTED_ROLES]))
    if missing_roles:
        findings.append(_finding("FAIL", "MANIFEST", f"missing required roles: {', '.join(missing_roles)}", missing_roles))
    if duplicate_roles:
        findings.append(_finding("FAIL", "MANIFEST", f"duplicate roles present: {', '.join(duplicate_roles)}", duplicate_roles))
    if extra_roles:
        findings.append(_finding("FAIL", "MANIFEST", f"unexpected extra roles present: {', '.join(extra_roles)}", extra_roles))

    for idx, m in enumerate(manifest):
        if not isinstance(m, dict):
            findings.append(_finding("FAIL", "MANIFEST", f"manifest entry at index {idx} is not an object", [f"artifact_manifest[{idx}]"]))
            continue
        for fld in _REQUIRED_MANIFEST_FIELDS:
            if fld not in m:
                findings.append(_finding("FAIL", "MANIFEST", f"manifest entry missing required field: {fld}", [str(m.get("artifact_id", f"idx:{idx}"))]))
        if m.get("passive_reference_only") is not True:
            findings.append(_finding("FAIL", "MANIFEST", f"manifest passive_reference_only must be true for {m.get('artifact_id', idx)}", [str(m.get("artifact_id", idx))]))

    inv = bundle.get("hash_inventory", {}) if isinstance(bundle.get("hash_inventory"), dict) else {}
    expected_inv = {str(m.get("artifact_id", "")): str(m.get("sha256", "")) for m in manifest if isinstance(m, dict)}
    if list(inv.keys()) != list(expected_inv.keys()):
        findings.append(_finding("FAIL", "HASH_INVENTORY", "hash_inventory keys must match manifest artifact order", ["hash_inventory", "artifact_manifest"]))
    for k, v in expected_inv.items():
        if inv.get(k) != v:
            findings.append(_finding("FAIL", "HASH_INVENTORY", f"hash mismatch for {k}", [k]))

    lineage = bundle.get("source_lineage_map")
    if not isinstance(lineage, dict) or not lineage:
        findings.append(_finding("FAIL", "LINEAGE", "source_lineage_map missing or empty", ["source_lineage_map"]))
    elif list(lineage.keys()) != sorted(lineage.keys()):
        findings.append(_finding("FAIL", "LINEAGE", "source_lineage_map keys not sorted", list(lineage.keys())))

    envelope = bundle.get("governance_envelope") if isinstance(bundle.get("governance_envelope"), dict) else {}
    for k in _AFFIRM:
        if envelope.get(k) is not True:
            findings.append(_finding("FAIL", "GOVERNANCE", f"governance_envelope affirm flag must be true: {k}", [k]))
    for k in _DENY:
        if envelope.get(k) is not False:
            findings.append(_finding("FAIL", "GOVERNANCE", f"governance_envelope deny flag must be false: {k}", [k]))

    recompute = deepcopy(bundle)
    recompute.pop("bundle_hash", None)
    recomputed = canonical_hash(recompute)
    if str(bundle.get("bundle_hash", "")) != recomputed:
        findings.append(_finding("FAIL", "BUNDLE_HASH", "bundle_hash mismatch from canonical packet-minus-bundle_hash recomputation", ["bundle_hash"]))

    notes = bundle.get("passive_export_notes")
    if not isinstance(notes, list) or not notes:
        findings.append(_finding("FAIL", "LANGUAGE_BOUNDARY", "passive_export_notes missing or empty", ["passive_export_notes"]))

    scan_payload = deepcopy(bundle)
    if isinstance(scan_payload, dict):
        scan_payload["governance_envelope"] = {}
        scan_payload["governance_flags"] = {}
        scan_payload["blocker_summary"] = []
    scan_text = "\n".join(_collect_string_values(scan_payload)).lower() + "\n" + (md_text or "").lower()
    for term in _FORBIDDEN_PHRASES:
        if term in scan_text:
            findings.append(_finding("FAIL", "LANGUAGE_BOUNDARY", f"forbidden phrase present: {term}", ["export_bundle_json", "export_bundle_markdown"]))

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    ci_targets = set(list_ci_drift_artifact_paths(registry))
    emap = {e.artifact_path: e for e in registry.entries}
    checked_paths = ["out/exports/operator_narrative_export_bundle_001.latest.json", "out/exports/operator_narrative_export_bundle_001.latest.md", "out/audit/operator_narrative_export_bundle_governance_audit_001.latest.json", "out/audit/operator_narrative_export_bundle_governance_audit_001.latest.md"]
    for p in checked_paths:
        if p not in emap:
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"missing registry entry: {p}", [p]))
            continue
        if emap[p].determinism_class != "DERIVED_OPTIONAL":
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"unexpected determinism_class for {p}: {emap[p].determinism_class}", [p]))
        if p.startswith("out/exports/") and p in ci_targets:
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"export artifact should not be ci-drift-enforced: {p}", [p]))

    missing_source = any(v != "PRESENT" for v in presence.values())
    fail_count = sum(1 for f in findings if f["severity"] == "FAIL")
    warn_count = sum(1 for f in findings if f["severity"] == "WARN")
    if missing_source:
        final_status, posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif fail_count:
        final_status, posture = "FAIL", "FAILED"
    elif warn_count:
        final_status, posture = "WARN", "WARNING"
    else:
        final_status, posture = "PASS", "CLEAN"
        findings.append(_finding("PASS", "SOURCE", "all required export bundle sources were readable", [json_path.as_posix(), md_path.as_posix()]))

    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    findings = sorted(findings, key=lambda x: (order.get(str(x["severity"]), 9), str(x["category"]), str(x["finding_id"])))

    out: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "audit_id": AUDIT_ID,
        "final_status": final_status,
        "audit_posture": posture,
        "checked_artifacts": {"operator_narrative_export_bundle_json": json_path.as_posix(), "operator_narrative_export_bundle_markdown": md_path.as_posix()},
        "findings": findings,
        "finding_counts": {"PASS": sum(1 for f in findings if f["severity"] == "PASS"), "WARN": sum(1 for f in findings if f["severity"] == "WARN"), "FAIL": sum(1 for f in findings if f["severity"] == "FAIL")},
        "manifest_integrity_summary": {"required_roles": _EXPECTED_ROLES, "observed_roles": roles, "required_fields": _REQUIRED_MANIFEST_FIELDS},
        "hash_inventory_summary": {"hash_inventory_keys": list(inv.keys()), "manifest_artifact_ids": list(expected_inv.keys()), "matches_manifest": inv == expected_inv},
        "lineage_summary": {"source_lineage_map_present": isinstance(lineage, dict) and bool(lineage), "source_lineage_keys_sorted": isinstance(lineage, dict) and list(lineage.keys()) == sorted(lineage.keys())},
        "governance_envelope_summary": {"required_affirm_flags": _AFFIRM, "required_deny_flags": _DENY},
        "language_boundary_summary": {"forbidden_phrases": _FORBIDDEN_PHRASES, "scan_exclusions": sorted(_JSON_SCAN_EXCLUSIONS)},
        "registry_classification_summary": {"checked_registry_paths": checked_paths, "expected_determinism_class": "DERIVED_OPTIONAL", "expected_non_ci_drift_enforced_exports": checked_paths[:2]},
        "source_hashes": {"operator_narrative_export_bundle_json": canonical_hash(bundle) if bundle else NOT_COMPUTABLE, "operator_narrative_export_bundle_markdown": hashlib.sha256((md_text or "").encode("utf-8")).hexdigest() if md_text is not None else NOT_COMPUTABLE},
        "blocker_summary": sorted(f["message"] for f in findings if f["severity"] == "FAIL"),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {"source_packet_presence": presence, "deterministic": True, "audit_only": True, "advisory_only": True, "non_authoritative": True, "fail_closed": True},
    }
    out["audit_hash"] = canonical_hash(out)
    return out


def build_operator_narrative_export_bundle_governance_audit_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P47 Operator Narrative Export Bundle Governance Audit",
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
        for f in findings:
            lines.append(f"- `{f['severity']}` `{f['category']}` `{f['finding_id']}`")
    else:
        lines.append("- none")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_export_bundle_governance_audit(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_export_bundle_governance_audit_markdown(packet), encoding="utf-8")
