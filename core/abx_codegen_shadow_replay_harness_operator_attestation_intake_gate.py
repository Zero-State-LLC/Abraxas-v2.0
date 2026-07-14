from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxCodegenShadowReplayHarnessOperatorAttestationIntakeGate.v1"
GATE_ID = "abx_codegen_shadow_replay_harness_operator_attestation_intake_gate_001"
GATE_JSON_PATH = Path(
    "out/audit/abx_codegen_shadow_replay_harness_operator_attestation_intake_gate_001.latest.json"
)
GATE_MD_PATH = GATE_JSON_PATH.with_suffix(".md")
DEFAULT_PAYLOAD_PATH = Path(
    "operator_input/abx_codegen_shadow_replay_harness_operator_attestation_payload_001.json"
)
SOURCE_REVIEW_JSON_PATH = Path(
    "out/audit/"
    "abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_review_001.latest.json"
)


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


def _authority_locks() -> dict[str, bool]:
    return {
        "activation_allowed": False,
        "auto_approval_allowed": False,
        "canon_mutation_allowed": False,
        "codegen_implementation_allowed": False,
        "decision_record_creation": False,
        "execution_authority": False,
        "forecast_routing_allowed": False,
        "github_writeback_allowed": False,
        "harness_implementation": False,
        "harness_implementation_authorized": False,
        "notion_writeback_allowed": False,
        "operator_attestation": False,
        "queue_mutation_allowed": False,
        "replay_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "shadow_replay_execution": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _validate_payload(payload: Mapping[str, Any]) -> tuple[list[str], str | None]:
    blockers: list[str] = []
    if not payload.get("payload_id"):
        blockers.append("payload_id_missing")

    governance = _mapping(payload.get("governance"))
    authorization = _mapping(payload.get("authorization"))
    if governance.get("authority_granted") is not False:
        blockers.append("authority_granted_not_false")
    if authorization.get("authority_granted") is not False:
        blockers.append("authorization_authority_granted_not_false")
    if governance.get("harness_implementation_authorized") is not False:
        blockers.append("harness_implementation_authorized_not_false")
    if authorization.get("authorize_harness_implementation") is not False:
        blockers.append("harness_implementation_authorization_requested")
    if authorization.get("authorize_harness_execution") is not False:
        blockers.append("harness_execution_authorization_requested")
    if governance.get("advisory_only") is not True:
        blockers.append("advisory_only_not_true")

    seal = _mapping(payload.get("seal"))
    governance_mutation = governance.get("mutation_allowed")
    if seal.get("mutation_allowed") is not False and governance_mutation is not False:
        blockers.append("mutation_allowed_not_false")

    attestation = _mapping(payload.get("attestation"))
    if attestation.get("external_attestation_received") is not True:
        blockers.append("external_attestation_not_received")
    if attestation.get("operator_acceptance") == "PENDING":
        blockers.append("operator_acceptance_pending")
    if attestation.get("operator_review_complete") is not True:
        blockers.append("operator_review_incomplete")
    if authorization.get("authorize_intake_gate_clearance") is not True:
        blockers.append("intake_gate_clearance_not_authorized")
    if authorization.get("codegen_shadow_replay_harness_attestation_intake_clearance") is not True:
        blockers.append("attestation_intake_clearance_not_authorized")

    operator_seal = _mapping(payload.get("operator_seal"))
    if operator_seal.get("decision") != "AUTHORIZE_ATTESTATION_INTAKE_CLEARANCE_ONLY":
        blockers.append("operator_seal_decision_invalid")

    payload_status = seal.get("payload_status")
    return sorted(set(blockers)), (
        str(payload_status) if isinstance(payload_status, str) else None
    )


def build_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate(
    repo_root: str | Path = ".",
    attestation_payload_path: str | Path = DEFAULT_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    payload_rel = Path(attestation_payload_path)
    payload = _read_json(root / payload_rel)
    review = _read_json(root / SOURCE_REVIEW_JSON_PATH) or {}
    review_observed = bool(review)
    review_status = review.get("operator_decision_record_review_status")
    review_upstream_ready = review_status in (
        "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR",
        "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW_INTAKE_CLEARED_OBSERVED",
    )
    review_held = review_upstream_ready
    payload_observed = payload is not None
    blockers, payload_status = (
        _validate_payload(payload) if payload_observed else (["payload_missing"], None)
    )
    intake_valid = review_observed and review_held and payload_observed and not blockers
    governance = _mapping(payload.get("governance")) if payload_observed else {}
    authorization = _mapping(payload.get("authorization")) if payload_observed else {}
    downstream_status = (
        str(governance.get("downstream_status", NOT_COMPUTABLE))
        if intake_valid
        else NOT_COMPUTABLE
    )
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "status": (
            "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE_VALIDATED"
            if intake_valid
            else "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE_BLOCKED"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "attestation_payload_path": payload_rel.as_posix(),
        "attestation_payload_observed": payload_observed,
        "attestation_payload_file_hash": _sha256(root / payload_rel)
        if payload_observed
        else NOT_COMPUTABLE,
        "attestation_payload_packet_hash": canonical_hash(payload)
        if payload_observed
        else NOT_COMPUTABLE,
        "source_review_path": SOURCE_REVIEW_JSON_PATH.as_posix(),
        "source_review_hash": str(review.get("packet_hash", NOT_COMPUTABLE)),
        "source_review_observed": review_observed,
        "source_review_held_for_operator": review_held,
        "payload_status": payload_status or NOT_COMPUTABLE,
        "authority_granted": governance.get("authority_granted", False),
        "harness_implementation_authorized": governance.get(
            "harness_implementation_authorized", False
        ),
        "intake_gate_clearance_authorized": authorization.get(
            "authorize_intake_gate_clearance", False
        ),
        "intake_validated_for_operator_decision_record": intake_valid,
        "validation_blockers": blockers,
        "authority_locks": _authority_locks(),
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "harness_implementation_performed": False,
        "recommended_next_lane": (
            "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW"
            if intake_valid
            else NOT_COMPUTABLE
        ),
        "downstream": downstream_status,
        "gate_hash": "",
    }
    packet["gate_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "gate_hash"}
    )
    return packet


def write_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate(
    repo_root: str | Path = ".",
    out_root: str | Path | None = None,
    attestation_payload_path: str | Path = DEFAULT_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate(
        root, attestation_payload_path=attestation_payload_path
    )
    write_canonical_json(target_root / GATE_JSON_PATH, packet)
    target_root.joinpath(GATE_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    target_root.joinpath(GATE_MD_PATH).write_text(
        "\n".join(
            [
                "# ABX Codegen Shadow Replay Harness Operator Attestation Intake Gate 001",
                "",
                f"- status: {packet['status']}",
                f"- payload_status: {packet['payload_status']}",
                f"- intake_validated_for_operator_decision_record: {packet['intake_validated_for_operator_decision_record']}",
                f"- authority_granted: {packet['authority_granted']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
