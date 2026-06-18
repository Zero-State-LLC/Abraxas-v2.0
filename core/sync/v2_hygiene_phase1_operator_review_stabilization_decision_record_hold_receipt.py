from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_operator_review_stabilization_operator_decision_record import (
    RECORD_JSON_PATH as SOURCE_RECORD_JSON_PATH,
)

SCHEMA_VERSION = (
    "V2HygienePhase1OperatorReviewStabilizationDecisionRecordHoldReceipt.v1"
)
RECEIPT_ID = (
    "v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt_001"
)
RECEIPT_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = (
    "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_OPERATOR_DECISION_RECORD_ATTESTED"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def build_v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    record = _read_json(root / SOURCE_RECORD_JSON_PATH) or {}
    source_ready = (
        record.get("schema_version")
        == "V2HygienePhase1OperatorReviewStabilizationOperatorDecisionRecord.v1"
        and record.get("status") == EXPECTED_SOURCE_STATUS
        and record.get("operator_attestations_present") is True
        and record.get("hygiene_code_creation_authorized") is False
        and record.get("schema_mutation_authorized") is False
        and record.get("v2_module_registration_authorized") is False
        and record.get("execution_authority") is False
        and record.get("valid_for_execution") is False
    )
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": (
            "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_HOLD_RECEIPT_EMITTED"
            if source_ready
            else "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_HOLD_RECEIPT_BLOCKED"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "terminal_hold": True if source_ready else False,
        "compression_receipt": True if source_ready else False,
        "hold_reason": (
            "stabilization operator decision record attested with hygiene implementation, "
            "schema mutation, v2 module registration, and execution authority denied"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "hygiene_code_creation_authorized": False,
        "schema_mutation_authorized": False,
        "v2_module_registration_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "source_decision_record_path": SOURCE_RECORD_JSON_PATH.as_posix(),
        "source_decision_record_hash": str(
            record.get("decision_record_hash", NOT_COMPUTABLE)
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "maintain stabilization hold; do not create hygiene code, mutate schemas, "
            "or register v2 modules"
            if source_ready
            else "restore stabilization operator decision record evidence"
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
        "# v2.0 Hygiene Phase 1 Stabilization Decision Record Hold Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- terminal_hold: {packet['terminal_hold']}",
        f"- downstream: {packet['downstream']}",
    ]


def write_v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(out_root) if out_root is not None else Path(repo_root)
    packet = (
        build_v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt(
            repo_root
        )
    )
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(render_markdown(packet)) + "\n", encoding="utf-8")
    return packet
