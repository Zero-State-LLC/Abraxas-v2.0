from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordDryRun.v1"
SOURCE_TEMPLATE_PATH = "out/temporal_continuity_operator_authorization_record_template/latest.json"


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "dry_run_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def build_temporal_continuity_operator_authorization_record_dry_run(
    *,
    repo_root: str | Path = ".",
    source_template_path: str = SOURCE_TEMPLATE_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_template_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    dry_run_status = "NOT_COMPUTABLE"
    recommended_next_lane = "P81_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE"
    source_template_hash = "NOT_COMPUTABLE"
    source_template_status = "NOT_COMPUTABLE"
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

    if source_payload is None:
        blockers = [
            "source_template_missing_or_unreadable",
            f"source_path:{source_template_path}",
        ]
    else:
        source_template_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_template_status = str(source_payload.get("template_status", "NOT_COMPUTABLE"))

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

        if source_template_status == "OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_READY":
            dry_run_status = "OPERATOR_AUTHORIZATION_RECORD_DRY_RUN_READY"
            recommended_next_lane = "P83_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN"
        else:
            dry_run_status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE"
            blockers = [f"source_template_status:{source_template_status}"]

    simulated_authorization_record = {
        "artifact_type": "OperatorAuthorizationRecord.v1.simulated",
        "simulated_only": True,
        "valid_for_execution": False,
        "authorization_granted": False,
        "execution_authority": False,
        "token_minting_allowed": False,
        "record_creation_authority": False,
        "required_operator_fields": required_operator_fields,
        "required_authorization_fields": required_authorization_fields,
        "required_command_fields": required_command_fields,
        "required_provenance_fields": required_provenance_fields,
        "required_hash_fields": required_hash_fields,
        "planned_authorization_scope": planned_authorization_scope,
        "planned_expected_outputs": planned_expected_outputs,
    }

    validation_blockers = sorted(
        list(
            {
                *([] if required_operator_fields else ["missing_required_operator_fields"]),
                *([] if required_authorization_fields else ["missing_required_authorization_fields"]),
                *([] if required_command_fields else ["missing_required_command_fields"]),
                *([] if required_provenance_fields else ["missing_required_provenance_fields"]),
                *([] if required_hash_fields else ["missing_required_hash_fields"]),
            }
        )
    )

    simulated_record_validation = {
        "shape_valid": len(validation_blockers) == 0,
        "validation_blockers": validation_blockers,
        "authorization_granted": False,
        "execution_authority": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
    }

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "dry_run_id": "temporal_continuity_operator_authorization_record_dry_run_001",
        "source_template_path": source_template_path,
        "source_template_hash": source_template_hash,
        "source_template_status": source_template_status,
        "source_template_observed": source_observed,
        "dry_run_status": dry_run_status,
        "simulated_authorization_record": simulated_authorization_record,
        "simulated_record_validation": simulated_record_validation,
        "required_operator_fields": required_operator_fields,
        "required_authorization_fields": required_authorization_fields,
        "required_command_fields": required_command_fields,
        "required_provenance_fields": required_provenance_fields,
        "required_hash_fields": required_hash_fields,
        "allowed_target_candidates": allowed_target_candidates,
        "denied_target_candidates": denied_target_candidates,
        "allowed_command_candidates": allowed_command_candidates,
        "denied_command_candidates": denied_command_candidates,
        "planned_authorization_scope": planned_authorization_scope,
        "planned_expected_outputs": planned_expected_outputs,
        "validation_blockers": validation_blockers,
        "recommended_next_lane": recommended_next_lane,
        "blockers": sorted(blockers),
        "advisory_only": True,
        "projection_only": True,
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


def write_temporal_continuity_operator_authorization_record_dry_run(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
