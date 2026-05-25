from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordValidationDryRun.v1"
SOURCE_VALIDATION_PLAN_PATH = "out/temporal_continuity_operator_authorization_record_validation_plan/latest.json"


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "validation_dry_run_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _execute_check_results(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "check_id": str(item.get("check_id", "NOT_COMPUTABLE")),
            "passed": bool(item.get("passed", False)),
        }
        for item in sorted(checks, key=lambda x: str(x.get("check_id", "NOT_COMPUTABLE")))
    ]


def build_temporal_continuity_operator_authorization_record_validation_dry_run(
    *,
    repo_root: str | Path = ".",
    source_validation_plan_path: str = SOURCE_VALIDATION_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_validation_plan_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_validation_plan_hash = "NOT_COMPUTABLE"
    source_validation_plan_status = "NOT_COMPUTABLE"
    status = "NOT_COMPUTABLE"
    recommended_next_lane = "P83_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN"
    blockers: list[str] = []

    executed_validation_checks: list[dict[str, Any]] = []
    operator_field_results: list[dict[str, Any]] = []
    authorization_field_results: list[dict[str, Any]] = []
    command_field_results: list[dict[str, Any]] = []
    provenance_field_results: list[dict[str, Any]] = []
    hash_field_results: list[dict[str, Any]] = []
    authority_invariant_results: list[dict[str, Any]] = []
    simulated_record_validation_result: dict[str, Any] = {
        "shape_valid": False,
        "validation_blockers": ["source_validation_plan_missing_or_unreadable"],
    }
    validation_passed = False
    validation_blockers: list[str] = []

    allowed_target_candidates: list[str] = []
    denied_target_candidates: list[str] = []
    allowed_command_candidates: list[str] = []
    denied_command_candidates: list[str] = []
    planned_authorization_scope: list[str] = []
    planned_expected_outputs: list[str] = []

    if source_payload is None:
        blockers = [
            "source_validation_plan_missing_or_unreadable",
            f"source_path:{source_validation_plan_path}",
        ]
    else:
        source_validation_plan_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_validation_plan_status = str(
            source_payload.get("validation_plan_status", "NOT_COMPUTABLE")
        )

        executed_validation_checks = _execute_check_results(
            _as_dict_list(source_payload.get("validation_checks"))
        )
        operator_field_results = _as_dict_list(source_payload.get("required_operator_field_checks"))
        authorization_field_results = _as_dict_list(source_payload.get("required_authorization_field_checks"))
        command_field_results = _as_dict_list(source_payload.get("required_command_field_checks"))
        provenance_field_results = _as_dict_list(source_payload.get("required_provenance_field_checks"))
        hash_field_results = _as_dict_list(source_payload.get("required_hash_field_checks"))
        authority_invariant_results = _as_dict_list(source_payload.get("authority_invariant_checks"))
        simulated_record_validation_result = dict(source_payload.get("simulated_record_validation", {}))

        allowed_target_candidates = sorted([str(i) for i in source_payload.get("allowed_target_candidates", [])])
        denied_target_candidates = sorted([str(i) for i in source_payload.get("denied_target_candidates", [])])
        allowed_command_candidates = sorted([str(i) for i in source_payload.get("allowed_command_candidates", [])])
        denied_command_candidates = sorted([str(i) for i in source_payload.get("denied_command_candidates", [])])
        planned_authorization_scope = sorted([str(i) for i in source_payload.get("planned_authorization_scope", [])])
        planned_expected_outputs = sorted([str(i) for i in source_payload.get("planned_expected_outputs", [])])

        if source_validation_plan_status != "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN_READY":
            status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN"
            blockers = [f"source_validation_plan_status:{source_validation_plan_status}"]
        else:
            group_presence = all(
                [
                    executed_validation_checks,
                    operator_field_results,
                    authorization_field_results,
                    command_field_results,
                    provenance_field_results,
                    hash_field_results,
                    authority_invariant_results,
                ]
            )
            checks_passed = all(item.get("passed", False) for item in executed_validation_checks)
            authority_passed = all(item.get("passed", False) for item in authority_invariant_results)
            simulated_shape_valid = bool(simulated_record_validation_result.get("shape_valid", False))
            invariants = {
                "simulated_only": source_payload.get("simulated_only") is True,
                "valid_for_execution": source_payload.get("valid_for_execution") is False,
                "authorization_granted": source_payload.get("authorization_granted") is False,
                "execution_authority": source_payload.get("execution_authority") is False,
                "token_minting_allowed": source_payload.get("token_minting_allowed") is False,
                "operator_approval_required": source_payload.get("operator_approval_required") is True,
            }
            invariants_passed = all(invariants.values())

            validation_passed = (
                group_presence
                and checks_passed
                and authority_passed
                and simulated_shape_valid
                and invariants_passed
            )

            if validation_passed:
                status = "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_DRY_RUN_READY"
                recommended_next_lane = "P85_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN"
            else:
                status = "VALIDATION_DRY_RUN_FAILED"
                validation_blockers = sorted(
                    [
                        *([] if group_presence else ["missing_validation_check_group"]),
                        *([] if checks_passed else ["planned_validation_check_failed"]),
                        *([] if authority_passed else ["authority_invariant_check_failed"]),
                        *([] if simulated_shape_valid else ["simulated_record_shape_invalid"]),
                        *([f"invariant_failed:{k}" for k, v in invariants.items() if not v]),
                    ]
                )

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "validation_dry_run_id": "temporal_continuity_operator_authorization_record_validation_dry_run_001",
        "source_validation_plan_path": source_validation_plan_path,
        "source_validation_plan_hash": source_validation_plan_hash,
        "validation_dry_run_status": status,
        "source_validation_plan_status": source_validation_plan_status,
        "executed_validation_checks": executed_validation_checks,
        "operator_field_results": operator_field_results,
        "authorization_field_results": authorization_field_results,
        "command_field_results": command_field_results,
        "provenance_field_results": provenance_field_results,
        "hash_field_results": hash_field_results,
        "authority_invariant_results": authority_invariant_results,
        "simulated_record_validation_result": simulated_record_validation_result,
        "validation_passed": validation_passed,
        "validation_blockers": validation_blockers,
        "allowed_target_candidates": allowed_target_candidates,
        "denied_target_candidates": denied_target_candidates,
        "allowed_command_candidates": allowed_command_candidates,
        "denied_command_candidates": denied_command_candidates,
        "planned_authorization_scope": planned_authorization_scope,
        "planned_expected_outputs": planned_expected_outputs,
        "recommended_next_lane": recommended_next_lane,
        "blockers": sorted(blockers),
        "advisory_only": True,
        "projection_only": True,
        "validation_dry_run_only": True,
        "validation_plan_only": False,
        "simulated_only": True,
        "authorization_granted": False,
        "execution_authority": False,
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "mutation_allowed": False,
        "forecast_authority": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "token_minting_allowed": False,
        "operator_approval_required": True,
        "valid_for_execution": False,
        "source_validation_plan_observed": source_observed,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_validation_dry_run(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
