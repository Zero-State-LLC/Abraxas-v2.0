from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_phase1_operator_decision_evidence_collection_plan import (
    _authority_locks,
)
from core.abx_codegen_phase1_operator_decision_evidence_collection_validation_plan import (
    VALIDATION_PLAN_JSON_PATH as SOURCE_VALIDATION_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = (
    "AbxCodegenPhase1OperatorDecisionEvidenceCollectionValidationDryRun.v1"
)
VALIDATION_DRY_RUN_ID = (
    "abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_001"
)
VALIDATION_DRY_RUN_JSON_PATH = Path(
    "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_001.latest.json"
)
VALIDATION_DRY_RUN_MD_PATH = VALIDATION_DRY_RUN_JSON_PATH.with_suffix(".md")

EXPECTED_SOURCE_STATUS = (
    "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_PLAN_READY"
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mapping_list(value: Any) -> list[dict[str, Any]]:
    return [dict(item) for item in value] if isinstance(value, list) else []


def _normalize_check_results(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "check_id": str(item.get("check_id", "NOT_COMPUTABLE")),
            "passed": bool(item.get("passed", False)),
        }
        for item in sorted(checks, key=lambda item: str(item.get("check_id", "")))
    ]


def _all_passed(checks: list[dict[str, Any]]) -> bool:
    return bool(checks) and all(item.get("passed") is True for item in checks)


def build_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_path = root / SOURCE_VALIDATION_PLAN_JSON
    validation_plan = _read_json(source_path)
    source_observed = validation_plan is not None
    validation_plan = validation_plan or {}

    source_status = str(validation_plan.get("status", "NOT_COMPUTABLE"))
    source_ready = (
        validation_plan.get("schema_version")
        == "AbxCodegenPhase1OperatorDecisionEvidenceCollectionValidationPlan.v1"
        and source_status == EXPECTED_SOURCE_STATUS
    )

    bundle_group_results = _mapping_list(validation_plan.get("bundle_group_checks"))
    invariant_results = _mapping_list(validation_plan.get("invariant_checks"))
    authority_lock_results = _mapping_list(validation_plan.get("authority_lock_checks"))
    executed_validation_checks = _normalize_check_results(
        _mapping_list(validation_plan.get("validation_checks"))
    )
    source_readiness_summary = dict(
        validation_plan.get(
            "source_readiness_summary",
            {
                "simulated_only": False,
                "operator_input_required": False,
                "groups_ready": -1,
                "groups_total": -1,
                "evidence_bundle_complete": False,
                "valid_for_decision_record": False,
                "evaluation_blockers": [
                    "source_validation_plan_missing_or_unreadable"
                ],
            },
        )
    )
    source_validation_blockers = [
        str(item) for item in validation_plan.get("validation_blockers", [])
    ]
    source_blockers = [str(item) for item in validation_plan.get("blockers", [])]

    group_presence = all(
        [
            bundle_group_results,
            invariant_results,
            authority_lock_results,
            executed_validation_checks,
        ]
    )
    checks_passed = _all_passed(executed_validation_checks)
    bundle_groups_passed = _all_passed(bundle_group_results)
    invariants_passed = _all_passed(invariant_results)
    authority_locks_passed = _all_passed(authority_lock_results)
    summary_valid = (
        source_readiness_summary.get("simulated_only") is True
        and source_readiness_summary.get("operator_input_required") is True
        and source_readiness_summary.get("groups_ready") == 0
        and source_readiness_summary.get("evidence_bundle_complete") is False
        and source_readiness_summary.get("valid_for_decision_record") is False
        and bool(source_readiness_summary.get("evaluation_blockers"))
    )
    plan_authority_locked = (
        validation_plan.get("operator_attestations_present") is False
        and validation_plan.get("evidence_bundle_created") is False
        and validation_plan.get("decision_record_created") is False
        and validation_plan.get("authorization_record_created") is False
        and validation_plan.get("authorization_record_lane_authorized") is False
        and validation_plan.get("implementation_authorized") is False
        and validation_plan.get("implementation_unblocked") is False
        and validation_plan.get("shadow_replay_execution_authorized") is False
        and validation_plan.get("execution_authority") is False
        and validation_plan.get("valid_for_execution") is False
        and validation_plan.get("valid_for_implementation") is False
        and validation_plan.get("valid_for_decision_record") is False
        and validation_plan.get("recommended_next_patch") == "NOT_COMPUTABLE"
    )

    validation_passed = (
        source_ready
        and group_presence
        and checks_passed
        and bundle_groups_passed
        and invariants_passed
        and authority_locks_passed
        and summary_valid
        and plan_authority_locked
        and not source_validation_blockers
        and not source_blockers
    )
    validation_blockers = sorted(
        {
            *(["source_validation_plan_missing_or_unreadable"] if not source_observed else []),
            *(["source_validation_plan_missing_or_not_ready"] if not source_ready else []),
            *(["missing_validation_check_group"] if not group_presence else []),
            *(["planned_validation_check_failed"] if not checks_passed else []),
            *(["bundle_group_validation_failed"] if not bundle_groups_passed else []),
            *(["validation_plan_invariant_check_failed"] if not invariants_passed else []),
            *(["authority_lock_validation_failed"] if not authority_locks_passed else []),
            *(["source_readiness_summary_not_fail_closed"] if not summary_valid else []),
            *(["source_validation_plan_authority_not_locked"] if not plan_authority_locked else []),
            *(f"source_validation_blocker:{item}" for item in source_validation_blockers),
            *(f"source_blocker:{item}" for item in source_blockers),
        }
    )

    if not source_observed:
        status = "NOT_COMPUTABLE"
        blockers = [
            "source_validation_plan_missing_or_unreadable",
            f"source_path:{SOURCE_VALIDATION_PLAN_JSON}",
        ]
    elif not source_ready:
        status = (
            "BLOCKED_BY_ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_PLAN"
        )
        blockers = [f"source_validation_plan_status:{source_status}"]
    elif validation_blockers:
        status = (
            "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_DRY_RUN_FAILED"
        )
        blockers = validation_blockers
    else:
        status = (
            "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_DRY_RUN_READY"
        )
        blockers = []

    validation_result_summary = {
        "simulated_only": True,
        "validation_passed": validation_passed,
        "validation_check_groups_present": group_presence,
        "checks_total": (
            len(bundle_group_results)
            + len(invariant_results)
            + len(authority_lock_results)
            + len(executed_validation_checks)
        ),
        "checks_failed": len(
            [
                item
                for item in (
                    bundle_group_results
                    + invariant_results
                    + authority_lock_results
                    + executed_validation_checks
                )
                if item.get("passed") is not True
            ]
        ),
        "validation_blocker_count": len(validation_blockers),
        "source_blocker_count": len(source_blockers),
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "valid_for_decision_record": False,
    }
    validation_result_summary["checks_passed"] = (
        validation_result_summary["checks_total"]
        - validation_result_summary["checks_failed"]
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "validation_dry_run_id": VALIDATION_DRY_RUN_ID,
        "validation_dry_run_hash": "",
        "source_validation_plan_path": str(SOURCE_VALIDATION_PLAN_JSON),
        "source_validation_plan_observed": source_observed,
        "source_validation_plan_ready": source_ready,
        "source_validation_plan_file_hash": _sha256(source_path),
        "source_validation_plan_packet_hash": str(
            validation_plan.get("validation_plan_hash", "NOT_COMPUTABLE")
        ),
        "source_validation_plan_status": source_status,
        "source_review_artifacts": [
            str(item) for item in validation_plan.get("source_review_artifacts", [])
        ],
        "replayed_bundle_group_results": bundle_group_results,
        "replayed_invariant_results": invariant_results,
        "replayed_authority_lock_results": authority_lock_results,
        "executed_validation_checks": executed_validation_checks,
        "source_readiness_summary": source_readiness_summary,
        "validation_result_summary": validation_result_summary,
        "validation_passed": validation_passed,
        "validation_blockers": validation_blockers,
        "blockers": blockers,
        "validation_dry_run_only": True,
        "validation_only": True,
        "simulated_only": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "evidence_bundle_created": False,
        "decision_record_created": False,
        "authorization_record_created": False,
        "authorization_record_lane_authorized": False,
        "implementation_authorized": False,
        "implementation_unblocked": False,
        "shadow_replay_execution_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "valid_for_decision_record": False,
        "recommended_next_action": (
            "preserve the Codegen Phase 1 operator review hold; this dry run only "
            "replays validation-plan checks and cannot create evidence, decisions, "
            "authorization records, code, fixtures, receipts, writeback, or execution"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "authority_locks": _authority_locks(),
    }
    packet["validation_dry_run_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "validation_dry_run_hash"}
    )
    return packet


def render_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Phase 1 Operator Decision Evidence Collection Validation Dry Run",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_validation_plan_ready`: `{packet['source_validation_plan_ready']}`",
        f"- `validation_passed`: `{packet['validation_passed']}`",
        f"- `valid_for_decision_record`: `{packet['valid_for_decision_record']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Validation Blockers",
        "",
    ]
    if packet["validation_blockers"]:
        for blocker in packet["validation_blockers"]:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- `none`")
    lines.extend(["", "## Validation Result Summary", ""])
    summary = packet["validation_result_summary"]
    for key in sorted(summary):
        lines.append(f"- `{key}`: `{summary[key]}`")
    return lines


def write_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
        root
    )
    write_canonical_json(target_root / VALIDATION_DRY_RUN_JSON_PATH, packet)
    _write_markdown(
        target_root / VALIDATION_DRY_RUN_MD_PATH,
        render_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_markdown(
            packet
        ),
    )
    return packet
