from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths

SCHEMA_VERSION = "OperatorNarrativeArchiveChainClosureReceipt.v1"
PATCH_ID = "PATCH-P55-OPERATOR-NARRATIVE-ARCHIVE-CHAIN-CLOSURE-RECEIPT-001"
RECEIPT_ID = "operator_narrative_archive_chain_closure_receipt_001"
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
_P51_REPAIRED_BLOCKERS = {
    "source_missing:p42_report_json",
    "source_missing:p44_ui_overlay_json",
    "overlay report hash lineage mismatch",
}

_P52_AFFIRM_TRUE = {
    "archive_index_only",
    "passive_index_only",
    "read_only",
    "non_authoritative",
    "source_linked",
    "deterministic_manifest",
    "advisory_only",
}
_P53_AFFIRM_TRUE = {
    "audit_only",
    "advisory_only",
    "read_only",
    "non_authoritative",
    "archive_index_governance_audit_only",
    "source_linked",
    "deterministic_audit",
}
_DENY_FALSE = {
    "package_created",
    "distribution_claims_allowed",
    "command_authority",
    "ui_command_authority",
    "action_authority",
    "recommendation_authority",
    "inference_authority",
    "prediction_allowed",
    "forecast_authority",
    "trend_prediction_allowed",
    "readiness_claims_allowed",
    "mutation_allowed",
    "authority_granted",
    "execution_authority",
    "routing_change_allowed",
    "queue_mutation_allowed",
    "canon_mutation_allowed",
    "runtime_mutation_allowed",
    "adaptive_behavior_allowed",
    "psychological_claims_allowed",
    "speculative_causation_allowed",
    "auto_execute",
    "auto_approve",
    "command_channel",
    "bidirectional_control",
    "script_allowed",
    "html_script_allowed",
    "external_fetch_allowed",
    "form_allowed",
    "button_allowed",
}
_GOVERNANCE_FLAGS = {
    "closure_receipt_only": True,
    "advisory_only": True,
    "read_only": True,
    "non_authoritative": True,
    "source_linked": True,
    "deterministic_receipt": True,
    "archive_chain_closure_only": True,
    "blocker_preservation_checked": True,
    "package_created": False,
    "distribution_claims_allowed": False,
    "release_readiness_claimed": False,
    **{k: False for k in _DENY_FALSE if k not in {"package_created", "distribution_claims_allowed"}},
}
_REGISTRY_PATHS = [
    "out/archive/operator_narrative_export_preview_archive_index_001.latest.json",
    "out/audit/operator_narrative_export_preview_archive_index_governance_audit_001.latest.json",
    "out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.json",
    "out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.md",
]


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "MISSING"
    except (OSError, json.JSONDecodeError):
        return None, "CORRUPT"
    if not isinstance(payload, dict):
        return None, "CORRUPT"
    return payload, "PRESENT"


def _validate_flags(flags: dict[str, Any], affirm_true: set[str]) -> list[str]:
    blockers: list[str] = []
    for key in affirm_true:
        if flags.get(key) is not True:
            blockers.append(f"governance affirm true required: {key}")
    for key in _DENY_FALSE:
        if flags.get(key) is not False:
            blockers.append(f"governance deny false required: {key}")
    return blockers


def _registry_summary() -> dict[str, Any]:
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    ci_targets = set(list_ci_drift_artifact_paths(registry))
    emap = {e.artifact_path: e for e in registry.entries}
    observed: dict[str, Any] = {}
    for path in _REGISTRY_PATHS:
        entry = emap.get(path)
        observed[path] = {
            "present": entry is not None,
            "determinism_class": entry.determinism_class if entry else NOT_COMPUTABLE,
            "authority_granted": entry.authority_granted if entry else NOT_COMPUTABLE,
            "ci_drift_enforced": path in ci_targets,
        }
    return {
        "checked_registry_paths": _REGISTRY_PATHS,
        "expected_determinism_class": "DERIVED_OPTIONAL",
        "expected_authority_granted": False,
        "expected_ci_drift_enforced": False,
        "observed": observed,
    }


