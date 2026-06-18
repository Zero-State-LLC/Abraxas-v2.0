from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.runtime_integration_gate_operator_review_decision_record import (
    RECORD_JSON_PATH as SOURCE_RECORD_JSON_PATH,
)

SCHEMA_VERSION = "RuntimeIntegrationGateOperatorReviewDecisionRecordHoldReceipt.v1"
RECEIPT_ID = "runtime_integration_gate_operator_review_decision_record_hold_receipt_001"
RECEIPT_JSON_PATH = Path(
    "out/audit/runtime_integration_gate_operator_review_decision_record_hold_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = (
    "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_ATTESTED"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def build_runtime_integration_gate_operator_review_decision_record_hold_receipt(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    record = _read_json(root / SOURCE_RECORD_JSON_PATH) or {}
    source_ready = (
        record.get("schema_version") == "RuntimeIntegrationGateOperatorReviewDecisionRecord.v1"
        and record.get("status") == EXPECTED_SOURCE_STATUS
        and record.get("operator_attestation_present") is True
        and record.get("mandatory_pre_dispatch_wiring") is False
        and record.get("valid_for_runtime_wiring") is False
        and record.get("runtime_mutation_allowed") is False
        and record.get("execution_authority") is False
        and record.get("valid_for_execution") is False
    )
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": (
            "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_HOLD_RECEIPT_EMITTED"
            if source_ready
            else "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_HOLD_RECEIPT_BLOCKED"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "terminal_hold": True if source_ready else False,
        "hold_reason": (
            "runtime integration gate operator review attested with all execution and "
            "runtime wiring authority denied; downstream lanes remain NOT_COMPUTABLE"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "mandatory_pre_dispatch_wiring": False,
        "valid_for_runtime_wiring": False,
        "runtime_mutation_allowed": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "source_decision_record_path": SOURCE_RECORD_JSON_PATH.as_posix(),
        "source_decision_record_hash": str(
            record.get("decision_record_hash", NOT_COMPUTABLE)
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "maintain runtime integration gate advisory hold; do not enable mandatory "
            "pre-dispatch wiring or runtime mutation"
            if source_ready
            else "restore operator-attested decision record evidence"
        ),
        "downstream": NOT_COMPUTABLE,
        "receipt_hash": "",
    }
    packet["receipt_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "receipt_hash"}
    )
    return packet


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    return [
        "# Runtime Integration Gate Operator Review Decision Record Hold Receipt 001",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- terminal_hold: {packet['terminal_hold']}",
        f"- mandatory_pre_dispatch_wiring: {packet['mandatory_pre_dispatch_wiring']}",
        f"- downstream: {packet['downstream']}",
    ]


def write_runtime_integration_gate_operator_review_decision_record_hold_receipt(
    repo_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_runtime_integration_gate_operator_review_decision_record_hold_receipt(
        root
    )
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    target_root.joinpath(RECEIPT_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    target_root.joinpath(RECEIPT_MD_PATH).write_text(
        "\n".join(render_markdown(packet)) + "\n",
        encoding="utf-8",
    )
    return packet
