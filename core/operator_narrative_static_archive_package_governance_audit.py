from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_static_archive_package import ROLE_ORDER

SCHEMA_VERSION = "OperatorNarrativeStaticArchivePackageGovernanceAudit.v1"
PATCH_ID = "PATCH-P65-OPERATOR-NARRATIVE-STATIC-ARCHIVE-PACKAGE-GOVERNANCE-AUDIT-001"
AUDIT_ID = "operator_narrative_static_archive_package_governance_audit_001"


def _finding_id(category: str, message: str, refs: list[str]) -> str:
    basis = f"{category}|{' '.join(message.split()).strip().lower()}|{'|'.join(sorted(refs))}"
    return hashlib.sha256(basis.encode()).hexdigest()


def _sev_rank(sev: str) -> int:
    return {"FAIL": 0, "WARN": 1, "PASS": 2}.get(sev, 9)


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str, str]:
    try:
        txt = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, "MISSING", ""
    except OSError:
        return None, "CORRUPT", ""
    try:
        data = json.loads(txt)
    except json.JSONDecodeError:
        return None, "CORRUPT", txt
    return (data if isinstance(data, dict) else None), ("PRESENT" if isinstance(data, dict) else "CORRUPT"), txt


def build_operator_narrative_static_archive_package_governance_audit_packet(*, package_json_path: str | Path = "out/package/operator_narrative_static_archive_package_001.latest.json", package_md_path: str | Path = "out/package/operator_narrative_static_archive_package_001.latest.md", repo_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_root)
    p_json = root / Path(package_json_path)
    p_md = root / Path(package_md_path)
    findings: list[dict[str, Any]] = []
    blockers: list[str] = []

    pkg, pkg_status, pkg_txt = _read_json(p_json)
    md_exists = p_md.exists()
    md_readable = False
    md_txt = ""
    try:
        md_txt = p_md.read_text(encoding="utf-8")
        md_readable = True
    except OSError:
        md_readable = False

    def add(sev: str, cat: str, msg: str, refs: list[str]) -> None:
        findings.append({"finding_id": _finding_id(cat, msg, refs), "severity": sev, "category": cat, "message": msg, "evidence_refs": sorted(refs)})
        if sev == "FAIL":
            blockers.append(msg)

    if pkg_status != "PRESENT":
        add("FAIL", "PACKAGE_SURFACE", "package json missing or corrupt", [p_json.as_posix()])
    if not md_exists or not md_readable:
        add("FAIL", "PACKAGE_SURFACE", "package markdown missing or unreadable", [p_md.as_posix()])

    recomputed = "NOT_COMPUTABLE"
    if pkg:
        p = deepcopy(pkg)
        observed_hash = p.pop("package_hash", None)
        recomputed = canonical_hash(p)
        if observed_hash != recomputed:
            add("FAIL", "PACKAGE_HASH", "package_hash mismatch", [p_json.as_posix()])

        if pkg.get("artifact_role_order") != ROLE_ORDER:
            add("FAIL", "ROLE_ORDER", "artifact_role_order mismatch", [p_json.as_posix()])

        pm = pkg.get("package_manifest") if isinstance(pkg.get("package_manifest"), list) else []
        if [x.get("role") for x in pm] != ROLE_ORDER:
            add("FAIL", "MANIFEST_ORDER", "package_manifest role order mismatch", [p_json.as_posix()])
        for i, e in enumerate(pm):
            role = e.get("role", f"idx:{i}")
            src = root / str(e.get("source_path", ""))
            if not e.get("sealed_reference_only"):
                add("FAIL", "MANIFEST_ENTRY", f"{role} not sealed_reference_only", [str(e.get("source_path", ""))])
            if e.get("executable_content_present"):
                add("FAIL", "MANIFEST_ENTRY", f"{role} executable_content_present true", [str(e.get("source_path", ""))])
            if e.get("active_surface_present"):
                add("FAIL", "MANIFEST_ENTRY", f"{role} active_surface_present true", [str(e.get("source_path", ""))])
            if not src.exists():
                add("FAIL", "MANIFEST_ENTRY", f"{role} source missing", [str(e.get("source_path", ""))])
            else:
                b = src.read_bytes()
                sha = hashlib.sha256(b).hexdigest()
                if e.get("sha256") != sha:
                    add("FAIL", "MANIFEST_ENTRY", f"{role} sha256 mismatch", [str(e.get("source_path", ""))])
                if str(e.get("source_path", "")).endswith(".json"):
                    try:
                        src_obj = json.loads(b.decode())
                        can = canonical_hash(src_obj)
                        if e.get("canonical_hash") != can:
                            add("FAIL", "MANIFEST_ENTRY", f"{role} canonical_hash mismatch", [str(e.get("source_path", ""))])
                    except Exception:
                        add("FAIL", "MANIFEST_ENTRY", f"{role} canonical json unreadable", [str(e.get("source_path", ""))])

        # scalar checks
        for field, expect in [("static_only", True), ("executable_payloads_present", False), ("distribution_claims_allowed", False), ("release_readiness_claimed", False), ("package_created", True)]:
            if pkg.get(field) != expect:
                add("FAIL", "PACKAGE_FLAGS", f"{field} must be {expect}", [p_json.as_posix()])

        g = pkg.get("governance_flags", {}) if isinstance(pkg.get("governance_flags"), dict) else {}
        if g.get("package_artifacts_created") is not True:
            add("FAIL", "PACKAGE_FLAGS", "package_artifacts_created must be true", [p_json.as_posix()])

        auth = pkg.get("authorization_evidence", {}) if isinstance(pkg.get("authorization_evidence"), dict) else {}
        for k, v in [("authorization_required", True), ("authorization_observed", True), ("authorization_source", "user_message"), ("authorization_text", "Authorized"), ("authorization_after_p63", True), ("generic_authorization_used", False)]:
            if auth.get(k) != v:
                add("FAIL", "AUTHORIZATION", f"authorization evidence mismatch: {k}", [p_json.as_posix()])

        bps = pkg.get("blocker_preservation_summary", {}) if isinstance(pkg.get("blocker_preservation_summary"), dict) else {}
        degraded = bool(bps.get("observed_degraded_roles")) or int(bps.get("observed_blocker_count", 0)) > 0
        if degraded and pkg.get("final_status") != "PACKAGE_CREATED_DEGRADED":
            add("FAIL", "BLOCKER_PRESERVATION", "degraded evidence present but final_status not PACKAGE_CREATED_DEGRADED", [p_json.as_posix()])
        if bps.get("blocker_suppression_applied") is not False:
            add("FAIL", "BLOCKER_PRESERVATION", "blocker suppression must be false", [p_json.as_posix()])

        gates = ((pkg.get("follow_on_gate_summary") or {}).get("required_gates") or [])
        for gname in ["P65 Static Archive Package Governance Audit", "P66 Static Archive Package Language-Boundary Audit", "P67 Static Archive Package Stability Receipt", "P68 Static Archive Package Global Verification Receipt"]:
            if gname not in gates:
                add("FAIL", "FOLLOW_ON_GATES", f"missing follow-on gate: {gname}", [p_json.as_posix()])

    reg = build_generated_artifact_registry(root)
    emap = {e.artifact_path: e for e in reg.entries}
    reg_json = emap.get("out/package/operator_narrative_static_archive_package_001.latest.json")
    reg_md = emap.get("out/package/operator_narrative_static_archive_package_001.latest.md")
    if not reg_json or not reg_md:
        add("FAIL", "REGISTRY", "p64 package artifacts missing from registry", ["core/generated_artifact_registry.py"])
    elif reg_json.determinism_class != "DERIVED_OPTIONAL" or reg_md.determinism_class != "DERIVED_OPTIONAL":
        add("FAIL", "REGISTRY", "p64 package artifacts wrong determinism class", ["core/generated_artifact_registry.py"])

    findings.sort(key=lambda x: (_sev_rank(x["severity"]), x["category"], x["finding_id"]))
    counts = {"PASS": sum(1 for f in findings if f["severity"] == "PASS"), "WARN": sum(1 for f in findings if f["severity"] == "WARN"), "FAIL": sum(1 for f in findings if f["severity"] == "FAIL")}

    not_computable = pkg_status != "PRESENT"
    if not_computable:
        final_status = "NOT_COMPUTABLE"
        posture = "NOT_COMPUTABLE"
    elif counts["FAIL"]:
        final_status = "PACKAGE_GOVERNANCE_AUDIT_FAIL"
        posture = "PACKAGE_GOVERNANCE_FAILED"
    else:
        final_status = "PACKAGE_GOVERNANCE_AUDIT_PASS"
        posture = "PACKAGE_GOVERNANCE_CLEAN"

    gflags = {
        "audit_only": True, "package_governance_audit_only": True, "advisory_only": True, "read_only": True, "non_authoritative": True, "source_linked": True, "deterministic_audit": True,
        "package_created": False, "package_artifacts_created": False, "distribution_claims_allowed": False, "release_readiness_claimed": False,
        "command_authority": False, "ui_command_authority": False, "action_authority": False, "recommendation_authority": False, "inference_authority": False, "prediction_allowed": False, "forecast_authority": False, "trend_prediction_allowed": False, "readiness_claims_allowed": False, "mutation_allowed": False, "authority_granted": False, "execution_authority": False, "routing_change_allowed": False, "queue_mutation_allowed": False, "canon_mutation_allowed": False, "runtime_mutation_allowed": False, "adaptive_behavior_allowed": False, "psychological_claims_allowed": False, "speculative_causation_allowed": False, "auto_execute": False, "auto_approve": False, "command_channel": False, "bidirectional_control": False, "script_allowed": False, "html_script_allowed": False, "external_fetch_allowed": False, "form_allowed": False, "button_allowed": False,
    }

    packet = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "audit_id": AUDIT_ID,
        "final_status": final_status,
        "audit_posture": posture,
        "checked_artifacts": {"package_json_path": p_json.as_posix(), "package_md_path": p_md.as_posix(), "registry_path": "core/generated_artifact_registry.py"},
        "findings": findings,
        "finding_counts": counts,
        "package_identity_summary": {"package_id": (pkg or {}).get("package_id", "NOT_COMPUTABLE"), "schema_version": (pkg or {}).get("schema_version", "NOT_COMPUTABLE")},
        "package_hash_summary": {"observed_package_hash": (pkg or {}).get("package_hash", "NOT_COMPUTABLE"), "recomputed_package_hash": recomputed, "hash_match": (pkg or {}).get("package_hash") == recomputed if pkg else False},
        "manifest_summary": {"expected_role_order": deepcopy(ROLE_ORDER), "manifest_entry_count": len((pkg or {}).get("package_manifest", []) if pkg else [])},
        "authorization_summary": deepcopy(((pkg or {}).get("authorization_evidence") or {}),),
        "blocker_preservation_summary": deepcopy(((pkg or {}).get("blocker_preservation_summary") or {}),),
        "governance_flag_summary": {"p64_governance_flags": deepcopy(((pkg or {}).get("governance_flags") or {}),)},
        "follow_on_gate_summary": deepcopy(((pkg or {}).get("follow_on_gate_summary") or {}),),
        "registry_classification_summary": {
            "p64_json_present": reg_json is not None,
            "p64_md_present": reg_md is not None,
            "p64_json_class": reg_json.determinism_class if reg_json else "NOT_COMPUTABLE",
            "p64_md_class": reg_md.determinism_class if reg_md else "NOT_COMPUTABLE",
        },
        "source_hashes": {
            "package_json": hashlib.sha256(pkg_txt.encode()).hexdigest() if pkg_txt else "NOT_COMPUTABLE",
            "package_md": hashlib.sha256(md_txt.encode()).hexdigest() if md_txt else "NOT_COMPUTABLE",
        },
        "blocker_summary": sorted(set(blockers)),
        "governance_flags": gflags,
        "provenance": {"deterministic": True, "read_only": True, "source_linked": True, "non_authoritative": True, "fail_closed": True},
    }
    packet["audit_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_static_archive_package_governance_audit_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P65 Static Archive Package Governance Audit",
        "",
        f"- audit_id: `{packet.get('audit_id','')}`",
        f"- final_status: `{packet.get('final_status','')}`",
        f"- audit_posture: `{packet.get('audit_posture','')}`",
        f"- audit_hash: `{packet.get('audit_hash','')}`",
        "",
        "## Findings",
    ]
    for f in packet.get("findings", []):
        lines.append(f"- [{f['severity']}] {f['category']}: {f['message']}")
    if not packet.get("findings"):
        lines.append("- none")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_static_archive_package_governance_audit(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_static_archive_package_governance_audit_markdown(packet), encoding="utf-8")
