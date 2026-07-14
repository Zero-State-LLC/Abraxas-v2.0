from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.operator_narrative_archive_chain_closure_receipt import (
    build_operator_narrative_archive_chain_closure_receipt_packet,
)
from core.operator_narrative_export_preview_archive_index import (
    build_operator_narrative_export_preview_archive_index_packet,
)
from core.operator_narrative_export_preview_archive_index_governance_audit import (
    build_operator_narrative_export_preview_archive_index_governance_audit_packet,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "OperatorNarrativeArchiveChainStabilityReceipt.v1"
PATCH_ID = "PATCH-P56-OPERATOR-NARRATIVE-ARCHIVE-CHAIN-STABILITY-RECEIPT-001"
RECEIPT_ID = "operator_narrative_archive_chain_stability_receipt_001"

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
_P51_REPAIRED_BLOCKERS = {
    "source_missing:p42_report_json",
    "source_missing:p44_ui_overlay_json",
    "overlay report hash lineage mismatch",
}
_DENY_FALSE = {
    "package_created", "distribution_claims_allowed", "release_readiness_claimed", "command_authority", "ui_command_authority", "action_authority", "recommendation_authority", "inference_authority", "prediction_allowed", "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed", "mutation_allowed", "authority_granted", "execution_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "adaptive_behavior_allowed", "psychological_claims_allowed", "speculative_causation_allowed", "auto_execute", "auto_approve", "command_channel", "bidirectional_control", "script_allowed", "html_script_allowed", "external_fetch_allowed", "form_allowed", "button_allowed",
}
_P52_TRUE = {"archive_index_only", "passive_index_only", "read_only", "non_authoritative", "source_linked", "deterministic_manifest", "advisory_only"}
_P53_TRUE = {"audit_only", "advisory_only", "read_only", "non_authoritative", "archive_index_governance_audit_only", "source_linked", "deterministic_audit"}
_P55_TRUE = {"closure_receipt_only", "advisory_only", "read_only", "non_authoritative", "source_linked", "deterministic_receipt", "archive_chain_closure_only", "blocker_preservation_checked"}
_GOVERNANCE_FLAGS = {
    "stability_receipt_only": True,
    "advisory_only": True,
    "read_only": True,
    "non_authoritative": True,
    "source_linked": True,
    "deterministic_receipt": True,
    "replay_invariance_only": True,
    "blocker_preservation_checked": True,
    **{k: False for k in _DENY_FALSE},
}


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "MISSING"
    except (OSError, json.JSONDecodeError):
        return None, "CORRUPT"
    return (payload, "PRESENT") if isinstance(payload, dict) else (None, "CORRUPT")


def _validate_flags(flags: dict[str, Any], affirm: set[str]) -> list[str]:
    blockers: list[str] = []
    for key in affirm:
        if flags.get(key) is not True:
            blockers.append(f"required true governance flag missing: {key}")
    for key in _DENY_FALSE:
        if key in flags and flags.get(key) is not False:
            blockers.append(f"required false governance flag violated: {key}")
    return blockers


def build_operator_narrative_archive_chain_stability_receipt_packet(
    *,
    archive_index_json_path: str | Path = "out/archive/operator_narrative_export_preview_archive_index_001.latest.json",
    archive_audit_json_path: str | Path = "out/audit/operator_narrative_export_preview_archive_index_governance_audit_001.latest.json",
    archive_closure_json_path: str | Path = "out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.json",
    replay_count: int = 3,
    replay_runs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    p52_path, p53_path, p55_path = Path(archive_index_json_path), Path(archive_audit_json_path), Path(archive_closure_json_path)
    p52, p52_status = _read_json(p52_path)
    p53, p53_status = _read_json(p53_path)
    p55, p55_status = _read_json(p55_path)
    blockers: list[str] = []

    if p52_status != "PRESENT":
        blockers.append(f"required source not readable: p52_archive_index_json ({p52_status})")
    if p53_status != "PRESENT":
        blockers.append(f"required source not readable: p53_archive_index_governance_audit_json ({p53_status})")
    if p55_status != "PRESENT":
        blockers.append(f"required source not readable: p55_archive_chain_closure_receipt_json ({p55_status})")

    if blockers:
        final_status, posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
        replays: list[dict[str, Any]] = []
    else:
        assert p52 and p53 and p55
        baseline_hashes = {
            "archive_index_hash": str(p52.get("archive_index_hash", "")),
            "archive_governance_audit_hash": str(p53.get("audit_hash", "")),
            "archive_closure_hash": str(p55.get("closure_hash", "")),
        }
        for k, v in baseline_hashes.items():
            if not v:
                blockers.append(f"missing baseline hash: {k}")

        runs = replay_runs if replay_runs is not None else [
            {
                "p52": build_operator_narrative_export_preview_archive_index_packet(),
                "p53": build_operator_narrative_export_preview_archive_index_governance_audit_packet(),
                "p55": build_operator_narrative_archive_chain_closure_receipt_packet(),
            }
            for _ in range(replay_count)
        ]
        replays = []
        for i, run in enumerate(runs, start=1):
            rp52, rp53, rp55 = run["p52"], run["p53"], run["p55"]
            replays.append({
                "replay_index": i,
                "archive_index_hash": rp52.get("archive_index_hash", ""),
                "archive_governance_audit_hash": rp53.get("audit_hash", ""),
                "archive_closure_hash": rp55.get("closure_hash", ""),
                "p53_final_status": rp53.get("final_status", NOT_COMPUTABLE),
                "p53_audit_posture": rp53.get("audit_posture", NOT_COMPUTABLE),
                "p55_final_status": rp55.get("final_status", NOT_COMPUTABLE),
                "p55_closure_posture": rp55.get("closure_posture", NOT_COMPUTABLE),
            })
            if rp52.get("archive_index_hash") != baseline_hashes["archive_index_hash"]:
                blockers.append(f"replay {i} archive_index_hash mismatch")
            if rp53.get("audit_hash") != baseline_hashes["archive_governance_audit_hash"]:
                blockers.append(f"replay {i} audit_hash mismatch")
            if rp55.get("closure_hash") != baseline_hashes["archive_closure_hash"]:
                blockers.append(f"replay {i} closure_hash mismatch")
            if rp52.get("artifact_role_order") != _EXPECTED_ROLE_ORDER:
                blockers.append(f"replay {i} role order mismatch")

        p52_flags = p52.get("governance_flags", {}) if isinstance(p52.get("governance_flags"), dict) else {}
        p53_flags = p53.get("governance_flags", {}) if isinstance(p53.get("governance_flags"), dict) else {}
        p55_flags = p55.get("governance_flags", {}) if isinstance(p55.get("governance_flags"), dict) else {}
        blockers.extend(_validate_flags(p52_flags, _P52_TRUE))
        blockers.extend(_validate_flags(p53_flags, _P53_TRUE))
        blockers.extend(_validate_flags(p55_flags, _P55_TRUE))

        if p53.get("final_status") != "PASS" or p53.get("audit_posture") != "CLEAN":
            blockers.append("p53 PASS/CLEAN preservation violated")
        if str(p55.get("closure_posture", "")).startswith("SEALED") is False:
            blockers.append("p55 closure posture not sealed")

        raw_count = p52.get("provenance", {}).get("raw_blocker_count")
        raw_hashes = p52.get("provenance", {}).get("raw_blocker_hashes")
        if not isinstance(raw_count, int) or not isinstance(raw_hashes, list):
            blockers.append("raw blocker preservation evidence missing")
        elif raw_count > 0 and not raw_hashes:
            blockers.append("raw blocker hash evidence empty while raw blocker count > 0")

        display_blockers = set(str(x) for x in (p52.get("blocker_summary") or []))
        if _P51_REPAIRED_BLOCKERS & display_blockers:
            blockers.append("p51 repaired blockers reintroduced")

        if blockers:
            final_status, posture = "FAIL", "FAILED"
        elif p52.get("final_status") == "ARCHIVE_INDEX_DEGRADED" or p55.get("final_status") == "CLOSURE_RECEIPT_DEGRADED":
            final_status, posture = "STABILITY_RECEIPT_DEGRADED", "STABLE_WITH_OBSERVED_BLOCKERS"
        else:
            final_status, posture = "STABILITY_RECEIPT_ONLY", "STABLE"

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "receipt_id": RECEIPT_ID,
        "final_status": final_status,
        "stability_posture": posture,
        "replay_count": replay_count,
        "checked_artifacts": {
            "p52_archive_index_json": p52_path.as_posix(),
            "p53_archive_index_governance_audit_json": p53_path.as_posix(),
            "p55_archive_chain_closure_receipt_json": p55_path.as_posix(),
        },
        "baseline_hashes": {
            "archive_index_hash": str((p52 or {}).get("archive_index_hash", "")),
            "archive_governance_audit_hash": str((p53 or {}).get("audit_hash", "")),
            "archive_closure_hash": str((p55 or {}).get("closure_hash", "")),
        },
        "replay_results": replays,
        "invariance_summary": {
            "archive_index_hash_stable": all(r.get("archive_index_hash") == str((p52 or {}).get("archive_index_hash", "")) for r in replays),
            "archive_governance_audit_hash_stable": all(r.get("archive_governance_audit_hash") == str((p53 or {}).get("audit_hash", "")) for r in replays),
            "archive_closure_hash_stable": all(r.get("archive_closure_hash") == str((p55 or {}).get("closure_hash", "")) for r in replays),
        },
        "role_order_summary": {"expected": _EXPECTED_ROLE_ORDER, "observed": (p52 or {}).get("artifact_role_order", [])},
        "governance_flag_summary": {"p52_affirm_true": sorted(_P52_TRUE), "p53_affirm_true": sorted(_P53_TRUE), "p55_affirm_true": sorted(_P55_TRUE), "deny_false": sorted(_DENY_FALSE)},
        "blocker_preservation_summary": {
            "display_blocker_count": len((p52 or {}).get("blocker_summary", []) if isinstance((p52 or {}).get("blocker_summary"), list) else []),
            "raw_blocker_count": (p52 or {}).get("provenance", {}).get("raw_blocker_count", NOT_COMPUTABLE),
            "raw_blocker_hash_count": len((p52 or {}).get("provenance", {}).get("raw_blocker_hashes", []) if isinstance((p52 or {}).get("provenance", {}).get("raw_blocker_hashes"), list) else []),
        },
        "repaired_blocker_guard_summary": {"p51_repaired_blockers_reintroduced": sorted(_P51_REPAIRED_BLOCKERS & set((p52 or {}).get("blocker_summary", [])))},
        "hash_lineage": {"p52_archive_index_hash": str((p52 or {}).get("archive_index_hash", "")), "p53_audit_hash": str((p53 or {}).get("audit_hash", "")), "p55_closure_hash": str((p55 or {}).get("closure_hash", ""))},
        "source_hashes": {
            "p52_archive_index_json": canonical_hash(p52) if p52 else NOT_COMPUTABLE,
            "p53_archive_index_governance_audit_json": canonical_hash(p53) if p53 else NOT_COMPUTABLE,
            "p55_archive_chain_closure_receipt_json": canonical_hash(p55) if p55 else NOT_COMPUTABLE,
        },
        "blocker_summary": sorted(set(blockers)),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "deterministic": True,
            "read_only": True,
            "non_authoritative": True,
            "source_linked": True,
            "fail_closed": True,
            "source_presence": {
                "p52_archive_index_json": p52_status,
                "p53_archive_index_governance_audit_json": p53_status,
                "p55_archive_chain_closure_receipt_json": p55_status,
            },
        },
    }
    packet["stability_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_archive_chain_stability_receipt_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P56 Operator Narrative Archive Chain Stability Receipt",
        "",
        f"- receipt_id: `{packet.get('receipt_id','')}`",
        f"- final_status: `{packet.get('final_status','')}`",
        f"- stability_posture: `{packet.get('stability_posture','')}`",
        f"- stability_hash: `{packet.get('stability_hash','')}`",
        "",
        "## Baseline Hashes",
    ]
    for k, v in (packet.get("baseline_hashes") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Replay Results"])
    for row in packet.get("replay_results", []):
        lines.append(f"- replay `{row.get('replay_index')}`: p52=`{row.get('archive_index_hash')}` p53=`{row.get('archive_governance_audit_hash')}` p55=`{row.get('archive_closure_hash')}`")
    lines.extend(["", "## Invariance Summary"])
    for k, v in (packet.get("invariance_summary") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Blockers"])
    b = packet.get("blocker_summary", [])
    lines.extend([f"- `{x}`" for x in b] if b else ["- none"])
    lines.extend(["", "## Governance Boundary"])
    for k, v in (packet.get("governance_flags") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_archive_chain_stability_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_archive_chain_stability_receipt_markdown(packet), encoding="utf-8")
