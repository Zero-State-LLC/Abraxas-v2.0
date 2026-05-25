from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordValidationPlan.v1"
SOURCE_DRY_RUN_PATH = "out/temporal_continuity_operator_authorization_record_dry_run/latest.json"


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "validation_plan_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _field_checks(group: str, values: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "check_id": f"{group}_{idx:03d}",
            "field": field,
            "present": bool(field),
        }
        for idx, field in enumerate(sorted(values), start=1)
    ]


def _authority_invariant_checks(source: dict[str, Any]) -> list[dict[str, Any]]:
    checks = [
        ("simulated_only", True),
        ("authorization_granted", False),
        ("execution_authority", False),
        ("token_minting_allowed", False),
        ("valid_for_execution", False),
        ("operator_approval_required", True),
    ]
    return [
        {
            "check_id": f"authority_{name}",
            "field": name,
            "expected": expected,
            "observed": source.get(name),
            "passed": source.get(name) == expected,
        }
        for name, expected in checks
    ]


def build_temporal_continuity_operator_authorization_record_validation_plan(
    *,
    repo_root: str | Path = ".",
    source_dry_run_path: str = SOURCE_DRY_RUN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_dry_run_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_dry_run_hash = "NOT_COMPUTABLE"
    source_dry_run_status = "NOT_COMPUTABLE"
    status = "NOT_COMPUTABLE"
    recommended_next_lane = "P82_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_DRY_RUN"
    blockers: list[str] = []

    required_operator_fields: list[str] = []
    required_authorization_fields: list[str] = []
    required_command_fields: list[str] = []
    required_provenance_fields: list[str] = []
    required_hash_fields: list[str] = []
    allowed_target_candidates: list[str] = []
    denied_target_candidates: list[str] = []
    allowed_command_candidates: list[str] = []
    denied_command_candidates: list[str] = []
    planned_authorization_scope: list[str] = []
    planned_expected_outputs: list[str] = []
    simulated_record_validation: dict[str, Any] = {
        "shape_valid": False,
        "validation_blockers": ["source_dry_run_missing_or_unreadable"],
    }

    if source_payload is None:
        blockers = ["source_dry_run_missing_or_unreadable", f"source_path:{source_dry_run_path}"]
    else:
        source_dry_run_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_dry_run_status = str(source_payload.get("dry_run_status", "NOT_COMPUTABLE"))

        required_operator_fields = sorted([str(i) for i in source_payload.get("required_operator_fields", [])])
        required_authorization_fields = sorted([str(i) for i in source_payload.get("required_authorization_fields", [])])
        required_command_fields = sorted([str(i) for i in source_payload.get("required_command_fields", [])])
        required_provenance_fields = sorted([str(i) for i in source_payload.get("required_provenance_fields", [])])
        required_hash_fields = sorted([str(i) for i in source_payload.get("required_hash_fields", [])])
        allowed_target_candidates = sorted([str(i) for i in source_payload.get("allowed_target_candidates", [])])
        denied_target_candidates = sorted([str(i) for i in source_payload.get("denied_target_candidates", [])])
        allowed_command_candidates = sorted([str(i) for i in source_payload.get("allowed_command_candidates", [])])
        denied_command_candidates = sorted([str(i) for i in source_payload.get("denied_command_candidates", [])])
        planned_authorization_scope = sorted([str(i) for i in source_payload.get("planned_authorization_scope", [])])
        planned_expected_outputs = sorted([str(i) for i in source_payload.get("planned_expected_outputs", [])])
        simulated_record_validation = dict(source_payload.get("simulated_record_validation", {}))

        if source_dry_run_status != "OPERATOR_AUTHORIZATION_RECORD_DRY_RUN_READY":
            status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_DRY_RUN"
            blockers = [f"source_dry_run_status:{source_dry_run_status}"]
        else:
            authority_checks = _authority_invariant_checks(source_payload)
            invariant_failures = [c["check_id"] for c in authority_checks if not c["passed"]]
            shape_valid = bool(simulated_record_validation.get("shape_valid", False))
            source_has_hash_path = source_dry_run_hash != "NOT_COMPUTABLE" and bool(source_dry_run_path)
            required_groups_ok = all(
                [
                    required_operator_fields,
                    required_authorization_fields,
                    required_command_fields,
                    required_provenance_fields,
                    required_hash_fields,
                ]
            )
            if invariant_failures or (not shape_valid) or (not source_has_hash_path) or (not required_groups_ok):
                status = "VALIDATION_PLAN_BLOCKED_BY_SIMULATED_RECORD"
                blockers = sorted(
                    [
                        *invariant_failures,
                        *(["simulated_record_shape_invalid"] if not shape_valid else []),
                        *(["source_hash_or_path_missing"] if not source_has_hash_path else []),
                        *(["required_field_group_missing"] if not required_groups_ok else []),
                    ]
                )
            else:
                status = "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN_READY"
                recommended_next_lane = "P84_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_VALIDATION_DRY_RUN"

    validation_checks = [
        {"check_id": "check_operator_fields_present", "passed": bool(required_operator_fields)},
        {"check_id": "check_authorization_fields_present", "passed": bool(required_authorization_fields)},
        {"check_id": "check_command_fields_present", "passed": bool(required_command_fields)},
        {"check_id": "check_provenance_fields_present", "passed": bool(required_provenance_fields)},
        {"check_id": "check_hash_fields_present", "passed": bool(required_hash_fields)},
        {"check_id": "check_source_hash_path_present", "passed": source_dry_run_hash != "NOT_COMPUTABLE" and bool(source_dry_run_path)},
        {"check_id": "check_simulated_record_exists", "passed": isinstance(source_payload, dict) and isinstance(source_payload.get("simulated_authorization_record"), dict) if source_payload else False},
    ]
    required_operator_field_checks = _field_checks("operator_field", required_operator_fields)
    required_authorization_field_checks = _field_checks("authorization_field", required_authorization_fields)
    required_command_field_checks = _field_checks("command_field", required_command_fields)
    required_provenance_field_checks = _field_checks("provenance_field", required_provenance_fields)
    required_hash_field_checks = _field_checks("hash_field", required_hash_fields)
    authority_invariant_checks = _authority_invariant_checks(source_payload or {})

    validation_blockers = sorted(
        list(
            {
                *(["missing_required_operator_fields"] if not required_operator_fields else []),
                *(["missing_required_authorization_fields"] if not required_authorization_fields else []),
                *(["missing_required_command_fields"] if not required_command_fields else []),
                *(["missing_required_provenance_fields"] if not required_provenance_fields else []),
                *(["missing_required_hash_fields"] if not required_hash_fields else []),
                *(["simulated_record_validation_not_shape_valid"] if not bool(simulated_record_validation.get("shape_valid", False)) else []),
                *[c["check_id"] for c in authority_invariant_checks if not c["passed"]],
            }
        )
    )

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "validation_plan_id": "temporal_continuity_operator_authorization_record_validation_plan_001",
        "source_dry_run_path": source_dry_run_path,
        "source_dry_run_hash": source_dry_run_hash,
        "source_dry_run_observed": source_observed,
        "validation_plan_status": status,
        "source_dry_run_status": source_dry_run_status,
        "validation_checks": validation_checks,
        "required_operator_field_checks": required_operator_field_checks,
        "required_authorization_field_checks": required_authorization_field_checks,
        "required_command_field_checks": required_command_field_checks,
        "required_provenance_field_checks": required_provenance_field_checks,
        "required_hash_field_checks": required_hash_field_checks,
        "authority_invariant_checks": authority_invariant_checks,
        "simulated_record_validation": simulated_record_validation,
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
        "validation_plan_only": True,
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
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_validation_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
