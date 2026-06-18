from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.runtime_integration_gate_operator_review_decision_record_plan import (
    PLAN_JSON_PATH as SOURCE_PLAN_JSON_PATH,
)

SCHEMA_VERSION = "RuntimeIntegrationGateOperatorAttestationIntakeGate.v1"
GATE_ID = "runtime_integration_gate_operator_attestation_intake_gate_001"
GATE_JSON_PATH = Path(
    "out/audit/runtime_integration_gate_operator_attestation_intake_gate_001.latest.json"
)
GATE_MD_PATH = GATE_JSON_PATH.with_suffix(".md")
DEFAULT_PAYLOAD_PATH = Path(
    "operator_input/runtime_integration_gate_operator_attestation_payload_001.json"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"
ALLOWED_DECISIONS = frozenset(
    {
        "MAINTAIN_HOLD",
        "APPROVE_SHADOW_WIRING_ONLY",
        "APPROVE_MANDATORY_PRE_DISPATCH_WIRING",
    }
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
        "mandatory_pre_dispatch_wiring": False,
        "notion_writeback_allowed": False,
        "operator_attestation": False,
        "queue_mutation_allowed": False,
        "replay_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "valid_for_execution": False,
        "valid_for_runtime_wiring": False,
    }


def _validate_payload(payload: Mapping[str, Any]) -> tuple[list[str], str | None]:
    blockers: list[str] = []
    for group in ("operator_identity", "review_attestations", "operator_disposition"):
        if not isinstance(payload.get(group), Mapping):
            blockers.append(f"{group}_missing")
    identity = payload.get("operator_identity", {})
    if not isinstance(identity, Mapping) or not identity.get("operator_id"):
        blockers.append("operator_identity_invalid")
    attestations = payload.get("review_attestations", {})
    for field in (
        "authority_owner_mapping_review_attested",
        "no_authority_seal_review_attested",
        "codegen_boundary_review_attested",
        "receipt_freshness_review_attested",
    ):
        if not isinstance(attestations, Mapping) or attestations.get(field) is not True:
            blockers.append(f"{field}_not_attested")
    disposition = payload.get("operator_disposition", {})
    selected = disposition.get("selected_decision") if isinstance(disposition, Mapping) else None
    if selected not in ALLOWED_DECISIONS:
        blockers.append("selected_decision_invalid")
    return sorted(set(blockers)), selected if isinstance(selected, str) else None


def build_runtime_integration_gate_operator_attestation_intake_gate(
    repo_root: str | Path = ".",
    attestation_payload_path: str | Path = DEFAULT_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    payload_rel = Path(attestation_payload_path)
    payload = _read_json(root / payload_rel)
    plan = _read_json(root / SOURCE_PLAN_JSON_PATH) or {}
    plan_ready = plan.get("status") == (
        "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_PLAN_READY"
    )
    payload_observed = payload is not None
    blockers, selected_decision = (
        _validate_payload(payload) if payload_observed else (["payload_missing"], None)
    )
    intake_valid = plan_ready and payload_observed and not blockers
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "status": (
            "RUNTIME_INTEGRATION_GATE_OPERATOR_ATTESTATION_INTAKE_VALIDATED"
            if intake_valid
            else "RUNTIME_INTEGRATION_GATE_OPERATOR_ATTESTATION_INTAKE_BLOCKED"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "attestation_payload_path": payload_rel.as_posix(),
        "attestation_payload_observed": payload_observed,
        "attestation_payload_file_hash": _sha256(root / payload_rel) if payload_observed else NOT_COMPUTABLE,
        "attestation_payload_packet_hash": canonical_hash(payload)
        if payload_observed
        else NOT_COMPUTABLE,
        "source_plan_path": SOURCE_PLAN_JSON_PATH.as_posix(),
        "source_plan_hash": str(plan.get("plan_hash", NOT_COMPUTABLE)),
        "source_plan_ready": plan_ready,
        "operator_selected_decision": selected_decision or NOT_COMPUTABLE,
        "intake_validated_for_decision_record": intake_valid,
        "validation_blockers": blockers,
        "authority_locks": _authority_locks(),
        "execution_authority": False,
        "valid_for_execution": False,
        "mandatory_pre_dispatch_wiring": False,
        "valid_for_runtime_wiring": False,
        "runtime_mutation_allowed": False,
        "recommended_next_lane": (
            "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_001"
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


def write_runtime_integration_gate_operator_attestation_intake_gate(
    repo_root: str | Path = ".",
    out_root: str | Path | None = None,
    attestation_payload_path: str | Path = DEFAULT_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_runtime_integration_gate_operator_attestation_intake_gate(
        root, attestation_payload_path=attestation_payload_path
    )
    write_canonical_json(target_root / GATE_JSON_PATH, packet)
    target_root.joinpath(GATE_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    target_root.joinpath(GATE_MD_PATH).write_text(
        "\n".join(
            [
                "# Runtime Integration Gate Operator Attestation Intake Gate 001",
                "",
                f"- status: {packet['status']}",
                f"- operator_selected_decision: {packet['operator_selected_decision']}",
                f"- intake_validated_for_decision_record: {packet['intake_validated_for_decision_record']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
