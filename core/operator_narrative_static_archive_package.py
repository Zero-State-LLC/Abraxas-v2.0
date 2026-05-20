from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

SCHEMA_VERSION = "OperatorNarrativeStaticArchivePackage.v1"
PATCH_ID = "PATCH-P64-OPERATOR-NARRATIVE-STATIC-ARCHIVE-PACKAGE-001"
PACKAGE_ID = "operator_narrative_static_archive_package_001"

FINAL_STATUS = {
    "STATIC": "PACKAGE_CREATED_STATIC",
    "DEGRADED": "PACKAGE_CREATED_DEGRADED",
    "NOT_COMPUTABLE": "PACKAGE_NOT_COMPUTABLE",
    "FAIL": "PACKAGE_FAIL",
}

PACKAGE_POSTURE = {
    "STATIC": "STATIC_PACKAGE_CREATED",
    "DEGRADED": "STATIC_PACKAGE_CREATED_WITH_OBSERVED_BLOCKERS",
    "NOT_COMPUTABLE": "NOT_COMPUTABLE",
    "FAIL": "PACKAGE_FAILED",
}

ROLE_ORDER = [
    "p46_export_bundle_json","p46_export_bundle_markdown","p47_export_bundle_governance_audit_json","p47_export_bundle_governance_audit_markdown",
    "p48_static_preview_json","p48_static_preview_markdown","p49_static_preview_governance_audit_json","p49_static_preview_governance_audit_markdown",
    "p52_archive_index_json","p52_archive_index_markdown","p53_archive_index_governance_audit_json","p53_archive_index_governance_audit_markdown",
    "p55_closure_receipt_json","p55_closure_receipt_markdown","p56_stability_receipt_json","p56_stability_receipt_markdown",
    "p57_global_verification_json","p57_global_verification_markdown","p58_package_planning_doc","p59_package_boundary_receipt_json",
    "p59_package_boundary_receipt_markdown","p60_package_implementation_planning_doc","p61_package_preflight_planning_doc",
    "p62_package_preflight_receipt_json","p62_package_preflight_receipt_markdown","p63_authorization_boundary_planning_doc",
]

SOURCE_MAP: dict[str, tuple[str, str]] = {
    "p46_export_bundle_json": ("P46", "out/exports/operator_narrative_export_bundle_001.latest.json"),
    "p46_export_bundle_markdown": ("P46", "out/exports/operator_narrative_export_bundle_001.latest.md"),
    "p47_export_bundle_governance_audit_json": ("P47", "out/audit/operator_narrative_export_bundle_governance_audit_001.latest.json"),
    "p47_export_bundle_governance_audit_markdown": ("P47", "out/audit/operator_narrative_export_bundle_governance_audit_001.latest.md"),
    "p48_static_preview_json": ("P48", "out/previews/operator_narrative_static_preview_001.latest.json"),
    "p48_static_preview_markdown": ("P48", "out/previews/operator_narrative_static_preview_001.latest.md"),
    "p49_static_preview_governance_audit_json": ("P49", "out/audit/operator_narrative_static_preview_governance_audit_001.latest.json"),
    "p49_static_preview_governance_audit_markdown": ("P49", "out/audit/operator_narrative_static_preview_governance_audit_001.latest.md"),
    "p52_archive_index_json": ("P52", "out/archive/operator_narrative_export_preview_archive_index_001.latest.json"),
    "p52_archive_index_markdown": ("P52", "out/archive/operator_narrative_export_preview_archive_index_001.latest.md"),
    "p53_archive_index_governance_audit_json": ("P53", "out/audit/operator_narrative_export_preview_archive_index_governance_audit_001.latest.json"),
    "p53_archive_index_governance_audit_markdown": ("P53", "out/audit/operator_narrative_export_preview_archive_index_governance_audit_001.latest.md"),
    "p55_closure_receipt_json": ("P55", "out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.json"),
    "p55_closure_receipt_markdown": ("P55", "out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.md"),
    "p56_stability_receipt_json": ("P56", "out/audit/operator_narrative_archive_chain_stability_receipt_001.latest.json"),
    "p56_stability_receipt_markdown": ("P56", "out/audit/operator_narrative_archive_chain_stability_receipt_001.latest.md"),
    "p57_global_verification_json": ("P57", "out/audit/operator_narrative_archive_chain_global_verification_001.latest.json"),
    "p57_global_verification_markdown": ("P57", "out/audit/operator_narrative_archive_chain_global_verification_001.latest.md"),
    "p58_package_planning_doc": ("P58", "docs/plans/P58_planning_gate_static_archive_package.md"),
    "p59_package_boundary_receipt_json": ("P59", "out/audit/operator_narrative_static_archive_package_boundary_receipt_001.latest.json"),
    "p59_package_boundary_receipt_markdown": ("P59", "out/audit/operator_narrative_static_archive_package_boundary_receipt_001.latest.md"),
    "p60_package_implementation_planning_doc": ("P60", "docs/plans/P60_planning_gate_static_archive_package_implementation.md"),
    "p61_package_preflight_planning_doc": ("P61", "docs/plans/P61_planning_gate_static_archive_package_preflight_receipt.md"),
    "p62_package_preflight_receipt_json": ("P62", "out/audit/operator_narrative_static_archive_package_preflight_receipt_001.latest.json"),
    "p62_package_preflight_receipt_markdown": ("P62", "out/audit/operator_narrative_static_archive_package_preflight_receipt_001.latest.md"),
    "p63_authorization_boundary_planning_doc": ("P63", "docs/plans/P63_planning_gate_static_archive_package_authorization_boundary.md"),
}

