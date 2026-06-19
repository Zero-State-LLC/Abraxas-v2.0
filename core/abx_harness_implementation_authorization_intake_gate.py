from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_shadow_replay_harness_implementation_authorization_gate import (
    OUT_JSON as SOURCE_GATE_JSON_PATH,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxHarnessImplementationAuthorizationIntakeGate.v1"
GATE_ID = "abx_harness_implementation_authorization_intake_gate_001"
GATE_JSON_PATH = Path(
    "out/operator_review/abx_harness_implementation_authorization_intake_gate_001.latest.json"
)
GATE_MD_PATH = GATE_JSON_PATH.with_suffix(".md")
DEFAULT_PAYLOAD_PATH = Path(
    "operator_input/abx_harness_implementation_authorization_record_001.json"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"
GATE_HELD_STATUS = "SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_HELD_FOR_OPERATOR"
GATE_GRANTED_STATUS = "SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_GRANTED"
UPSTREAM_GATE_STATUSES = frozenset({GATE_HELD_STATUS, GATE_GRANTED_STATUS})


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _validate_payload(payload: Mapping[str, Any]) -> tuple[list[str], str | None]:
    blockers: list[str] = []
    if payload.get("record_type") != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL":
        blockers.append("record_type_invalid")
    if payload.get("record_id") != "ABX_HARNESS_IMPLEMENTATION_AUTHORIZATION_RECORD_001":
        blockers.append("record_id_invalid")
    if payload.get("decision_value") != "approve_harness_implementation_record":
        blockers.append("decision_value_invalid")
    if payload.get("status") != "AUTHORIZED_RECORD":
        blockers.append("status_invalid")

    scope = _mapping(payload.get("implementation_scope"))
    if scope.get("implementation_may_proceed") is not True:
        blockers.append("implementation_may_proceed_not_true")

    boundaries = _mapping(payload.get("authority_boundaries"))
    for field in (
        "executable_authority_granted",
        "runtime_execution_allowed",
        "repair_execution_allowed",
        "canon_promotion_allowed",
        "scheduler_mutation_allowed",
        "queue_mutation_allowed",
        "notion_writeback_allowed",
        "github_admin_authority_allowed",
        "downstream_authority_granted",
    ):
        if boundaries.get(field) is not False:
            blockers.append(f"{field}_not_false")

    acknowledgements = _mapping(payload.get("operator_acknowledgements"))
    for field in (
        "advisory_only_acknowledged",
        "implementation_scope_only_acknowledged",
        "no_executable_authority_granted_acknowledged",
        "no_runtime_mutation_acknowledged",
        "no_canon_promotion_acknowledged",
        "separate_authorization_required_for_downstream_lanes",
    ):
        if acknowledgements.get(field) is not True:
            blockers.append(f"{field}_not_acknowledged")

    seal = _mapping(payload.get("seal"))
    if seal.get("authorization_class") != "IMPLEMENTATION_APPROVED_RECORD_ONLY":
        blockers.append("authorization_class_invalid")
    if seal.get("execution_status") != "NOT_AUTHORIZED_FOR_EXECUTION":
        blockers.append("execution_status_invalid")

    decision_value = payload.get("decision_value")
    return sorted(set(blockers)), (
        str(decision_value) if isinstance(decision_value, str) else None
    )


def build_abx_harness_implementation_authorization_intake_gate(
    repo_root: str | Path = ".",
    authorization_payload_path: str | Path = DEFAULT_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    payload_rel = Path(authorization_payload_path)
    payload = _read_json(root / payload_rel)
    source_gate = _read_json(root / SOURCE_GATE_JSON_PATH) or {}
    source_gate_observed = bool(source_gate)
    source_gate_held = source_gate.get("authorization_gate_status") in UPSTREAM_GATE_STATUSES
    payload_observed = payload is not None
    blockers, decision_value = (
        _validate_payload(payload) if payload_observed else (["payload_missing"], None)
    )
    intake_valid = source_gate_observed and source_gate_held and payload_observed and not blockers
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "status": (
            "ABX_HARNESS_IMPLEMENTATION_AUTHORIZATION_INTAKE_VALIDATED"
            if intake_valid
            else "ABX_HARNESS_IMPLEMENTATION_AUTHORIZATION_INTAKE_BLOCKED"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authorization_payload_path": payload_rel.as_posix(),
        "authorization_payload_observed": payload_observed,
        "authorization_payload_file_hash": _sha256(root / payload_rel)
        if payload_observed
        else NOT_COMPUTABLE,
        "authorization_payload_packet_hash": canonical_hash(payload)
        if payload_observed
        else NOT_COMPUTABLE,
        "source_gate_path": SOURCE_GATE_JSON_PATH,
        "source_gate_hash": str(source_gate.get("packet_hash", NOT_COMPUTABLE)),
        "source_gate_observed": source_gate_observed,
        "source_gate_held_for_operator": source_gate_held,
        "operator_decision_value": decision_value or NOT_COMPUTABLE,
        "intake_validated_for_authorization_record": intake_valid,
        "validation_blockers": blockers,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "recommended_next_lane": (
            "ABX_HARNESS_IMPLEMENTATION_AUTHORIZATION_RECORD_001"
            if intake_valid
            else NOT_COMPUTABLE
        ),
        "downstream": NOT_COMPUTABLE,
        "gate_hash": "",
    }
    packet["gate_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "gate_hash"}
    )
    return packet


def write_abx_harness_implementation_authorization_intake_gate(
    repo_root: str | Path = ".",
    out_root: str | Path | None = None,
    authorization_payload_path: str | Path = DEFAULT_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_harness_implementation_authorization_intake_gate(
        root, authorization_payload_path=authorization_payload_path
    )
    write_canonical_json(target_root / GATE_JSON_PATH, packet)
    target_root.joinpath(GATE_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    target_root.joinpath(GATE_MD_PATH).write_text(
        "\n".join(
            [
                "# ABX Harness Implementation Authorization Intake Gate 001",
                "",
                f"- status: {packet['status']}",
                f"- intake_validated_for_authorization_record: {packet['intake_validated_for_authorization_record']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