def build_operator_narrative_archive_chain_closure_receipt_packet(
    *,
    archive_index_json_path: str | Path = "out/archive/operator_narrative_export_preview_archive_index_001.latest.json",
    archive_audit_json_path: str | Path = "out/audit/operator_narrative_export_preview_archive_index_governance_audit_001.latest.json",
    archive_index_packet: dict[str, Any] | None = None,
    archive_audit_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    p52_path = Path(archive_index_json_path)
    p53_path = Path(archive_audit_json_path)
    p52, p52_status = (deepcopy(archive_index_packet), "PRESENT") if archive_index_packet is not None else _read_json(p52_path)
    p53, p53_status = (deepcopy(archive_audit_packet), "PRESENT") if archive_audit_packet is not None else _read_json(p53_path)

    blockers: list[str] = []
    if p52_status != "PRESENT":
        blockers.append(f"required source not readable: p52_archive_index_json ({p52_status})")
    if p53_status != "PRESENT":
        blockers.append(f"required source not readable: p53_archive_index_governance_audit_json ({p53_status})")

    if p52_status != "PRESENT" or p53_status != "PRESENT":
        final_status, closure_posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    else:
        assert p52 is not None and p53 is not None
        if not p52.get("archive_index_hash"):
            blockers.append("missing p52 archive_index_hash")
        if not p53.get("audit_hash"):
            blockers.append("missing p53 audit_hash")
        if p53.get("final_status") != "PASS" or p53.get("audit_posture") != "CLEAN":
            blockers.append("p53 PASS/CLEAN preservation violated")

        finding_counts = p53.get("finding_counts", {}) if isinstance(p53.get("finding_counts"), dict) else {}
        if int(finding_counts.get("FAIL", 0)) > 0 or int(finding_counts.get("WARN", 0)) > 0:
            blockers.append("p53 finding_counts FAIL/WARN must be zero")

        if p52.get("artifact_role_order") != _EXPECTED_ROLE_ORDER:
            blockers.append("p52 artifact_role_order mismatch")

        p52_flags = p52.get("governance_flags", {}) if isinstance(p52.get("governance_flags"), dict) else {}
        p53_flags = p53.get("governance_flags", {}) if isinstance(p53.get("governance_flags"), dict) else {}
        blockers.extend(_validate_flags(p52_flags, _P52_AFFIRM_TRUE))
        blockers.extend(_validate_flags(p53_flags, _P53_AFFIRM_TRUE))

        raw_count = p52.get("provenance", {}).get("raw_blocker_count")
        raw_hashes = p52.get("provenance", {}).get("raw_blocker_hashes")
        normalized = p52.get("provenance", {}).get("display_blocker_summary_normalized") is True
        if normalized and (not isinstance(raw_hashes, list) or not isinstance(raw_count, int)):
            blockers.append("raw blocker preservation evidence missing for normalized blockers")

        display_blockers = p52.get("blocker_summary", []) if isinstance(p52.get("blocker_summary"), list) else []
        if display_blockers and not normalized:
            blockers.append("blockers present but normalization evidence missing")
        if sorted(_P51_REPAIRED_BLOCKERS & set(str(x) for x in display_blockers)):
            blockers.append("p51 repaired blockers reintroduced")

        if p52_flags.get("package_created") is not False or p52_flags.get("distribution_claims_allowed") is not False:
            blockers.append("p52 package/distribution denial violated")
        if p53_flags.get("package_created") is not False or p53_flags.get("distribution_claims_allowed") is not False:
            blockers.append("p53 package/distribution denial violated")

        if blockers:
            final_status, closure_posture = "FAIL", "FAILED"
        elif p52.get("final_status") == "ARCHIVE_INDEX_DEGRADED":
            final_status, closure_posture = "CLOSURE_RECEIPT_DEGRADED", "SEALED_WITH_OBSERVED_BLOCKERS"
        else:
            final_status, closure_posture = "CLOSURE_RECEIPT_ONLY", "SEALED"

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "receipt_id": RECEIPT_ID,
        "final_status": final_status,
        "closure_posture": closure_posture,
        "checked_artifacts": {
            "p52_archive_index_json": p52_path.as_posix(),
            "p53_archive_index_governance_audit_json": p53_path.as_posix(),
        },
        "archive_chain_summary": {
            "p52_final_status": str((p52 or {}).get("final_status", NOT_COMPUTABLE)),
            "p52_archive_posture": str((p52 or {}).get("archive_posture", NOT_COMPUTABLE)),
            "p53_final_status": str((p53 or {}).get("final_status", NOT_COMPUTABLE)),
            "p53_audit_posture": str((p53 or {}).get("audit_posture", NOT_COMPUTABLE)),
        },
        "closure_evidence": {
            "p54_repair_evidence_via_p53_pass_clean": bool((p53 or {}).get("final_status") == "PASS" and (p53 or {}).get("audit_posture") == "CLEAN"),
            "p53_language_boundary_fail_count": sum(1 for f in ((p53 or {}).get("findings") or []) if isinstance(f, dict) and f.get("severity") == "FAIL" and f.get("category") == "LANGUAGE_BOUNDARY"),
            "p52_role_order_preserved": (p52 or {}).get("artifact_role_order") == _EXPECTED_ROLE_ORDER,
        },
        "hash_lineage": {
            "p52_archive_index_hash": str((p52 or {}).get("archive_index_hash", "")),
            "p53_audit_hash": str((p53 or {}).get("audit_hash", "")),
        },
        "blocker_preservation_summary": {
            "display_blocker_count": len((p52 or {}).get("blocker_summary", []) if isinstance((p52 or {}).get("blocker_summary"), list) else []),
            "raw_blocker_count": (p52 or {}).get("provenance", {}).get("raw_blocker_count", NOT_COMPUTABLE),
            "raw_blocker_hash_count": len((p52 or {}).get("provenance", {}).get("raw_blocker_hashes", []) if isinstance((p52 or {}).get("provenance", {}).get("raw_blocker_hashes"), list) else []),
            "display_blocker_summary_normalized": (p52 or {}).get("provenance", {}).get("display_blocker_summary_normalized", False),
            "p51_repaired_blockers_reintroduced": sorted(_P51_REPAIRED_BLOCKERS & set((p52 or {}).get("blocker_summary", []))),
        },
        "governance_flag_summary": {
            "p52_affirm_true": sorted(_P52_AFFIRM_TRUE),
            "p53_affirm_true": sorted(_P53_AFFIRM_TRUE),
            "deny_false": sorted(_DENY_FALSE),
        },
        "registry_classification_summary": _registry_summary(),
        "source_hashes": {
            "p52_archive_index_json": canonical_hash(p52) if p52 else NOT_COMPUTABLE,
            "p53_archive_index_governance_audit_json": canonical_hash(p53) if p53 else NOT_COMPUTABLE,
        },
        "blocker_summary": sorted(set(blockers)),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "deterministic": True,
            "closure_receipt_only": True,
            "read_only": True,
            "non_authoritative": True,
            "source_linked": True,
            "fail_closed": True,
            "source_presence": {
                "p52_archive_index_json": p52_status,
                "p53_archive_index_governance_audit_json": p53_status,
            },
        },
    }
    packet["closure_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_archive_chain_closure_receipt_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P55 Operator Narrative Archive Chain Closure Receipt",
        "",
        f"- receipt_id: `{packet.get('receipt_id','')}`",
        f"- final_status: `{packet.get('final_status','')}`",
        f"- closure_posture: `{packet.get('closure_posture','')}`",
        f"- closure_hash: `{packet.get('closure_hash','')}`",
        "",
        "## Archive Chain Summary",
    ]
    for k, v in (packet.get("archive_chain_summary") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Closure Evidence"])
    for k, v in (packet.get("closure_evidence") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Blocker Preservation"])
    for k, v in (packet.get("blocker_preservation_summary") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Blockers"])
    blockers = packet.get("blocker_summary", [])
    lines.extend([f"- `{b}`" for b in blockers] if blockers else ["- none"])
    lines.extend(["", "## Governance Boundary"])
    for k, v in (packet.get("governance_flags") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_archive_chain_closure_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_archive_chain_closure_receipt_markdown(packet), encoding="utf-8")
