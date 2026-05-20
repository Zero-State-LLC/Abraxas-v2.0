from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "static_archive_package_completion_seal_receipt"
SCHEMA_VERSION = "OperatorNarrativeStaticArchivePackageCompletionSealReceipt.v1"
PATCH_ID = "PATCH-P72-OPERATOR-NARRATIVE-STATIC-ARCHIVE-PACKAGE-COMPLETION-SEAL-RECEIPT-001"
RECEIPT_ID = "operator_narrative_static_archive_package_completion_seal_receipt_001"
EXPECTED_ORDER = ["P64", "P65", "P66", "P67", "P68", "P69", "P70"]


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, "MISSING", ""
    except OSError:
        return None, "CORRUPT", ""
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None, "CORRUPT", text
    return (obj if isinstance(obj, dict) else None), ("PRESENT" if isinstance(obj, dict) else "CORRUPT"), text


def build_operator_narrative_static_archive_package_completion_seal_receipt_packet(*, repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[1]
    p71_path = root / "docs/plans/P71_planning_gate_static_archive_package_completion_seal.md"
    refs = {
        "P64": root / "out/package/operator_narrative_static_archive_package_001.latest.json",
        "P65": root / "out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json",
        "P66": root / "out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.json",
        "P67": root / "out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.json",
        "P68": root / "out/audit/operator_narrative_static_archive_package_chain_closure_receipt_001.latest.json",
        "P69": root / "out/audit/operator_narrative_static_archive_package_index_pointer_receipt_001.latest.json",
        "P70": root / "out/audit/operator_narrative_static_archive_package_final_index_receipt_001.latest.json",
    }
    loaded: dict[str, dict[str, Any] | None] = {}
    raw: dict[str, str] = {}
    state: dict[str, str] = {}
    blockers: list[str] = []

    for sid, path in refs.items():
        obj, st, txt = _read_json(path)
        loaded[sid], state[sid], raw[sid] = obj, st, txt

    p71_exists = p71_path.exists()
    p71_text = p71_path.read_text(encoding="utf-8") if p71_exists else ""
    p71_labels = ["P71_PLAN_READY", "P71_COMPLETION_SEAL_PLANNING_REQUIRED"]
    missing_p71_labels = [x for x in p71_labels if x not in p71_text]

    if not p71_exists:
        blockers.append("P71 planning doc missing")
    if missing_p71_labels:
        blockers.append("P71 required labels missing")
    if any(state[s] != "PRESENT" or loaded[s] is None for s in EXPECTED_ORDER):
        blockers.extend([f"{s} missing/corrupt" for s in EXPECTED_ORDER if state[s] != "PRESENT" or loaded[s] is None])

    p64, p65, p66, p67, p68, p69, p70 = [(loaded.get(s) or {}) for s in EXPECTED_ORDER]

    if p64.get("final_status") not in {"PACKAGE_CREATED_STATIC", "PACKAGE_CREATED_DEGRADED"}:
        blockers.append("P64 final_status invalid")
    if p65.get("final_status") != "PACKAGE_GOVERNANCE_AUDIT_PASS" or p65.get("audit_posture") != "PACKAGE_GOVERNANCE_CLEAN":
        blockers.append("P65 status/posture invalid")
    if p66.get("final_status") != "PACKAGE_LANGUAGE_BOUNDARY_PASS" or p66.get("audit_posture") != "LANGUAGE_BOUNDARY_CLEAN":
        blockers.append("P66 status/posture invalid")
    if p67.get("final_status") not in {"PACKAGE_STABILITY_RECEIPT_PASS", "PACKAGE_STABILITY_RECEIPT_DEGRADED"}:
        blockers.append("P67 final_status invalid")
    if p68.get("final_status") not in {"STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_PASS", "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_DEGRADED"}:
        blockers.append("P68 final_status invalid")
    if p69.get("pointer_count") != 5 or p69.get("ordered_surface_ids") != ["P64", "P65", "P66", "P67", "P68"]:
        blockers.append("P69 pointer summary invalid")
    if p70.get("pointer_count") != 6 or p70.get("ordered_surface_ids") != ["P64", "P65", "P66", "P67", "P68", "P69"]:
        blockers.append("P70 pointer summary invalid")
    if p70.get("final_status") not in {"STATIC_ARCHIVE_PACKAGE_FINAL_INDEX_PASS", "STATIC_ARCHIVE_PACKAGE_FINAL_INDEX_DEGRADED"}:
        blockers.append("P70 final_status invalid")

    for key in ["distribution_claims_allowed", "release_readiness_claimed"]:
        if p64.get(key) is not False:
            blockers.append(f"P64 forbidden flag true: {key}")

    degraded = any("DEGRADED" in str((loaded.get(s) or {}).get("final_status", "")) for s in EXPECTED_ORDER)

    if not p71_exists or any(state[s] != "PRESENT" or loaded[s] is None for s in EXPECTED_ORDER):
        final_status = "NOT_COMPUTABLE"
        posture = "NOT_COMPUTABLE"
    elif blockers:
        final_status = "STATIC_ARCHIVE_PACKAGE_COMPLETION_SEAL_FAIL"
        posture = "STATIC_ARCHIVE_PACKAGE_COMPLETION_SEAL_FAILED"
    elif degraded:
        final_status = "STATIC_ARCHIVE_PACKAGE_COMPLETION_SEAL_DEGRADED"
        posture = "STATIC_ARCHIVE_PACKAGE_COMPLETION_SEALED_WITH_OBSERVED_BLOCKERS"
    else:
        final_status = "STATIC_ARCHIVE_PACKAGE_COMPLETION_SEAL_PASS"
        posture = "STATIC_ARCHIVE_PACKAGE_COMPLETION_SEALED"

    governance_flags = {
        "completion_seal_receipt_only": True,
        "package_completion_seal_only": True,
        "advisory_only": True,
        "read_only": True,
        "non_authoritative": True,
        "source_linked": True,
        "deterministic_receipt": True,
        "complete_but_degraded_supported": True,
        "blocker_preservation_checked": True,
        "final_index_checked": True,
        "package_mutation_allowed": False,
        "distribution_claims_allowed": False,
        "release_readiness_claimed": False,
        "deployment_claimed": False,
        "public_release_claimed": False,
        "operator_action_recommended": False,
        "command_authority": False,
        "ui_command_authority": False,
        "action_authority": False,
        "recommendation_authority": False,
        "inference_authority": False,
        "prediction_allowed": False,
        "forecast_authority": False,
        "readiness_claims_allowed": False,
        "mutation_allowed": False,
        "authority_granted": False,
        "execution_authority": False,
        "routing_change_allowed": False,
        "queue_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "adaptive_behavior_allowed": False,
        "auto_execute": False,
        "auto_approve": False,
        "command_channel": False,
        "bidirectional_control": False,
        "script_allowed": False,
        "html_script_allowed": False,
        "external_fetch_allowed": False,
        "form_allowed": False,
        "button_allowed": False,
        "executable_payloads_present": False,
        "active_surfaces_present": False,
    }

    packet = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "receipt_id": RECEIPT_ID,
        "final_status": final_status,
        "completion_posture": posture,
        "checked_artifacts": {"P71": p71_path.as_posix(), **{k: v.as_posix() for k, v in refs.items()}},
        "ordered_surface_ids": EXPECTED_ORDER,
        "completion_evidence_summary": {
            "p71_doc_present": p71_exists,
            "p71_required_labels_present": not missing_p71_labels,
            "p70_final_status": p70.get("final_status", "NOT_COMPUTABLE"),
            "p70_pointer_count": p70.get("pointer_count", "NOT_COMPUTABLE"),
        },
        "package_chain_status_summary": {s: (loaded.get(s) or {}).get("final_status", "NOT_COMPUTABLE") for s in EXPECTED_ORDER},
        "blocker_preservation_summary": deepcopy(p70.get("blocker_preservation_summary", p69.get("blocker_preservation_summary", {}))),
        "governance_boundary_summary": {"distribution_claims_allowed": False, "release_readiness_claimed": False, "deployment_claimed": False},
        "p71_planning_summary": {"required_labels": p71_labels, "missing_labels": missing_p71_labels},
        "p70_final_index_summary": {"final_status": p70.get("final_status"), "final_index_posture": p70.get("final_index_posture"), "pointer_count": p70.get("pointer_count")},
        "source_hashes": {s: hashlib.sha256(raw.get(s, "").encode("utf-8")).hexdigest() if raw.get(s) else "NOT_COMPUTABLE" for s in EXPECTED_ORDER},
        "blocker_summary": sorted(set(blockers)),
        "governance_flags": governance_flags,
        "provenance": {"deterministic": True, "read_only": True, "non_authoritative": True, "source_linked": True},
        "broken_surface_ledger": sorted(set(blockers)),
    }
    packet["completion_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_static_archive_package_completion_seal_receipt_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P72 Static Archive Package Completion Seal Receipt",
        "",
        f"- final_status: `{packet.get('final_status', '')}`",
        f"- completion_posture: `{packet.get('completion_posture', '')}`",
        f"- completion_hash: `{packet.get('completion_hash', '')}`",
        "",
        "## Ordered Surface IDs",
    ]
    lines.extend([f"- `{s}`" for s in packet.get("ordered_surface_ids", [])])
    lines.extend(["", "## Broken Surface Ledger"])
    ledger = packet.get("broken_surface_ledger", [])
    lines.extend([f"- `{x}`" for x in ledger] if ledger else ["- none"])
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_static_archive_package_completion_seal_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(
        build_operator_narrative_static_archive_package_completion_seal_receipt_markdown(packet), encoding="utf-8"
    )
