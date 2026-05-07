from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel


class ManualExecutionReceiptDiagnosticPacket(BaseModel):
    schema_version: Literal["ManualExecutionReceiptDiagnosticPacket.v1"] = "ManualExecutionReceiptDiagnosticPacket.v1"
    diagnostic_id: str
    diagnostic_type: Literal[
        "forbidden_receipt_status",
        "forbidden_receipt_action",
        "replay_mismatch",
        "missing_acknowledgement",
        "missing_authorization_envelope",
        "authority_violation",
        "auto_execution_attempted",
        "receipt_lineage_cycle",
        "receipt_continuity_break",
    ]
    severity: Literal["info", "warning", "critical"]
    diagnostic_message: str
    resolved: bool = False
    deterministic_diagnostic_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(diag_type: str, severity: str, message: str) -> str:
        return hashlib.sha256(f"{diag_type}|{severity}|{message}".encode()).hexdigest()
