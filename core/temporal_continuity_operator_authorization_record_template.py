from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordTemplate.v1"
SOURCE_AUTHORIZATION_RECORD_PLAN_PATH = (
    "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "template_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def build_temporal_continuity_operator_authorization_record_template(
    *,
    repo_root: str | Path = ".",
    source_authorization_record_plan_path: str = SOURCE_AUTHORIZATION_RECORD_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_authorization_record_plan_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    required_operator_fields = ["operator_id", "operator_name", "operator_approval_timestamp", "operator_approval_signature"]
    required_authorization_fields = ["authorization_scope", "authorization_granted", "authorization_authority", "authorization_record_creation_authority", "execution_authority"]
    required_command_fields = ["authorized_commands", "authorized_expected_outputs", "command_hashes"]
    required_provenance_fields = ["source_authorization_record_plan_path", "source_authorization_record_plan_hash", "source_authorization_record_plan_status"]
    required_hash_fields = ["template_hash", "record_hash", "source_authorization_record_plan_hash"]
    allowed_target_candidates = ["out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json"]
    denied_target_candidates = ["canon://*", "runtime://*", "queue://*", "forecast://*"]
    allowed_command_candidates = ["python scripts/run_temporal_continuity_upstream_input_regeneration_execution_plan.py"]
    denied_command_candidates = ["rm *", "python -c 'mutate canon'", "runtime_execute"]

    template_status = "NOT_COMPUTABLE"
    next_lane = "P80_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_RECORD_PLAN"
    blockers: list[str] = []
    source_hash = "NOT_COMPUTABLE"
    source_plan_status = "NOT_COMPUTABLE"

    if source_payload is None:
        blockers = [
            "source_authorization_record_plan_missing_or_unreadable",
            f"source_path:{source_authorization_record_plan_path}",
        ]
    else:
        source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_plan_status = str(source_payload.get("authorization_record_plan_status", "NOT_COMPUTABLE"))
        if source_plan_status == "AUTHORIZATION_RECORD_PLAN_READY":
            template_status = "OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_READY"
            next_lane = "P82_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_DRY_RUN"
        else:
            template_status = "BLOCKED_BY_AUTHORIZATION_RECORD_PLAN"
            blockers = [f"source_authorization_record_plan_status:{source_plan_status}"]

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "template_id": "temporal_continuity_operator_authorization_record_template_001",
        "source_authorization_record_plan_path": source_authorization_record_plan_path,
        "source_authorization_record_plan_hash": source_hash,
        "source_authorization_record_plan_status": source_plan_status,
        "source_authorization_record_plan_observed": source_observed,
        "template_status": template_status,
        "required_operator_fields": sorted(required_operator_fields),
        "required_authorization_fields": sorted(required_authorization_fields),
        "required_command_fields": sorted(required_command_fields),
        "required_provenance_fields": sorted(required_provenance_fields),
        "required_hash_fields": sorted(required_hash_fields),
        "allowed_target_candidates": sorted(allowed_target_candidates),
        "denied_target_candidates": sorted(denied_target_candidates),
        "allowed_command_candidates": sorted(allowed_command_candidates),
        "denied_command_candidates": sorted(denied_command_candidates),
        "planned_authorization_scope": ["upstream_input_regeneration_authorization_record_creation_only"],
        "planned_expected_outputs": sorted(allowed_target_candidates),
        "operator_approval_requirements": [
            "explicit_operator_approval_required",
            "no_autonomous_authorization",
            "authorization_record_must_be_human_attested",
        ],
        "record_creation_requirements": [
            "future_lane_only",
            "no_token_minting_in_p81",
            "execution_authority_must_remain_false",
            "authorization_granted_must_remain_false_until_future_lane",
        ],
        "recommended_next_lane": next_lane,
        "blockers": sorted(blockers),
        "advisory_only": True,
        "projection_only": True,
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
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_template(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
