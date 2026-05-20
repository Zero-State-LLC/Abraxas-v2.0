from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityUpstreamInputRegenerationAuthorizationRecordPlan.v1"
SOURCE_AUTHORIZATION_GATE_PATH = (
    "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json"
)

_AUTHORIZATION_RECORD_PLAN_STATUSES = (
    "NOT_COMPUTABLE",
    "AUTHORIZATION_RECORD_PLAN_READY",
    "AUTHORIZATION_RECORD_PLAN_BLOCKED",
    "AUTHORIZATION_RECORD_NOT_REQUIRED",
)

_DENIED_AUTHORITY = (
    "production_activation",
    "canon_promotion",
    "forecast_influence",
    "scheduler_mutation",
    "runtime_authority",
    "repair_authority",
    "evidence_generation_authority",
    "restoration_execution_authority",
    "generator_execution_authority",
    "upstream_input_generation_authority",
    "artifact_regeneration_authority",
    "execution_authority",
    "authorization_authority",
    "authorization_record_creation_authority",
    "spine_implementation_authority",
)

_FUTURE_ARTIFACT_DRY_RUN_LANES = frozenset(
    {
        "P79_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN",
        "P80_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN",
        "P81_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN",
    }
)
_FUTURE_SPINE_GATE_LANES = frozenset(
    {
        "P79_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
        "P80_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
        "P81_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
    }
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _command_hash(command: str) -> str:
    return hashlib.sha256(command.encode("utf-8")).hexdigest()


def _planned_authorization_record(
    *,
    authorization_scope: list[str],
    authorized_commands: list[str],
    authorized_expected_outputs: list[str],
    source_authorization_gate_hash: str,
    source_authorization_gate_path: str,
) -> dict[str, Any]:
    return {
        "artifact_type": "OperatorAuthorizationToken.v1",
        "authorization_scope": sorted(authorization_scope),
        "authorized_commands": sorted(authorized_commands),
        "authorized_expected_outputs": sorted(authorized_expected_outputs),
        "source_authorization_gate_hash": source_authorization_gate_hash,
        "source_authorization_gate_path": source_authorization_gate_path,
        "operator_approval_required": True,
        "operator_approved": False,
        "authorization_granted": False,
        "execution_authority": False,
        "authorization_created_by": "NOT_CREATED_BY_P80",
        "authorization_created_at": "NOT_CREATED_BY_P80",
        "expiration_policy": {
            "policy_type": "OPERATOR_DEFINED",
            "expiration_required": True,
            "default_expiry": "NOT_SET_BY_P80",
            "note": "Expiration policy must be explicitly set by the operator in the future authorization lane.",
        },
        "revocation_policy": {
            "policy_type": "OPERATOR_DEFINED",
            "revocation_required": True,
            "revocable": True,
            "note": "Token must be revocable. Revocation policy must be explicitly defined in the future authorization lane.",
        },
        "validation_requirements": [
            {
                "requirement_id": "token_validation_001_source_gate_hash",
                "requirement": "Token must include and validate the source_authorization_gate_hash from P79.",
            },
            {
                "requirement_id": "token_validation_002_command_match",
                "requirement": "Token authorized_commands must exactly match the P79 eligible command allowlist.",
            },
            {
                "requirement_id": "token_validation_003_output_match",
                "requirement": "Token authorized_expected_outputs must exactly match the P79 eligible expected output paths.",
            },
            {
                "requirement_id": "token_validation_004_canonical_json",
                "requirement": "Token must be deterministic canonical JSON with sorted keys and packet_hash.",
            },
            {
                "requirement_id": "token_validation_005_execution_authority_denied",
                "requirement": "Token execution_authority must remain false unless a separate explicitly authorized execution lane grants it.",
            },
        ],
        "packet_hash_required": True,
    }


def _empty_planned_authorization_record(*, source_gate_path: str) -> dict[str, Any]:
    return _planned_authorization_record(
        authorization_scope=[],
        authorized_commands=[],
        authorized_expected_outputs=[],
        source_authorization_gate_hash="NOT_COMPUTABLE",
        source_authorization_gate_path=source_gate_path,
    )


def _operator_approval_requirements(
    *,
    authorization_scope: list[str],
    authorized_command_candidates: list[str],
    authorized_expected_output_candidates: list[str],
) -> list[dict[str, Any]]:
    requirements = [
        {
            "requirement_id": "approval_001_explicit_operator_approval",
            "requirement_type": "explicit_operator_approval",
            "requirement": "Explicit human/operator approval is required; no autonomous approval is permitted.",
        },
        {
            "requirement_id": "approval_002_command_review",
            "requirement_type": "command_review",
            "commands": sorted(authorized_command_candidates),
            "requirement": "Operator must explicitly review and approve each authorized command candidate.",
        },
        {
            "requirement_id": "approval_003_output_path_review",
            "requirement_type": "output_path_review",
            "expected_outputs": sorted(authorized_expected_output_candidates),
            "requirement": "Operator must explicitly review and approve each authorized expected output path.",
        },
        {
            "requirement_id": "approval_004_scope_review",
            "requirement_type": "scope_review",
            "scope_paths": sorted(authorization_scope),
            "requirement": "Operator must review the full authorization scope matching eligible execution step input paths.",
        },
        {
            "requirement_id": "approval_005_source_hash_review",
            "requirement_type": "source_hash_review",
            "requirement": "Operator must verify the source_authorization_gate_hash matches the P79 artifact on disk.",
        },
        {
            "requirement_id": "approval_006_expiration_policy_review",
            "requirement_type": "expiration_policy_review",
            "requirement": "Operator must explicitly define and approve the expiration policy for the authorization token.",
        },
        {
            "requirement_id": "approval_007_revocation_policy_review",
            "requirement_type": "revocation_policy_review",
            "requirement": "Operator must explicitly define and approve the revocation policy for the authorization token.",
        },
        {
            "requirement_id": "approval_008_no_op_rollback_review",
            "requirement_type": "no_op_rollback_review",
            "requirement": "Operator must confirm no-op rollback posture remains in place until a future execution lane explicitly permits execution.",
        },
        {
            "requirement_id": "approval_009_post_run_validation_review",
            "requirement_type": "post_run_validation_review",
            "requirement": "Operator must review all post-run validation requirements before any future authorization token is issued.",
        },
        {
            "requirement_id": "approval_010_authority_denial_confirmation",
            "requirement_type": "authority_denial_confirmation",
            "requirement": "Operator must explicitly confirm all authority-denial defaults (execution_authority=false, authorization_authority=false, etc.) are preserved in any issued token.",
        },
    ]
    return sorted(requirements, key=lambda item: str(item["requirement_id"]))


def _token_creation_requirements() -> list[dict[str, Any]]:
    return [
        {
            "requirement_id": "token_req_001_future_lane_only",
            "requirement_type": "future_lane_only",
            "requirement": "Token creation is future-lane only. P80 does not create any authorization token or authorization record.",
        },
        {
            "requirement_id": "token_req_002_source_gate_hash",
            "requirement_type": "source_gate_hash_required",
            "requirement": "Token must include source_authorization_gate_hash from P79 at the time of creation.",
        },
        {
            "requirement_id": "token_req_003_authorized_commands",
            "requirement_type": "authorized_commands_required",
            "requirement": "Token must include the complete list of authorized_commands matching P79 eligible commands exactly.",
        },
        {
            "requirement_id": "token_req_004_authorized_expected_outputs",
            "requirement_type": "authorized_expected_outputs_required",
            "requirement": "Token must include authorized_expected_outputs matching P79 eligible command output paths exactly.",
        },
        {
            "requirement_id": "token_req_005_execution_authority_locked_false",
            "requirement_type": "execution_authority_locked_false",
            "requirement": "Token must keep execution_authority=false unless a separate explicitly authorized execution lane exists and has been separately approved.",
        },
        {
            "requirement_id": "token_req_006_revocable",
            "requirement_type": "revocable_required",
            "requirement": "Token must be revocable. Revocation mechanism must be defined in the future authorization lane.",
        },
        {
            "requirement_id": "token_req_007_canonical_json_with_packet_hash",
            "requirement_type": "canonical_json_required",
            "requirement": "Token must be deterministic canonical JSON with sorted keys, final newline, and a stable packet_hash.",
        },
        {
            "requirement_id": "token_req_008_not_generated_by_p80",
            "requirement_type": "not_generated_by_p80",
            "requirement": "P80 must not generate the token. Token generation is reserved for a future explicitly authorized operator lane.",
        },
    ]


def _provenance_bindings(
    *,
    source_gate_path: str,
    source_gate_hash: str,
    eligible_step_ids: list[str],
    eligible_commands: list[str],
    expected_output_paths: list[str],
    degraded_evidence_count: int,
    blocker_count: int,
    drift_flag_count: int,
) -> dict[str, Any]:
    return {
        "source_authorization_gate_path": source_gate_path,
        "source_authorization_gate_hash": source_gate_hash,
        "eligible_step_ids": sorted(eligible_step_ids),
        "eligible_command_hashes": sorted(
            [_command_hash(cmd) for cmd in eligible_commands]
        ),
        "expected_output_paths": sorted(expected_output_paths),
        "inherited_degraded_evidence_count": degraded_evidence_count,
        "inherited_blocker_count": blocker_count,
        "inherited_drift_flag_count": drift_flag_count,
    }


def _build_status_and_recommendation(
    *,
    gate_status: str,
    authorization_required: bool,
    degraded_evidence_inputs: list[str],
    source_recommended_next_lane: str,
) -> tuple[str, bool, bool, str, str]:
    """Return (plan_status, record_required, record_creation_allowed, next_lane, reason)."""
    if gate_status == "AUTHORIZATION_ELIGIBLE" and authorization_required:
        return (
            "AUTHORIZATION_RECORD_PLAN_READY",
            True,
            False,
            "P81_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE",
            "P79 is AUTHORIZATION_ELIGIBLE and requires an authorization record; P80 defines the planned shape for the future operator authorization record.",
        )

    if gate_status == "AUTHORIZATION_BLOCKED":
        return (
            "AUTHORIZATION_RECORD_PLAN_BLOCKED",
            False,
            False,
            "P81_TEMPORAL_CONTINUITY_AUTHORIZATION_BLOCKER_REPAIR_PLAN",
            "P79 reported AUTHORIZATION_BLOCKED; authorization record planning is blocked until blockers are repaired.",
        )

    if gate_status == "AUTHORIZATION_NOT_REQUIRED":
        if degraded_evidence_inputs:
            return (
                "AUTHORIZATION_RECORD_NOT_REQUIRED",
                False,
                False,
                "P81_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN",
                "Authorization is not required, but degraded evidence remains and must be repaired before advancing.",
            )
        if source_recommended_next_lane in _FUTURE_ARTIFACT_DRY_RUN_LANES:
            return (
                "AUTHORIZATION_RECORD_NOT_REQUIRED",
                False,
                False,
                "P81_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN",
                "Authorization is not required; P79 source routes to artifact regeneration dry-run planning.",
            )
        if source_recommended_next_lane in _FUTURE_SPINE_GATE_LANES:
            return (
                "AUTHORIZATION_RECORD_NOT_REQUIRED",
                False,
                False,
                "P81_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
                "Authorization is not required and no degraded evidence remains; routing to spine implementation planning gate.",
            )
        return (
            "NOT_COMPUTABLE",
            False,
            False,
            "P79_AUTHORIZATION_GATE_REGENERATION",
            "P79 reported AUTHORIZATION_NOT_REQUIRED but its source recommended next lane is inconsistent; regenerate P79 before P80.",
        )

    return (
        "NOT_COMPUTABLE",
        False,
        False,
        "P79_AUTHORIZATION_GATE_REGENERATION",
        "P79 authorization gate status is missing or inconsistent; regenerate P79 before P80 authorization record planning.",
    )


def _not_computable_packet(
    *, source_path: str, source_observed: bool
) -> dict[str, Any]:
    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_record_plan_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "evidence_generation_authority": False,
        "restoration_execution_authority": False,
        "generator_execution_authority": False,
        "upstream_input_generation_authority": False,
        "artifact_regeneration_authority": False,
        "execution_authority": False,
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "spine_implementation_authority": False,
        "source_authorization_gate_path": source_path,
        "source_authorization_gate_observed": source_observed,
        "source_authorization_gate_hash": "NOT_COMPUTABLE",
        "source_authorization_gate_status": "NOT_COMPUTABLE",
        "source_recommended_next_lane": "NOT_COMPUTABLE",
        "authorization_record_plan_status": "NOT_COMPUTABLE",
        "authorization_record_required": False,
        "authorization_record_creation_allowed": False,
        "operator_approved": False,
        "authorization_granted": False,
        "planned_authorization_record": _empty_planned_authorization_record(
            source_gate_path=source_path
        ),
        "authorization_scope": [],
        "authorized_command_candidates": [],
        "authorized_expected_output_candidates": [],
        "provenance_bindings": _provenance_bindings(
            source_gate_path=source_path,
            source_gate_hash="NOT_COMPUTABLE",
            eligible_step_ids=[],
            eligible_commands=[],
            expected_output_paths=[],
            degraded_evidence_count=0,
            blocker_count=0,
            drift_flag_count=0,
        ),
        "operator_approval_requirements": _operator_approval_requirements(
            authorization_scope=[],
            authorized_command_candidates=[],
            authorized_expected_output_candidates=[],
        ),
        "token_creation_requirements": _token_creation_requirements(),
        "blocked_authorization_reasons": [
            f"source_authorization_gate_not_computable:{source_path}"
        ],
        "degraded_evidence_inputs": [],
        "inherited_blockers": [f"source_authorization_gate_not_computable:{source_path}"],
        "inherited_drift_flags": ["SOURCE_AUTHORIZATION_GATE_NOT_COMPUTABLE"],
        "semantic_overlap_flags": [],
        "authorization_record_strategy_summary": {
            "source_gate_status": "NOT_COMPUTABLE",
            "authorization_scope_count": 0,
            "authorized_command_candidates_count": 0,
            "authorized_expected_output_candidates_count": 0,
            "provenance_bindings_count": 0,
            "operator_approval_requirements_count": 10,
            "token_creation_requirements_count": 8,
            "blocked_authorization_reasons_count": 1,
            "authorization_record_required": False,
            "authorization_record_creation_allowed": False,
        },
        "recommended_next_lane": "P79_AUTHORIZATION_GATE_REGENERATION",
        "recommended_next_lane_reason": (
            "P79 authorization gate is missing, unreadable, or malformed; regenerate P79 before P80 authorization record planning."
        ),
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
    *,
    repo_root: str | Path = ".",
    source_authorization_gate_path: str = SOURCE_AUTHORIZATION_GATE_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_authorization_gate_path
    source_observed = source_path.exists()

    source_payload = _load_json_dict(source_path)
    if source_payload is None:
        return _not_computable_packet(
            source_path=source_authorization_gate_path,
            source_observed=source_observed,
        )

    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    gate_status = str(source_payload.get("authorization_gate_status", "NOT_COMPUTABLE"))
    source_recommended_next_lane = str(
        source_payload.get("source_recommended_next_lane", "NOT_COMPUTABLE")
    )

    degraded_evidence_inputs = _as_str_list(source_payload.get("degraded_evidence_inputs"))
    inherited_blockers = _as_str_list(source_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(source_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(source_payload.get("semantic_overlap_flags"))

    authorization_required_record = source_payload.get("authorization_required_record", {})
    authorization_required = bool(
        isinstance(authorization_required_record, dict)
        and authorization_required_record.get("required", False)
    )

    eligible_execution_steps = _as_dict_list(source_payload.get("eligible_execution_steps"))
    eligible_commands_raw = _as_dict_list(source_payload.get("eligible_commands"))

    authorization_scope = sorted(
        {str(step.get("target_input_path", "NOT_COMPUTABLE")) for step in eligible_execution_steps}
    ) if gate_status == "AUTHORIZATION_ELIGIBLE" else []

    authorized_command_candidates = sorted(
        [str(cmd.get("command", "NOT_COMPUTABLE")) for cmd in eligible_commands_raw]
    ) if gate_status == "AUTHORIZATION_ELIGIBLE" else []

    authorized_expected_output_candidates = sorted(
        [str(cmd.get("expected_output_path", "NOT_COMPUTABLE")) for cmd in eligible_commands_raw]
    ) if gate_status == "AUTHORIZATION_ELIGIBLE" else []

    eligible_step_ids = sorted(
        [str(step.get("step_id", "NOT_COMPUTABLE")) for step in eligible_execution_steps]
    ) if gate_status == "AUTHORIZATION_ELIGIBLE" else []

    (
        plan_status,
        record_required,
        record_creation_allowed,
        recommended_next_lane,
        recommended_next_lane_reason,
    ) = _build_status_and_recommendation(
        gate_status=gate_status,
        authorization_required=authorization_required,
        degraded_evidence_inputs=degraded_evidence_inputs,
        source_recommended_next_lane=source_recommended_next_lane,
    )

    planned_record = _planned_authorization_record(
        authorization_scope=authorization_scope,
        authorized_commands=authorized_command_candidates,
        authorized_expected_outputs=authorized_expected_output_candidates,
        source_authorization_gate_hash=source_hash,
        source_authorization_gate_path=source_authorization_gate_path,
    )

    prov_bindings = _provenance_bindings(
        source_gate_path=source_authorization_gate_path,
        source_gate_hash=source_hash,
        eligible_step_ids=eligible_step_ids,
        eligible_commands=authorized_command_candidates,
        expected_output_paths=authorized_expected_output_candidates,
        degraded_evidence_count=len(degraded_evidence_inputs),
        blocker_count=len(inherited_blockers),
        drift_flag_count=len(inherited_drift_flags),
    )

    approval_requirements = _operator_approval_requirements(
        authorization_scope=authorization_scope,
        authorized_command_candidates=authorized_command_candidates,
        authorized_expected_output_candidates=authorized_expected_output_candidates,
    )

    token_requirements = _token_creation_requirements()

    blocked_reasons: list[str] = []
    if plan_status in ("NOT_COMPUTABLE", "AUTHORIZATION_RECORD_PLAN_BLOCKED"):
        blocked_reasons = sorted(
            list(
                {
                    f"source_authorization_gate_status:{gate_status}",
                    *[f"inherited_blocker:{b}" for b in inherited_blockers],
                }
            )
        )

    strategy_summary = {
        "source_gate_status": gate_status,
        "authorization_scope_count": len(authorization_scope),
        "authorized_command_candidates_count": len(authorized_command_candidates),
        "authorized_expected_output_candidates_count": len(
            authorized_expected_output_candidates
        ),
        "provenance_bindings_count": len(prov_bindings),
        "operator_approval_requirements_count": len(approval_requirements),
        "token_creation_requirements_count": len(token_requirements),
        "blocked_authorization_reasons_count": len(blocked_reasons),
        "authorization_record_required": record_required,
        "authorization_record_creation_allowed": record_creation_allowed,
    }

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_record_plan_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "evidence_generation_authority": False,
        "restoration_execution_authority": False,
        "generator_execution_authority": False,
        "upstream_input_generation_authority": False,
        "artifact_regeneration_authority": False,
        "execution_authority": False,
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "spine_implementation_authority": False,
        "source_authorization_gate_path": source_authorization_gate_path,
        "source_authorization_gate_observed": source_observed,
        "source_authorization_gate_hash": source_hash,
        "source_authorization_gate_status": (
            gate_status
            if gate_status in (
                "NOT_COMPUTABLE",
                "AUTHORIZATION_BLOCKED",
                "AUTHORIZATION_ELIGIBLE",
                "AUTHORIZATION_NOT_REQUIRED",
            )
            else "NOT_COMPUTABLE"
        ),
        "source_recommended_next_lane": source_recommended_next_lane,
        "authorization_record_plan_status": (
            plan_status
            if plan_status in _AUTHORIZATION_RECORD_PLAN_STATUSES
            else "NOT_COMPUTABLE"
        ),
        "authorization_record_required": record_required,
        "authorization_record_creation_allowed": record_creation_allowed,
        "operator_approved": False,
        "authorization_granted": False,
        "planned_authorization_record": planned_record,
        "authorization_scope": authorization_scope,
        "authorized_command_candidates": authorized_command_candidates,
        "authorized_expected_output_candidates": authorized_expected_output_candidates,
        "provenance_bindings": prov_bindings,
        "operator_approval_requirements": approval_requirements,
        "token_creation_requirements": token_requirements,
        "blocked_authorization_reasons": blocked_reasons,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "authorization_record_strategy_summary": strategy_summary,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def write_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
