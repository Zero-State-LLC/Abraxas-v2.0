from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.abx_harness_implementation_authorization_intake_gate import (
    DEFAULT_PAYLOAD_PATH,
    GATE_JSON_PATH as INTAKE_GATE_JSON_PATH,
    build_abx_harness_implementation_authorization_intake_gate,
)
from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxHarnessImplementationAuthorizationRecord.v1"
RECORD_ID = "abx_harness_implementation_authorization_record_001"
RECORD_JSON_PATH = Path(
    "out/operator_review/abx_harness_implementation_authorization_record_001.latest.json"
)
RECORD_MD_PATH = RECORD_JSON_PATH.with_suffix(".md")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _authority_locks(*, implementation_authorized: bool) -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "canon_promotion": False,
        "downstream_authority": False,
        "execution_authority": False,
        "github_writeback": False,
        "implementation_authority": implementation_authorized,
        "notion_writeback": False,
        "queue_mutation": False,
        "repair_execution": False,
        "runtime_mutation": False,
        "runtime_execution": False,
        "scheduler_mutation": False,
    }


def build_abx_harness_implementation_authorization_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    intake = build_abx_harness_implementation_authorization_intake_gate(root)
    payload = _read_json(root / DEFAULT_PAYLOAD_PATH) or {}
    intake_valid = intake.get("intake_validated_for_authorization_record") is True
    approved = intake_valid and payload.get("status") == "AUTHORIZED_RECORD"
    scope = payload.get("implementation_scope", {})
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record_id": RECORD_ID,
        "status": (
            "ABX_HARNESS_IMPLEMENTATION_AUTHORIZATION_RECORD_EMITTED"
            if approved
            else (
                "ABX_HARNESS_IMPLEMENTATION_AUTHORIZATION_RECORD_BLOCKED"
                if not intake_valid
                else "ABX_HARNESS_IMPLEMENTATION_AUTHORIZATION_HOLD_MAINTAINED"
            )
        ),
        "target_surface_id": payload.get("surface_id", NOT_COMPUTABLE)
        if intake_valid
        else NOT_COMPUTABLE,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "decision_value": payload.get("decision_value", NOT_COMPUTABLE)
        if intake_valid
        else NOT_COMPUTABLE,
        "implementation_scope": scope.get("scope_class", NOT_COMPUTABLE)
        if intake_valid
        else NOT_COMPUTABLE,
        "operator_id": payload.get("operator_id", NOT_COMPUTABLE)
        if intake_valid
        else NOT_COMPUTABLE,
        "operator_role": payload.get("operator_role", NOT_COMPUTABLE)
        if intake_valid
        else NOT_COMPUTABLE,
        "decision_date": payload.get("decision_date", NOT_COMPUTABLE)
        if intake_valid
        else NOT_COMPUTABLE,
        "implementation_authorized": approved,
        "implementation_may_proceed": scope.get("implementation_may_proceed", False)
        if intake_valid
        else False,
        "execution_authority": False,
        "runtime_execution_allowed": False,
        "repair_execution_allowed": False,
        "canon_promotion_allowed": False,
        "scheduler_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "downstream_authority_granted": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_implementation_pr": approved,
        "authority_locks": _authority_locks(implementation_authorized=approved),
        "source_intake_gate_path": INTAKE_GATE_JSON_PATH.as_posix(),
        "source_intake_gate_hash": str(intake.get("gate_hash", NOT_COMPUTABLE)),
        "authorization_class": (
            payload.get("seal", {}).get("authorization_class", NOT_COMPUTABLE)
            if intake_valid
            else NOT_COMPUTABLE
        ),
        "execution_status": (
            payload.get("seal", {}).get("execution_status", NOT_COMPUTABLE)
            if intake_valid
            else NOT_COMPUTABLE
        ),
        "decision_outcome_summary": (
            "Operator authorized ABX Harness Phase 1 implementation within approved "
            "repo-visible scope; execution, runtime, canon promotion, and downstream "
            "authority remain denied."
            if approved
            else NOT_COMPUTABLE
        ),
        "recommended_next_action": (
            "implement core/codegen_shadow_replay_harness.py under advisory-only posture"
            if approved
            else "collect valid operator authorization intake"
        ),
        "recommended_next_patch": NOT_COMPUTABLE,
        "record_hash": "",
    }
    packet["record_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "record_hash"}
    )
    return packet


def write_abx_harness_implementation_authorization_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_harness_implementation_authorization_record(root)
    write_canonical_json(target_root / RECORD_JSON_PATH, packet)
    target_root.joinpath(RECORD_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    target_root.joinpath(RECORD_MD_PATH).write_text(
        f"# ABX Harness Implementation Authorization Record\n\n- status: {packet['status']}\n",
        encoding="utf-8",
    )
    return packet
