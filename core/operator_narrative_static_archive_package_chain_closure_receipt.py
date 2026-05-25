from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.operator_narrative_static_archive_package import ROLE_ORDER

ARTIFACT_TYPE = "static_archive_package_chain_closure_receipt"
SCHEMA_VERSION = "OperatorNarrativeStaticArchivePackageChainClosureReceipt.v1"
PATCH_ID = "PATCH-P68-OPERATOR-NARRATIVE-STATIC-ARCHIVE-PACKAGE-CHAIN-CLOSURE-RECEIPT-001"
RECEIPT_ID = "operator_narrative_static_archive_package_chain_closure_receipt_001"
DETERMINISTIC_GENERATED_AT = "1970-01-01T00:00:00Z"


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


def build_operator_narrative_static_archive_package_chain_closure_receipt_packet(*,
    p64_json_path: str | Path = "out/package/operator_narrative_static_archive_package_001.latest.json",
    p65_json_path: str | Path = "out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json",
    p66_json_path: str | Path = "out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.json",
    p67_json_path: str | Path = "out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.json",
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    p64p, p65p, p66p, p67p = root / Path(p64_json_path), root / Path(p65_json_path), root / Path(p66_json_path), root / Path(p67_json_path)
    p64, s64, r64 = _read_json(p64p)
    p65, s65, r65 = _read_json(p65p)
    p66, s66, r66 = _read_json(p66p)
    p67, s67, r67 = _read_json(p67p)
    blockers: list[str] = []

    for lbl, st, obj in [("p64", s64, p64), ("p65", s65, p65), ("p66", s66, p66), ("p67", s67, p67)]:
        if st != "PRESENT" or obj is None:
            blockers.append(f"{lbl} missing/corrupt")

    if p64 and not p64.get("package_hash"):
        blockers.append("p64 package_hash missing")
    if p65 and not p65.get("audit_hash"):
        blockers.append("p65 audit_hash missing")
    if p66 and not p66.get("audit_hash"):
        blockers.append("p66 audit_hash missing")
    if p67 and not p67.get("stability_hash"):
        blockers.append("p67 stability_hash missing")

    if p65 and (p65.get("final_status") != "PACKAGE_GOVERNANCE_AUDIT_PASS" or p65.get("audit_posture") != "PACKAGE_GOVERNANCE_CLEAN"):
        blockers.append("p65 status/posture invalid")
    if p66 and (p66.get("final_status") != "PACKAGE_LANGUAGE_BOUNDARY_PASS" or p66.get("audit_posture") != "LANGUAGE_BOUNDARY_CLEAN"):
        blockers.append("p66 status/posture invalid")
    if p67 and p67.get("final_status") not in {"PACKAGE_STABILITY_RECEIPT_PASS", "PACKAGE_STABILITY_RECEIPT_DEGRADED"}:
        blockers.append("p67 final_status invalid")
    if p67 and p67.get("stability_posture") not in {"PACKAGE_STABLE", "PACKAGE_STABLE_WITH_OBSERVED_BLOCKERS"}:
        blockers.append("p67 stability_posture invalid")

    if p64:
        if p64.get("artifact_role_order") != ROLE_ORDER:
            blockers.append("p64 artifact_role_order drift")
        manifest = p64.get("package_manifest", []) if isinstance(p64.get("package_manifest"), list) else []
        if [m.get("role") for m in manifest] != ROLE_ORDER:
            blockers.append("p64 manifest role order drift")
        for k in ["distribution_claims_allowed", "release_readiness_claimed", "executable_payloads_present"]:
            if p64.get(k) is not False:
                blockers.append(f"p64 forbidden flag true: {k}")
        for entry in manifest:
            if entry.get("sealed_reference_only") is not True:
                blockers.append("p64 manifest not sealed_reference_only")
                break

    if p64 and p67:
        p64_b = p64.get("blocker_preservation_summary", {}) if isinstance(p64.get("blocker_preservation_summary"), dict) else {}
        p67_b = p67.get("blocker_preservation_summary", {}) if isinstance(p67.get("blocker_preservation_summary"), dict) else {}
        if p64_b != p67_b:
            blockers.append("blocker preservation mismatch p64 vs p67")

    degraded = False
    if p64:
        bps = p64.get("blocker_preservation_summary", {}) if isinstance(p64.get("blocker_preservation_summary"), dict) else {}
        degraded = bool(bps.get("observed_degraded_roles")) or int(bps.get("observed_blocker_count", 0) or 0) > 0

    if any(s != "PRESENT" for s in [s64, s65, s66, s67]):
        final_status = "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_NOT_COMPUTABLE"
        posture = "STATIC_ARCHIVE_PACKAGE_CHAIN_NOT_COMPUTABLE"
    elif blockers:
        final_status = "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_FAIL"
        posture = "STATIC_ARCHIVE_PACKAGE_CHAIN_NOT_CLOSED"
    elif degraded and p67 and p67.get("final_status") == "PACKAGE_STABILITY_RECEIPT_DEGRADED":
        final_status = "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_DEGRADED"
        posture = "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSED_WITH_OBSERVED_BLOCKERS"
    else:
        final_status = "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_PASS"
        posture = "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSED"

    governance_flags = {
        "receipt_only": True, "read_only": True, "non_authoritative": True, "deterministic": True, "advisory_only": True,
        "package_creation": False, "package_mutation": False, "distribution": False, "release_readiness": False,
        "command_authority": False, "action_authority": False, "execution_authority": False, "runtime_mutation": False,
        "forecast_influence": False, "canon_promotion": False,
    }

    packet = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "receipt_id": RECEIPT_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "final_status": final_status,
        "closure_posture": posture,
        "upstream_packet_references": {"p64": p64p.as_posix(), "p65": p65p.as_posix(), "p66": p66p.as_posix(), "p67": p67p.as_posix()},
        "boundary_flags": {"distribution": False, "release_readiness": False, "command_authority": False, "action_authority": False, "execution_authority": False},
        "chain_structure_summary": {"artifact_role_order": (p64 or {}).get("artifact_role_order", []), "manifest_role_order": [m.get("role") for m in ((p64 or {}).get("package_manifest") or [])] if isinstance((p64 or {}).get("package_manifest"), list) else []},
        "upstream_status_summary": {"p64_final_status": (p64 or {}).get("final_status", "NOT_COMPUTABLE"), "p65_final_status": (p65 or {}).get("final_status", "NOT_COMPUTABLE"), "p66_final_status": (p66 or {}).get("final_status", "NOT_COMPUTABLE"), "p67_final_status": (p67 or {}).get("final_status", "NOT_COMPUTABLE")},
        "blocker_preservation_summary": deepcopy((p64 or {}).get("blocker_preservation_summary", {})),
        "source_hashes": {"p64_json": hashlib.sha256(r64.encode()).hexdigest() if r64 else "NOT_COMPUTABLE", "p65_json": hashlib.sha256(r65.encode()).hexdigest() if r65 else "NOT_COMPUTABLE", "p66_json": hashlib.sha256(r66.encode()).hexdigest() if r66 else "NOT_COMPUTABLE", "p67_json": hashlib.sha256(r67.encode()).hexdigest() if r67 else "NOT_COMPUTABLE"},
        "governance_flags": governance_flags,
        "broken_surface_ledger": sorted(set(blockers)),
        "blocker_summary": sorted(set(blockers)),
        "provenance": {"deterministic": True, "read_only": True, "non_authoritative": True, "source_linked": True, "fail_closed": True},
    }
    packet["closure_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_static_archive_package_chain_closure_receipt_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P68 Static Archive Package Chain Closure Receipt", "",
        f"- final_status: `{packet.get('final_status','')}`",
        f"- closure_posture: `{packet.get('closure_posture','')}`",
        f"- closure_hash: `{packet.get('closure_hash','')}`", "",
        "## Upstream Surfaces",
    ]
    for k, v in (packet.get("upstream_packet_references") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Blocker Preservation", f"- `{packet.get('blocker_preservation_summary',{})}`", "", "## Governance Denial Flags"])
    for k, v in (packet.get("governance_flags") or {}).items():
        if isinstance(v, bool) and v is False:
            lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Broken Surface Ledger"])
    ledger = packet.get("broken_surface_ledger", [])
    lines.extend([f"- `{x}`" for x in ledger] if ledger else ["- none"])
    lines.extend(["", "## Chain Closure Decision", f"- `{packet.get('closure_posture','')}`"])
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_static_archive_package_chain_closure_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix('.md').write_text(build_operator_narrative_static_archive_package_chain_closure_receipt_markdown(packet), encoding='utf-8')
