from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths

SCHEMA_VERSION = "OperatorNarrativeExportPreviewArchiveIndexGovernanceAudit.v1"
PATCH_ID = "PATCH-P53-OPERATOR-NARRATIVE-EXPORT-PREVIEW-ARCHIVE-INDEX-GOVERNANCE-AUDIT-001"
AUDIT_ID = "operator_narrative_export_preview_archive_index_governance_audit_001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"

_EXPECTED_ROLE_ORDER = [
    "p46_export_bundle_json",
    "p46_export_bundle_markdown",
    "p47_export_bundle_governance_audit_json",
    "p47_export_bundle_governance_audit_markdown",
    "p48_static_preview_json",
    "p48_static_preview_markdown",
    "p49_static_preview_governance_audit_json",
    "p49_static_preview_governance_audit_markdown",
]
_P52_REGISTRY_PATHS = [
    "out/archive/operator_narrative_export_preview_archive_index_001.latest.json",
    "out/archive/operator_narrative_export_preview_archive_index_001.latest.md",
]
_P53_REGISTRY_PATHS = [
    "out/audit/operator_narrative_export_preview_archive_index_governance_audit_001.latest.json",
    "out/audit/operator_narrative_export_preview_archive_index_governance_audit_001.latest.md",
]
_BLOCKER_BANNED = {
    "source_missing:p42_report_json",
    "source_missing:p44_ui_overlay_json",
    "overlay report hash lineage mismatch",
}
_ACTIVE_FIELDS = {"command_url", "action_url", "href", "onclick"}
_EXECUTABLE_SCHEMES = ("javascript:", "data:", "http://", "https://")
_PAYLOAD_PATTERNS = ("base64", "payload", "blob")
_MD_SECTIONS = [
    "## Artifact Role Order",
    "## Archive Manifest",
    "## Receipt Status Summary",
    "## Source Hashes",
    "## Receipt Hashes",
    "## Registry Classification Summary",
    "## Blockers",
    "## Governance Boundary",
]
_FORBIDDEN_PROSE = [
    "recommend",
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
    "package",
    "distribution",
    "deploy",
    "release",
]

_GOVERNANCE_FLAGS = {
    "audit_only": True,
    "advisory_only": True,
    "read_only": True,
    "non_authoritative": True,
    "archive_index_governance_audit_only": True,
    "source_linked": True,
    "deterministic_audit": True,
    "package_created": False,
    "distribution_claims_allowed": False,
    "command_authority": False,
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


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str, str | None]:
    text, status = _read_text(path)
    if status != "PRESENT" or text is None:
        return None, status, text
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None, "CORRUPT", text
    if not isinstance(payload, dict):
        return None, "CORRUPT", text
    return payload, "PRESENT", text


def _finding(severity: str, category: str, message: str, refs: list[str]) -> dict[str, Any]:
    normalized = " ".join(message.lower().split())
    evidence = sorted(set(ref for ref in refs if ref))
    finding_id = hashlib.sha256(f"{category}|{normalized}|{'|'.join(evidence)}".encode("utf-8")).hexdigest()
    return {
        "finding_id": finding_id,
        "severity": severity,
        "category": category,
        "message": message,
        "evidence_refs": evidence,
    }


