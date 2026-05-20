from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "static_archive_package_final_index_receipt"
SCHEMA_VERSION = "OperatorNarrativeStaticArchivePackageFinalIndexReceipt.v1"
PATCH_ID = "PATCH-P70-OPERATOR-NARRATIVE-STATIC-ARCHIVE-PACKAGE-FINAL-INDEX-RECEIPT-001"
RECEIPT_ID = "operator_narrative_static_archive_package_final_index_receipt_001"
EXPECTED_ORDER = ["P64", "P65", "P66", "P67", "P68", "P69"]


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


def build_operator_narrative_static_archive_package_final_index_receipt_packet(*, repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[1]
    refs = {
        "P64": root / "out/package/operator_narrative_static_archive_package_001.latest.json",
        "P65": root / "out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json",
        "P66": root / "out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.json",
        "P67": root / "out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.json",
        "P68": root / "out/audit/operator_narrative_static_archive_package_chain_closure_receipt_001.latest.json",
        "P69": root / "out/audit/operator_narrative_static_archive_package_index_pointer_receipt_001.latest.json",
    }
    loaded: dict[str, dict[str, Any] | None] = {}
    raw: dict[str, str] = {}
    state: dict[str, str] = {}
    blockers: list[str] = []

    for sid, path in refs.items():
        obj, st, txt = _read_json(path)
        loaded[sid], raw[sid], state[sid] = obj, txt, st

    if any(state[s] != "PRESENT" for s in EXPECTED_ORDER):
        blockers.extend([f"{s} missing/corrupt" for s in EXPECTED_ORDER if state[s] != "PRESENT"])

    manifest: list[dict[str, Any]] = []
    for sid in EXPECTED_ORDER:
        pkt = loaded.get(sid) or {}
        posture = str(pkt.get("final_index_posture", pkt.get("index_posture", pkt.get("closure_posture", pkt.get("stability_posture", pkt.get("audit_posture", "NOT_COMPUTABLE"))))))
        governing_field = "package_hash" if sid == "P64" else ("audit_hash" if sid in {"P65", "P66"} else ("stability_hash" if sid == "P67" else ("closure_hash" if sid == "P68" else "index_hash")))
        manifest.append({
            "surface_id": sid,
            "role": "static_archive_package" if sid == "P64" else "audit_or_receipt",
            "path": refs[sid].as_posix(),
            "exists": state[sid] == "PRESENT",
            "readable": state[sid] == "PRESENT",
            "sha256": hashlib.sha256(raw.get(sid, "").encode("utf-8")).hexdigest() if raw.get(sid) else "NOT_COMPUTABLE",
            "canonical_hash": canonical_hash(pkt) if pkt else "NOT_COMPUTABLE",
            "final_status": str(pkt.get("final_status", "NOT_COMPUTABLE")),
            "posture": posture,
            "governing_hash_field": governing_field,
            "governing_hash_value": str(pkt.get(governing_field, "NOT_COMPUTABLE")),
            "blocker_or_degraded_observed": "DEGRADED" in str(pkt.get("final_status", "")) or bool((pkt.get("blocker_preservation_summary") or {}).get("observed_degraded_roles")),
            "classification": "DERIVED_OPTIONAL",
            "compact_reference_only": True,
        })

    p64, p65, p66, p67, p68, p69 = (loaded.get("P64") or {}), (loaded.get("P65") or {}), (loaded.get("P66") or {}), (loaded.get("P67") or {}), (loaded.get("P68") or {}), (loaded.get("P69") or {})

    if p64.get("final_status") not in {"PACKAGE_CREATED_STATIC", "PACKAGE_CREATED_DEGRADED"}:
        blockers.append("P64 final_status invalid")
    for key in ["package_hash", "package_created", "static_only"]:
        if key == "package_hash" and not p64.get(key):
            blockers.append("P64 package_hash missing")
        if key != "package_hash" and p64.get(key) is not True:
            blockers.append(f"P64 {key} invalid")
    for key in ["distribution_claims_allowed", "release_readiness_claimed", "executable_payloads_present"]:
        if p64.get(key) is not False:
            blockers.append(f"P64 forbidden flag true: {key}")

    if p65.get("final_status") != "PACKAGE_GOVERNANCE_AUDIT_PASS" or p65.get("audit_posture") != "PACKAGE_GOVERNANCE_CLEAN" or not p65.get("audit_hash"):
        blockers.append("P65 status/posture/hash invalid")
    if p66.get("final_status") != "PACKAGE_LANGUAGE_BOUNDARY_PASS" or p66.get("audit_posture") != "LANGUAGE_BOUNDARY_CLEAN" or not p66.get("audit_hash"):
        blockers.append("P66 status/posture/hash invalid")
    if p67.get("final_status") not in {"PACKAGE_STABILITY_RECEIPT_PASS", "PACKAGE_STABILITY_RECEIPT_DEGRADED"} or not p67.get("stability_hash") or int(p67.get("replay_count", 0) or 0) < 3:
        blockers.append("P67 status/hash/replay invalid")
    if p68.get("final_status") not in {"STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_PASS", "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_DEGRADED"} or not p68.get("closure_hash"):
        blockers.append("P68 status/hash invalid")
    if p69.get("pointer_count") != 5 or p69.get("ordered_surface_ids") != ["P64", "P65", "P66", "P67", "P68"] or not p69.get("index_hash"):
        blockers.append("P69 pointer summary invalid")

    if [m["surface_id"] for m in manifest] != EXPECTED_ORDER:
        blockers.append("ordered_surface_ids mismatch")

    degraded = any(m["blocker_or_degraded_observed"] for m in manifest)

    if any(state[s] != "PRESENT" for s in EXPECTED_ORDER):
        final_status = "NOT_COMPUTABLE"
        posture = "NOT_COMPUTABLE"
    elif blockers:
        final_status = "STATIC_ARCHIVE_PACKAGE_FINAL_INDEX_FAIL"
        posture = "STATIC_ARCHIVE_PACKAGE_FINAL_INDEX_FAILED"
    elif degraded:
        final_status = "STATIC_ARCHIVE_PACKAGE_FINAL_INDEX_DEGRADED"
        posture = "STATIC_ARCHIVE_PACKAGE_FINAL_INDEX_STABLE_WITH_OBSERVED_BLOCKERS"
    else:
        final_status = "STATIC_ARCHIVE_PACKAGE_FINAL_INDEX_PASS"
        posture = "STATIC_ARCHIVE_PACKAGE_FINAL_INDEX_STABLE"

    governance_flags = {
        "final_index_receipt_only": True, "package_final_index_only": True, "compact_reference_only": True,
        "advisory_only": True, "read_only": True, "non_authoritative": True, "source_linked": True,
        "deterministic_receipt": True, "package_chain_indexed": True, "pointer_receipt_checked": True,
        "blocker_preservation_checked": True,
        "package_mutation_allowed": False, "distribution_claims_allowed": False, "release_readiness_claimed": False,
        "command_authority": False, "ui_command_authority": False, "action_authority": False,
        "recommendation_authority": False, "inference_authority": False, "prediction_allowed": False,
        "forecast_authority": False, "trend_prediction_allowed": False, "readiness_claims_allowed": False,
        "mutation_allowed": False, "authority_granted": False, "execution_authority": False,
        "routing_change_allowed": False, "queue_mutation_allowed": False, "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False, "adaptive_behavior_allowed": False, "psychological_claims_allowed": False,
        "speculative_causation_allowed": False, "auto_execute": False, "auto_approve": False,
        "command_channel": False, "bidirectional_control": False, "script_allowed": False,
        "html_script_allowed": False, "external_fetch_allowed": False, "form_allowed": False,
        "button_allowed": False, "executable_payloads_present": False, "active_surfaces_present": False,
    }

    packet = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "receipt_id": RECEIPT_ID,
        "final_status": final_status,
        "final_index_posture": posture,
        "checked_artifacts": {k: v.as_posix() for k, v in refs.items()},
        "ordered_surface_ids": EXPECTED_ORDER,
        "pointer_count": 6,
        "final_index_manifest": manifest,
        "source_hashes": {k: m["sha256"] for k, m in zip(EXPECTED_ORDER, manifest, strict=False)},
        "status_summary": {m["surface_id"]: m["final_status"] for m in manifest},
        "posture_summary": {m["surface_id"]: m["posture"] for m in manifest},
        "blocker_preservation_summary": deepcopy(p69.get("blocker_preservation_summary", p68.get("blocker_preservation_summary", {}))),
        "governance_boundary_summary": {"distribution_claims_allowed": False, "release_readiness_claimed": False, "command_authority": False},
        "p69_pointer_summary": {"pointer_count": p69.get("pointer_count"), "ordered_surface_ids": p69.get("ordered_surface_ids"), "index_hash": p69.get("index_hash")},
        "registry_classification_summary": {sid: "DERIVED_OPTIONAL" for sid in EXPECTED_ORDER},
        "follow_on_summary": {"next_surface": None, "chain_complete": True},
        "blocker_summary": sorted(set(blockers)),
        "governance_flags": governance_flags,
        "provenance": {"deterministic": True, "read_only": True, "non_authoritative": True, "source_linked": True},
        "broken_surface_ledger": sorted(set(blockers)),
    }
    packet["final_index_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_static_archive_package_final_index_receipt_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P70 Static Archive Package Final Index Receipt", "",
        f"- final_status: `{packet.get('final_status','')}`",
        f"- final_index_posture: `{packet.get('final_index_posture','')}`",
        f"- final_index_hash: `{packet.get('final_index_hash','')}`",
        f"- pointer_count: `{packet.get('pointer_count',0)}`", "", "## Ordered Surface IDs",
    ]
    lines.extend([f"- `{s}`" for s in packet.get("ordered_surface_ids", [])])
    lines.extend(["", "## Broken Surface Ledger"])
    ledger = packet.get("broken_surface_ledger", [])
    lines.extend([f"- `{x}`" for x in ledger] if ledger else ["- none"])
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_static_archive_package_final_index_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_static_archive_package_final_index_receipt_markdown(packet), encoding="utf-8")