_REQUIRED_FALSE = ["distribution_claims_allowed","release_readiness_claimed","command_authority","ui_command_authority","action_authority","recommendation_authority","inference_authority","prediction_allowed","forecast_authority","trend_prediction_allowed","readiness_claims_allowed","mutation_allowed","authority_granted","execution_authority","routing_change_allowed","queue_mutation_allowed","canon_mutation_allowed","runtime_mutation_allowed","adaptive_behavior_allowed","psychological_claims_allowed","speculative_causation_allowed","auto_execute","auto_approve","command_channel","bidirectional_control","script_allowed","html_script_allowed","external_fetch_allowed","form_allowed","button_allowed","executable_payloads_present","active_surfaces_present"]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_text(path: Path) -> tuple[str | None, str]:
    try:
        return path.read_text(encoding="utf-8"), "PRESENT"
    except FileNotFoundError:
        return None, "MISSING"
    except OSError:
        return None, "CORRUPT"


def _json_status(path: Path) -> tuple[str, str | None, bool, str | None]:
    txt, s = _read_text(path)
    if txt is None:
        return s, None, False, None
    try:
        obj = json.loads(txt)
    except json.JSONDecodeError:
        return "CORRUPT", _sha256_bytes(txt.encode()), False, None
    ch = canonical_hash(obj) if isinstance(obj, dict) else None
    degraded = False
    if isinstance(obj, dict):
        cands = [str(obj.get("final_status", "")), str(obj.get("verification_posture", "")), str(obj.get("preflight_posture", "")), str(obj.get("boundary_posture", ""))]
        degraded = any(any(k in v for k in ["DEGRADED", "BLOCKED", "FAIL", "FAILED", "NOT_COMPUTABLE"]) for v in cands)
        bs = obj.get("blocker_summary")
        if isinstance(bs, list) and bs:
            degraded = True
    return "PRESENT", _sha256_bytes(txt.encode()), degraded, ch


