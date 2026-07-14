from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.oracle_signal_physical_implementation_authorization_record_plan import (
    PLAN_JSON_PATH as SOURCE_PLAN_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "OracleSignalPhysicalImplementationAuthorizationIntakeGate.v1"
GATE_ID = "oracle_signal_physical_implementation_authorization_intake_gate_001"
GATE_JSON_PATH = Path(
    "out/operator_review/oracle_signal_physical_implementation_authorization_intake_gate_001.latest.json"
)
GATE_MD_PATH = GATE_JSON_PATH.with_suffix(".md")
DEFAULT_PAYLOAD_PATH = Path(
    "operator_input/oracle_signal_physical_implementation_authorization_payload_001.json"
)
ALLOWED_DECISIONS = frozenset({"APPROVE_PHYSICAL_IMPLEMENTATION", "MAINTAIN_HOLD"})


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


def _validate_payload(payload: Mapping[str, Any], review_hash: str) -> tuple[list[str], str | None]:
    blockers: list[str] = []
    for group in ("operator_identity", "operator_decision", "acknowledgements"):
        if not isinstance(payload.get(group), Mapping):
            blockers.append(f"{group}_missing")
    decision = payload.get("operator_decision", {})
    selected = decision.get("selected_decision") if isinstance(decision, Mapping) else None
    if selected not in ALLOWED_DECISIONS:
        blockers.append("selected_decision_invalid")
    if isinstance(decision, Mapping) and decision.get("source_review_hash") != review_hash:
        blockers.append("source_review_hash_mismatch")
    acks = payload.get("acknowledgements", {})
    for field in (
        "authority_boundaries_acknowledged",
        "execution_authority_denied_acknowledged",
        "rollback_and_fail_closed_acknowledged",
    ):
        if not isinstance(acks, Mapping) or acks.get(field) is not True:
            blockers.append(f"{field}_not_acknowledged")
    return sorted(set(blockers)), selected if isinstance(selected, str) else None


def build_oracle_signal_physical_implementation_authorization_intake_gate(
    repo_root: str | Path = ".",
    attestation_payload_path: str | Path = DEFAULT_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    payload_rel = Path(attestation_payload_path)
    payload = _read_json(root / payload_rel)
    plan = _read_json(root / SOURCE_PLAN_JSON_PATH) or {}
    plan_ready = plan.get("status") == (
        "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN_READY"
    )
    review_hash = str(plan.get("source_review_hash", ""))
    payload_observed = payload is not None
    blockers, selected_decision = (
        _validate_payload(payload, review_hash) if payload_observed else (["payload_missing"], None)
    )
    intake_valid = plan_ready and payload_observed and not blockers
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "status": (
            "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_INTAKE_VALIDATED"
            if intake_valid
            else "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_INTAKE_BLOCKED"
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
        "intake_validated_for_authorization_record": intake_valid,
        "validation_blockers": blockers,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "recommended_next_lane": (
            "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_RECORD_001"
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


def write_oracle_signal_physical_implementation_authorization_intake_gate(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
    attestation_payload_path: str | Path = DEFAULT_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_oracle_signal_physical_implementation_authorization_intake_gate(
        root, attestation_payload_path=attestation_payload_path
    )
    write_canonical_json(target_root / GATE_JSON_PATH, packet)
    target_root.joinpath(GATE_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    target_root.joinpath(GATE_MD_PATH).write_text(
        f"# Oracle Signal Physical Implementation Authorization Intake Gate\n\n- status: {packet['status']}\n",
        encoding="utf-8",
    )
    return packet
