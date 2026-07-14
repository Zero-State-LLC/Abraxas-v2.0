from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.operator_narrative_static_archive_package import (
    ROLE_ORDER,
    build_operator_narrative_static_archive_package_packet,
)
from core.operator_narrative_static_archive_package_governance_audit import (
    build_operator_narrative_static_archive_package_governance_audit_packet,
)
from core.operator_narrative_static_archive_package_language_boundary_audit import (
    build_operator_narrative_static_archive_package_language_boundary_audit_packet,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "OperatorNarrativeStaticArchivePackageStabilityReceipt.v1"
PATCH_ID = "PATCH-P67-OPERATOR-NARRATIVE-STATIC-ARCHIVE-PACKAGE-STABILITY-RECEIPT-001"
RECEIPT_ID = "operator_narrative_static_archive_package_stability_receipt_001"


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


def build_operator_narrative_static_archive_package_stability_receipt_packet(
    *,
    p64_json_path: str | Path = "out/package/operator_narrative_static_archive_package_001.latest.json",
    p64_md_path: str | Path = "out/package/operator_narrative_static_archive_package_001.latest.md",
    p65_json_path: str | Path = "out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json",
    p65_md_path: str | Path = "out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.md",
    p66_json_path: str | Path = "out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.json",
    p66_md_path: str | Path = "out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.md",
    repo_root: str | Path = ".",
    replay_count: int = 3,
    replay_runs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    p64j, p64m, p65j, p65m, p66j, p66m = root / Path(p64_json_path), root / Path(p64_md_path), root / Path(p65_json_path), root / Path(p65_md_path), root / Path(p66_json_path), root / Path(p66_md_path)
    p64, p64s, p64raw = _read_json(p64j)
    p65, p65s, p65raw = _read_json(p65j)
    p66, p66s, p66raw = _read_json(p66j)
    blockers: list[str] = []

    for status, j, m, label in [(p64s, p64j, p64m, "p64"), (p65s, p65j, p65m, "p65"), (p66s, p66j, p66m, "p66")]:
        if status != "PRESENT" or not m.exists():
            blockers.append(f"{label} surface missing/corrupt")

    runs = replay_runs if replay_runs is not None else [
        {
            "p64": build_operator_narrative_static_archive_package_packet(repo_root=root),
            "p65": build_operator_narrative_static_archive_package_governance_audit_packet(repo_root=root),
            "p66": build_operator_narrative_static_archive_package_language_boundary_audit_packet(repo_root=root),
        }
        for _ in range(replay_count)
    ]

    replay_results: list[dict[str, Any]] = []
    if p64 and p65 and p66:
        b_pkg_hash = runs[0]["p64"].get("package_hash", "") if runs else ""
        b_a65_hash = runs[0]["p65"].get("audit_hash", "") if runs else ""
        b_a66_hash = runs[0]["p66"].get("audit_hash", "") if runs else ""
        for i, run in enumerate(runs, start=1):
            rp64, rp65, rp66 = run["p64"], run["p65"], run["p66"]
            replay_results.append({
                "replay_index": i,
                "package_hash": rp64.get("package_hash", ""),
                "p65_audit_hash": rp65.get("audit_hash", ""),
                "p66_audit_hash": rp66.get("audit_hash", ""),
                "role_order": rp64.get("artifact_role_order", []),
                "manifest_roles": [x.get("role") for x in rp64.get("package_manifest", [])] if isinstance(rp64.get("package_manifest"), list) else [],
            })
            if rp64.get("package_hash") != b_pkg_hash:
                blockers.append(f"replay {i} package_hash mismatch")
            if rp65.get("audit_hash") != b_a65_hash:
                blockers.append(f"replay {i} p65 audit_hash mismatch")
            if rp66.get("audit_hash") != b_a66_hash:
                blockers.append(f"replay {i} p66 audit_hash mismatch")
            if rp64.get("artifact_role_order") != ROLE_ORDER:
                blockers.append(f"replay {i} role order mismatch")
            if [x.get("role") for x in rp64.get("package_manifest", [])] != ROLE_ORDER:
                blockers.append(f"replay {i} manifest role order mismatch")
            if rp65.get("final_status") != "PACKAGE_GOVERNANCE_AUDIT_PASS" or rp65.get("audit_posture") != "PACKAGE_GOVERNANCE_CLEAN":
                blockers.append(f"replay {i} p65 pass/clean violated")
            if rp66.get("final_status") != "PACKAGE_LANGUAGE_BOUNDARY_PASS" or rp66.get("audit_posture") != "LANGUAGE_BOUNDARY_CLEAN":
                blockers.append(f"replay {i} p66 pass/clean violated")

        if p64.get("final_status") not in {"PACKAGE_CREATED_STATIC", "PACKAGE_CREATED_DEGRADED"}:
            blockers.append("p64 final_status invalid")
        if p64.get("package_created") is not True or p64.get("static_only") is not True:
            blockers.append("p64 package/static flags invalid")
        for k in ["executable_payloads_present", "distribution_claims_allowed", "release_readiness_claimed"]:
            if p64.get(k) is not False:
                blockers.append(f"p64 {k} must be false")
        if p64.get("artifact_role_order") != ROLE_ORDER:
            blockers.append("p64 role order mismatch")
        manifest = p64.get("package_manifest", []) if isinstance(p64.get("package_manifest"), list) else []
        if [x.get("role") for x in manifest] != ROLE_ORDER:
            blockers.append("p64 manifest role mismatch")
        for e in manifest:
            if e.get("sealed_reference_only") is not True or e.get("executable_content_present") is not False or e.get("active_surface_present") is not False:
                blockers.append("p64 manifest entry boundary violation")
                break

        gates = ((p64.get("follow_on_gate_summary") or {}).get("required_gates") or [])
        for g in ["P65 Static Archive Package Governance Audit", "P66 Static Archive Package Language-Boundary Audit", "P67 Static Archive Package Stability Receipt", "P68 Static Archive Package Global Verification Receipt"]:
            if g not in gates:
                blockers.append(f"missing follow-on gate: {g}")

        if p65.get("final_status") != "PACKAGE_GOVERNANCE_AUDIT_PASS" or p65.get("audit_posture") != "PACKAGE_GOVERNANCE_CLEAN":
            blockers.append("p65 pass/clean violated")
        if not p65.get("audit_hash"):
            blockers.append("p65 audit_hash missing")
        if p66.get("final_status") != "PACKAGE_LANGUAGE_BOUNDARY_PASS" or p66.get("audit_posture") != "LANGUAGE_BOUNDARY_CLEAN":
            blockers.append("p66 pass/clean violated")
        if not p66.get("audit_hash"):
            blockers.append("p66 audit_hash missing")

    degraded = bool(((p64 or {}).get("blocker_preservation_summary") or {}).get("observed_degraded_roles")) or int(((p64 or {}).get("blocker_preservation_summary") or {}).get("observed_blocker_count", 0) or 0) > 0

    if p64s != "PRESENT" or p65s != "PRESENT" or p66s != "PRESENT" or not p64m.exists() or not p65m.exists() or not p66m.exists():
        final_status, posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif blockers:
        final_status, posture = "PACKAGE_STABILITY_RECEIPT_FAIL", "PACKAGE_STABILITY_FAILED"
    elif degraded and (p64 or {}).get("final_status") == "PACKAGE_CREATED_DEGRADED":
        final_status, posture = "PACKAGE_STABILITY_RECEIPT_DEGRADED", "PACKAGE_STABLE_WITH_OBSERVED_BLOCKERS"
    else:
        final_status, posture = "PACKAGE_STABILITY_RECEIPT_PASS", "PACKAGE_STABLE"

    gflags = {
        "stability_receipt_only": True, "package_stability_receipt_only": True, "advisory_only": True, "read_only": True, "non_authoritative": True, "source_linked": True, "deterministic_receipt": True,
        "replay_stability_checked": True, "package_manifest_stability_checked": True, "governance_audit_checked": True, "language_boundary_audit_checked": True,
        "package_created": False, "package_artifacts_created": False, "package_mutation_allowed": False, "distribution_claims_allowed": False, "release_readiness_claimed": False,
        "command_authority": False, "ui_command_authority": False, "action_authority": False, "recommendation_authority": False, "inference_authority": False, "prediction_allowed": False, "forecast_authority": False, "trend_prediction_allowed": False, "readiness_claims_allowed": False, "mutation_allowed": False, "authority_granted": False, "execution_authority": False, "routing_change_allowed": False, "queue_mutation_allowed": False, "canon_mutation_allowed": False, "runtime_mutation_allowed": False, "adaptive_behavior_allowed": False, "psychological_claims_allowed": False, "speculative_causation_allowed": False, "auto_execute": False, "auto_approve": False, "command_channel": False, "bidirectional_control": False, "script_allowed": False, "html_script_allowed": False, "external_fetch_allowed": False, "form_allowed": False, "button_allowed": False, "executable_payloads_present": False, "active_surfaces_present": False,
    }

    packet = {
        "schema_version": SCHEMA_VERSION, "patch_id": PATCH_ID, "receipt_id": RECEIPT_ID,
        "final_status": final_status, "stability_posture": posture, "replay_count": replay_count,
        "checked_artifacts": {"p64_json": p64j.as_posix(), "p64_md": p64m.as_posix(), "p65_json": p65j.as_posix(), "p65_md": p65m.as_posix(), "p66_json": p66j.as_posix(), "p66_md": p66m.as_posix()},
        "replay_results": replay_results,
        "hash_stability_summary": {"package_hash_stable": all(r.get("package_hash") == (p64 or {}).get("package_hash") for r in replay_results), "p65_audit_hash_stable": all(r.get("p65_audit_hash") == (p65 or {}).get("audit_hash") for r in replay_results), "p66_audit_hash_stable": all(r.get("p66_audit_hash") == (p66 or {}).get("audit_hash") for r in replay_results)},
        "package_manifest_stability_summary": {"role_order_expected": deepcopy(ROLE_ORDER), "role_order_observed": (p64 or {}).get("artifact_role_order", []), "manifest_role_order_observed": [x.get("role") for x in ((p64 or {}).get("package_manifest") or [])] if isinstance((p64 or {}).get("package_manifest"), list) else []},
        "governance_audit_summary": {"final_status": (p65 or {}).get("final_status", NOT_COMPUTABLE), "audit_posture": (p65 or {}).get("audit_posture", NOT_COMPUTABLE), "audit_hash": (p65 or {}).get("audit_hash", "")},
        "language_boundary_audit_summary": {"final_status": (p66 or {}).get("final_status", NOT_COMPUTABLE), "audit_posture": (p66 or {}).get("audit_posture", NOT_COMPUTABLE), "audit_hash": (p66 or {}).get("audit_hash", "")},
        "blocker_preservation_summary": deepcopy(((p64 or {}).get("blocker_preservation_summary") or {})),
        "governance_boundary_summary": {"distribution_claims_allowed": (p64 or {}).get("distribution_claims_allowed", NOT_COMPUTABLE), "release_readiness_claimed": (p64 or {}).get("release_readiness_claimed", NOT_COMPUTABLE), "executable_payloads_present": (p64 or {}).get("executable_payloads_present", NOT_COMPUTABLE), "package_created": (p64 or {}).get("package_created", NOT_COMPUTABLE)},
        "source_hashes": {"p64_json": hashlib.sha256(p64raw.encode()).hexdigest() if p64raw else NOT_COMPUTABLE, "p65_json": hashlib.sha256(p65raw.encode()).hexdigest() if p65raw else NOT_COMPUTABLE, "p66_json": hashlib.sha256(p66raw.encode()).hexdigest() if p66raw else NOT_COMPUTABLE},
        "blocker_summary": sorted(set(blockers)), "governance_flags": gflags,
        "provenance": {"deterministic": True, "read_only": True, "source_linked": True, "non_authoritative": True, "fail_closed": True, "replay_method": "in_process_packet_builders"},
    }
    packet["stability_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_static_archive_package_stability_receipt_markdown(packet: dict[str, Any]) -> str:
    lines = ["# P67 Static Archive Package Stability Receipt", "", f"- receipt_id: `{packet.get('receipt_id','')}`", f"- final_status: `{packet.get('final_status','')}`", f"- stability_posture: `{packet.get('stability_posture','')}`", f"- stability_hash: `{packet.get('stability_hash','')}`", "", "## Replay Results"]
    for row in packet.get("replay_results", []):
        lines.append(f"- replay `{row.get('replay_index')}`: package=`{row.get('package_hash')}` p65=`{row.get('p65_audit_hash')}` p66=`{row.get('p66_audit_hash')}`")
    if not packet.get("replay_results"):
        lines.append("- none")
    lines.extend(["", "## Blockers"])
    lines.extend([f"- `{x}`" for x in packet.get("blocker_summary", [])] or ["- none"])
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_static_archive_package_stability_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_static_archive_package_stability_receipt_markdown(packet), encoding="utf-8")