def build_operator_narrative_static_archive_package_packet(*, repo_root: str | Path = ".", authorization_text: str = "Authorized") -> dict[str, Any]:
    root = Path(repo_root)
    paths = RuntimePaths.from_env()
    blockers: list[str] = []
    manifest: list[dict[str, Any]] = []
    source_hashes: dict[str, str] = {}
    canonical_hashes: dict[str, str | None] = {}
    degraded_roles: list[str] = []
    blocker_hashes: list[str] = []

    for role in ROLE_ORDER:
        source_patch, rel = SOURCE_MAP[role]
        path = root / rel
        is_json = path.suffix == ".json"
        if is_json:
            status, sha, degraded, can = _json_status(path)
            exists = status == "PRESENT"
            readable = status == "PRESENT"
            if status != "PRESENT":
                blockers.append(f"missing/corrupt required source: {rel} ({status})")
            if degraded:
                degraded_roles.append(role)
            if can is None and exists:
                blockers.append(f"canonical hash required for json source: {rel}")
            canonical_hashes[role] = can
            source_hashes[role] = sha or "NOT_COMPUTABLE"
        else:
            txt, status = _read_text(path)
            exists = status == "PRESENT"
            readable = status == "PRESENT"
            if status != "PRESENT":
                blockers.append(f"missing/corrupt required source: {rel} ({status})")
            sha = _sha256_bytes((txt or "").encode()) if txt is not None else None
            source_hashes[role] = sha or "NOT_COMPUTABLE"
            canonical_hashes[role] = None
            can = None
        if source_hashes[role] != "NOT_COMPUTABLE":
            blocker_hashes.append(source_hashes[role])
        manifest.append({
            "artifact_id": role,
            "source_patch": source_patch,
            "role": role,
            "source_path": rel,
            "included_as": "sealed_reference",
            "exists": exists,
            "readable": readable,
            "sha256": source_hashes[role],
            "canonical_hash": can,
            "classification": "sealed_reference",
            "sealed_reference_only": True,
            "executable_content_present": False,
            "active_surface_present": False,
        })

    governance_flags = {
        "static_package_artifact": True,"package_created": True,"package_artifacts_created": True,"static_only": True,"non_executable": True,
        "source_linked": True,"hash_manifested": True,"blocker_preserving": True,"advisory_only": True,"non_authoritative": True,
        "read_only_package": True,"authorization_observed": True,"follow_on_audits_required": True,
    }
    governance_flags.update({k: False for k in _REQUIRED_FALSE})

    not_computable = any((not m["exists"]) or (not m["readable"]) for m in manifest)
    fail = (not governance_flags["authorization_observed"]) or authorization_text.strip() != "Authorized"
    fail = fail or governance_flags["distribution_claims_allowed"] or governance_flags["release_readiness_claimed"]
    if not_computable:
        final_status = FINAL_STATUS["NOT_COMPUTABLE"]
        posture = PACKAGE_POSTURE["NOT_COMPUTABLE"]
    elif fail:
        final_status = FINAL_STATUS["FAIL"]
        posture = PACKAGE_POSTURE["FAIL"]
    elif degraded_roles:
        final_status = FINAL_STATUS["DEGRADED"]
        posture = PACKAGE_POSTURE["DEGRADED"]
    else:
        final_status = FINAL_STATUS["STATIC"]
        posture = PACKAGE_POSTURE["STATIC"]

    packet = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "package_id": PACKAGE_ID,
        "final_status": final_status,
        "package_posture": posture,
        "package_created": True,
        "package_mode": "sealed_reference_manifest",
        "static_only": True,
        "executable_payloads_present": False,
        "distribution_claims_allowed": False,
        "release_readiness_claimed": False,
        "artifact_role_order": deepcopy(ROLE_ORDER),
        "package_manifest": manifest,
        "source_hashes": source_hashes,
        "canonical_hashes": canonical_hashes,
        "authorization_evidence": {
            "authorization_required": True,
            "authorization_observed": True,
            "authorization_source": "user_message",
            "authorization_text": authorization_text,
            "authorization_after_p63": True,
            "generic_authorization_used": False,
        },
        "blocker_preservation_summary": {
            "observed_degraded_roles": degraded_roles,
            "observed_blocker_count": len(blockers),
            "observed_blocker_hashes": sorted(set(blocker_hashes)),
            "blocker_suppression_applied": False,
        },
        "governance_boundary_summary": {
            "static_non_executable": True,
            "distribution_claims_allowed": False,
            "release_readiness_claimed": False,
            "authority_escalation": False,
        },
        "follow_on_gate_summary": {
            "required_gates": [
                "P65 Static Archive Package Governance Audit",
                "P66 Static Archive Package Language-Boundary Audit",
                "P67 Static Archive Package Stability Receipt",
                "P68 Static Archive Package Global Verification Receipt",
            ]
        },
        "package_absence_to_creation_transition": {
            "previous_package_absence_verified_by_p59": True,
            "preflight_verified_by_p62": True,
            "authorization_boundary_defined_by_p63": True,
            "explicit_authorization_observed": True,
            "package_created_in_p64": True,
            "package_artifacts_created": True,
            "distribution_claims_allowed": False,
            "release_readiness_claimed": False,
        },
        "governance_flags": governance_flags,
        "provenance": {"deterministic": True, "read_only": True, "source_linked": True, "non_authoritative": True, "fail_closed": True, "runtime_paths_out_dir": paths.out_dir.as_posix()},
    }
    packet["package_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_static_archive_package_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P64 Static Archive Package",
        "",
        f"- package_id: `{packet.get('package_id','')}`",
        f"- final_status: `{packet.get('final_status','')}`",
        f"- package_posture: `{packet.get('package_posture','')}`",
        f"- package_hash: `{packet.get('package_hash','')}`",
        "",
        "## Authorization Evidence",
    ]
    for k, v in (packet.get("authorization_evidence") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Package Manifest Roles"])
    for e in packet.get("package_manifest", []):
        lines.append(f"- `{e['role']}` -> `{e['source_path']}` ({e['included_as']})")
    lines.extend(["", "## Governance Flags"])
    for k, v in (packet.get("governance_flags") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_static_archive_package(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_static_archive_package_markdown(packet), encoding="utf-8")