def _walk(obj: Any, path: str = "$") -> list[tuple[str, Any]]:
    out = [(path, obj)]
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(_walk(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(_walk(v, f"{path}[{i}]") )
    return out


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_operator_narrative_export_preview_archive_index_governance_audit_packet(
    *,
    archive_index_json_path: str | Path = "out/archive/operator_narrative_export_preview_archive_index_001.latest.json",
    archive_index_markdown_path: str | Path = "out/archive/operator_narrative_export_preview_archive_index_001.latest.md",
    archive_packet: dict[str, Any] | None = None,
    archive_markdown_text: str | None = None,
) -> dict[str, Any]:
    json_path = Path(archive_index_json_path)
    md_path = Path(archive_index_markdown_path)
    findings: list[dict[str, Any]] = []

    if archive_packet is None:
        packet, json_status, _json_text = _read_json(json_path)
    else:
        packet = deepcopy(archive_packet)
        json_status, _json_text = "PRESENT", json.dumps(packet, sort_keys=True)
    if archive_markdown_text is None:
        md_text, md_status = _read_text(md_path)
    else:
        md_text, md_status = archive_markdown_text, "PRESENT"

    checked = {"archive_index_json": json_path.as_posix(), "archive_index_markdown": md_path.as_posix()}
    if json_status != "PRESENT":
        findings.append(_finding("FAIL", "SOURCE", f"required source not readable: archive_index_json ({json_status})", [json_path.as_posix()]))
    if md_status != "PRESENT":
        findings.append(_finding("FAIL", "SOURCE", f"required source not readable: archive_index_markdown ({md_status})", [md_path.as_posix()]))

    payload = packet or {}
    role_order = payload.get("artifact_role_order") if isinstance(payload.get("artifact_role_order"), list) else []
    manifest = payload.get("archive_manifest") if isinstance(payload.get("archive_manifest"), list) else []
    manifest_ids = [str(item.get("artifact_id", "")) for item in manifest if isinstance(item, dict)]

    if role_order != _EXPECTED_ROLE_ORDER:
        findings.append(_finding("FAIL", "ROLE_ORDER", "artifact_role_order mismatch", ["artifact_role_order"]))
    if manifest_ids != role_order:
        findings.append(_finding("FAIL", "MANIFEST", "archive_manifest artifact order must mirror artifact_role_order", ["archive_manifest", "artifact_role_order"]))

    for idx, item in enumerate(manifest):
        if not isinstance(item, dict):
            findings.append(_finding("FAIL", "MANIFEST", f"manifest entry {idx} is not object", [f"archive_manifest[{idx}]"]))
            continue
        if item.get("passive_reference_only") is not True:
            findings.append(_finding("FAIL", "MANIFEST", f"passive_reference_only must be true for {item.get('artifact_id', idx)}", [f"archive_manifest[{idx}]" ]))
        for key in item:
            low = key.lower()
            if any(token in low for token in _PAYLOAD_PATTERNS):
                findings.append(_finding("FAIL", "MANIFEST", f"embedded payload-like field detected: {key}", [f"archive_manifest[{idx}].{key}"]))

    for path, value in _walk(payload):
        if isinstance(value, str):
            lowered_value = value.lower()
            if lowered_value.startswith(_EXECUTABLE_SCHEMES):
                findings.append(_finding("FAIL", "ACTIVE_SURFACE", f"executable scheme detected at {path}", [path]))
        if path.split(".")[-1] in _ACTIVE_FIELDS:
            findings.append(_finding("FAIL", "ACTIVE_SURFACE", f"active field detected: {path}", [path]))

    expected_hash = ""
    if packet:
        recompute = deepcopy(packet)
        recompute.pop("archive_index_hash", None)
        expected_hash = canonical_hash(recompute)
        if str(packet.get("archive_index_hash", "")) != expected_hash:
            findings.append(_finding("FAIL", "HASH_INTEGRITY", "archive_index_hash mismatch from canonical packet-minus-archive_index_hash recomputation", ["archive_index_hash"]))

    hash_inventory = payload.get("hash_inventory") if isinstance(payload.get("hash_inventory"), dict) else {}
    for item in manifest:
        if not isinstance(item, dict):
            continue
        aid = str(item.get("artifact_id", ""))
        sha = str(item.get("sha256", ""))
        if hash_inventory.get(aid) != sha:
            findings.append(_finding("FAIL", "HASH_INTEGRITY", f"hash_inventory mismatch for {aid}", [aid]))
        path = Path(str(item.get("path", "")))
        if item.get("exists") is True and path.exists() and path.is_file():
            text, st = _read_text(path)
            if st == "PRESENT" and text is not None and _sha256_text(text) != sha:
                findings.append(_finding("FAIL", "HASH_INTEGRITY", f"manifest sha256 mismatch for readable file {aid}", [aid, path.as_posix()]))

    for required in ["p46_export_bundle_json", "p47_export_bundle_governance_audit_json", "p48_static_preview_json", "p49_static_preview_governance_audit_json"]:
        if required not in (payload.get("source_hashes") or {}):
            findings.append(_finding("FAIL", "HASH_INTEGRITY", f"missing source_hashes entry {required}", ["source_hashes"]))
        if required not in (payload.get("receipt_hashes") or {}):
            findings.append(_finding("FAIL", "HASH_INTEGRITY", f"missing receipt_hashes entry {required}", ["receipt_hashes"]))

    receipt = payload.get("governance_receipt_summary") if isinstance(payload.get("governance_receipt_summary"), dict) else {}
    p47 = receipt.get("p47_export_bundle_governance_audit") if isinstance(receipt.get("p47_export_bundle_governance_audit"), dict) else {}
    p49 = receipt.get("p49_static_preview_governance_audit") if isinstance(receipt.get("p49_static_preview_governance_audit"), dict) else {}
    if p47.get("final_status") != "PASS" or p47.get("audit_posture") != "CLEAN":
        findings.append(_finding("FAIL", "RECEIPT_PRESERVATION", "P47 PASS/CLEAN preservation violated", ["governance_receipt_summary.p47_export_bundle_governance_audit"]))
    if p49.get("final_status") != "PASS" or p49.get("audit_posture") != "CLEAN":
        findings.append(_finding("FAIL", "RECEIPT_PRESERVATION", "P49 PASS/CLEAN preservation violated", ["governance_receipt_summary.p49_static_preview_governance_audit"]))

    blockers = payload.get("blocker_summary") if isinstance(payload.get("blocker_summary"), list) else []
    if not blockers and payload:
        findings.append(_finding("FAIL", "BLOCKER_PRESERVATION", "blocker_summary unexpectedly empty (suppression suspected)", ["blocker_summary"]))
    for item in blockers:
        if str(item).strip() in _BLOCKER_BANNED:
            findings.append(_finding("FAIL", "BLOCKER_PRESERVATION", f"reintroduced repaired blocker: {item}", ["blocker_summary"]))

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    ci_targets = set(list_ci_drift_artifact_paths(registry))
    emap = {e.artifact_path: e for e in registry.entries}
    for path in _P52_REGISTRY_PATHS:
        entry = emap.get(path)
        if not entry:
            findings.append(_finding("FAIL", "REGISTRY", f"missing registry entry: {path}", [path]))
            continue
        if entry.determinism_class != "DERIVED_OPTIONAL":
            findings.append(_finding("FAIL", "REGISTRY", f"unexpected determinism_class for {path}: {entry.determinism_class}", [path]))
        if entry.authority_granted is not False:
            findings.append(_finding("FAIL", "REGISTRY", f"authority_granted must be false for {path}", [path]))
        if path in ci_targets:
            findings.append(_finding("FAIL", "REGISTRY", f"artifact should not be ci-drift-enforced: {path}", [path]))

    md_lower = (md_text or "").lower()
    section_positions = [md_lower.find(s.lower()) for s in _MD_SECTIONS]
    if any(pos < 0 for pos in section_positions) or section_positions != sorted(section_positions):
        findings.append(_finding("FAIL", "MARKDOWN_STRUCTURE", "markdown section order mismatch", ["archive_index_markdown"]))

    payload_without_governance = deepcopy(payload)
    if isinstance(payload_without_governance, dict):
        payload_without_governance["governance_flags"] = {}
    scan = json.dumps(payload_without_governance, sort_keys=True).lower() + "\n" + md_lower
    for term in _FORBIDDEN_PROSE:
        if term in scan:
            findings.append(_finding("FAIL", "LANGUAGE_BOUNDARY", f"forbidden prose present: {term}", ["archive_index_json", "archive_index_markdown"]))

    missing_source = json_status != "PRESENT" or md_status != "PRESENT"
    fail_count = sum(1 for f in findings if f["severity"] == "FAIL")
    if missing_source:
        final_status, posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif fail_count:
        final_status, posture = "FAIL", "FAILED"
    else:
        final_status, posture = "PASS", "CLEAN"
        findings.append(_finding("PASS", "SOURCE", "archive index sources readable and auditable", [json_path.as_posix(), md_path.as_posix()]))

    severity_order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    findings = sorted(findings, key=lambda x: (severity_order.get(str(x["severity"]), 9), str(x["category"]), str(x["finding_id"])))

    packet_out: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "audit_id": AUDIT_ID,
        "final_status": final_status,
        "audit_posture": posture,
        "checked_artifacts": checked,
        "findings": findings,
        "finding_counts": {"PASS": sum(1 for f in findings if f["severity"] == "PASS"), "WARN": sum(1 for f in findings if f["severity"] == "WARN"), "FAIL": sum(1 for f in findings if f["severity"] == "FAIL")},
        "role_order_summary": {"expected": _EXPECTED_ROLE_ORDER, "observed": role_order, "manifest_observed": manifest_ids},
        "manifest_summary": {"entry_count": len(manifest), "passive_reference_only_all_true": all(isinstance(i, dict) and i.get("passive_reference_only") is True for i in manifest)},
        "hash_integrity_summary": {"archive_index_hash_matches": bool(packet and str(packet.get("archive_index_hash", "")) == expected_hash), "hash_inventory_keys": list(hash_inventory.keys()) if isinstance(hash_inventory, dict) else []},
        "receipt_preservation_summary": {"p47_final_status": str(p47.get("final_status", NOT_COMPUTABLE)), "p47_audit_posture": str(p47.get("audit_posture", NOT_COMPUTABLE)), "p49_final_status": str(p49.get("final_status", NOT_COMPUTABLE)), "p49_audit_posture": str(p49.get("audit_posture", NOT_COMPUTABLE))},
        "blocker_preservation_summary": {"blocker_count": len(blockers), "repaired_blockers_reintroduced": sorted([b for b in blockers if str(b).strip() in _BLOCKER_BANNED])},
        "registry_classification_summary": {"checked_registry_paths": _P52_REGISTRY_PATHS + _P53_REGISTRY_PATHS, "expected_determinism_class": "DERIVED_OPTIONAL"},
        "language_boundary_summary": {"markdown_sections": _MD_SECTIONS, "forbidden_prose": _FORBIDDEN_PROSE},
        "governance_flag_summary": {"required": deepcopy(_GOVERNANCE_FLAGS)},
        "source_hashes": {"archive_index_json": canonical_hash(packet) if packet else NOT_COMPUTABLE, "archive_index_markdown": _sha256_text(md_text) if md_text is not None else NOT_COMPUTABLE},
        "blocker_summary": sorted(f["message"] for f in findings if f["severity"] == "FAIL"),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {"deterministic": True, "audit_only": True, "read_only": True, "source_linked": True, "fail_closed": True, "source_presence": {"archive_index_json": json_status, "archive_index_markdown": md_status}},
    }
    packet_out["audit_hash"] = canonical_hash(packet_out)
    return packet_out


def build_operator_narrative_export_preview_archive_index_governance_audit_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P53 Operator Narrative Export / Preview Archive Index Governance Audit",
        "",
        f"- audit_id: `{packet.get('audit_id', '')}`",
        f"- final_status: `{packet.get('final_status', '')}`",
        f"- audit_posture: `{packet.get('audit_posture', '')}`",
        f"- audit_hash: `{packet.get('audit_hash', '')}`",
        "",
        "## Findings",
    ]
    for finding in packet.get("findings", []):
        lines.append(f"- `{finding.get('severity', '')}` `{finding.get('category', '')}` {finding.get('message', '')}")
    lines.extend(["", "## Finding Counts"])
    for k, v in (packet.get("finding_counts") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Role Order Summary"])
    ros = packet.get("role_order_summary", {})
    lines.append(f"- expected: `{ros.get('expected', [])}`")
    lines.append(f"- observed: `{ros.get('observed', [])}`")
    lines.append(f"- manifest_observed: `{ros.get('manifest_observed', [])}`")
    lines.extend(["", "## Governance Boundary"])
    for k, v in sorted((packet.get("governance_flags") or {}).items()):
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_export_preview_archive_index_governance_audit(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_export_preview_archive_index_governance_audit_markdown(packet), encoding="utf-8")
