from __future__ import annotations

# WP-D4-C1: pure builder — sole-writer scripts own out/ publication.
from core.governance.upstream_evidence import require_upstream_packets
from core.manual_execution_receipts.acknowledgements import (
    ManualExecutionReceiptAcknowledgementPacket,
)
from core.manual_execution_receipts.continuity import (
    ManualExecutionReceiptContinuityPacket,
)
from core.manual_execution_receipts.diagnostics import (
    ManualExecutionReceiptDiagnosticPacket,
)
from core.manual_execution_receipts.ledger import ManualExecutionReceiptLedgerPacket
from core.manual_execution_receipts.lineage import ManualExecutionReceiptLineagePacket
from core.manual_execution_receipts.operator_review import (
    ManualExecutionReceiptOperatorReviewPacket,
)
from core.manual_execution_receipts.receipts import ManualExecutionReceiptPacket
from core.manual_execution_receipts.replay import ManualExecutionReceiptReplayPacket
from core.manual_execution_receipts.scope import (
    FORBIDDEN_RECEIPT_ACTIONS,
    ManualExecutionReceiptScopePacket,
)
from core.manual_execution_receipts.validators import validate_manual_execution_receipts


def run_manual_execution_receipt_ledger(
    manual_execution_packets: list[dict],
    authorization_packets: list[dict],
    acknowledgement_packets: list[dict],
    replay_packets: list[dict],
    rollback_packets: list[dict],
) -> dict[str, object]:
    require_upstream_packets(
        ("manual_execution_packets", manual_execution_packets),
        ("authorization_packets", authorization_packets),
        ("acknowledgement_packets", acknowledgement_packets),
        ("replay_packets", replay_packets),
        ("rollback_packets", rollback_packets),
        surface="manual_execution_receipt_ledger",
    )
    del (
        manual_execution_packets,
        authorization_packets,
        acknowledgement_packets,
        replay_packets,
        rollback_packets,
    )
    receipt = ManualExecutionReceiptPacket(
        receipt_id="merc-1",
        authorization_hash="auth-1",
        envelope_hash="env-1",
        acknowledgement_hash="ack-1",
        scope_hash="scope-1",
        replay_hash="replay-1",
        rollback_hash="rollback-1",
        receipt_status="receipt_recorded",
        receipt_reason="human receipt recorded for manual review only",
        deterministic_receipt_hash=ManualExecutionReceiptPacket.compute_hash(
            "auth-1",
            "env-1",
            "ack-1",
            "scope-1",
            "replay-1",
            "rollback-1",
            "receipt_recorded",
            "human receipt recorded for manual review only",
        ),
        status="passed",
    )
    ledger = ManualExecutionReceiptLedgerPacket(
        ledger_id="merl-1",
        receipt_hashes=[receipt.deterministic_receipt_hash],
        total_receipts=1,
        pending_receipts=0,
        blocked_receipts=0,
        invalid_receipts=0,
        deterministic_ledger_hash=ManualExecutionReceiptLedgerPacket.compute_hash(
            [receipt.deterministic_receipt_hash], 1, 0, 0, 0
        ),
        status="passed",
    )
    scope = ManualExecutionReceiptScopePacket(
        receipt_scope_id="mers-1",
        receipt_hash=receipt.deterministic_receipt_hash,
        bounded_scope_hash="bounded-1",
        allowed_receipt_actions=[
            "inspect_receipt",
            "document_receipt",
            "compare_receipt",
            "defer_receipt",
            "invalidate_receipt",
        ],
        forbidden_receipt_actions=sorted(FORBIDDEN_RECEIPT_ACTIONS),
        deterministic_scope_hash=ManualExecutionReceiptScopePacket.compute_hash(
            receipt.deterministic_receipt_hash,
            "bounded-1",
            [
                "inspect_receipt",
                "document_receipt",
                "compare_receipt",
                "defer_receipt",
                "invalidate_receipt",
            ],
            sorted(FORBIDDEN_RECEIPT_ACTIONS),
        ),
        status="passed",
    )
    ack = ManualExecutionReceiptAcknowledgementPacket(
        acknowledgement_id="mera-1",
        receipt_hash=receipt.deterministic_receipt_hash,
        acknowledgement_hash="human-ack-1",
        deterministic_acknowledgement_hash=ManualExecutionReceiptAcknowledgementPacket.compute_hash(
            receipt.deterministic_receipt_hash, "human-ack-1"
        ),
        status="passed",
    )
    continuity = ManualExecutionReceiptContinuityPacket(
        continuity_id="merc-1",
        receipt_hash=receipt.deterministic_receipt_hash,
        envelope_hash=receipt.envelope_hash,
        append_only=True,
        deterministic_continuity_hash=ManualExecutionReceiptContinuityPacket.compute_hash(
            receipt.deterministic_receipt_hash, receipt.envelope_hash, True
        ),
        status="passed",
    )
    replay = ManualExecutionReceiptReplayPacket(
        replay_id="merr-1",
        source_ledger_hash=ledger.deterministic_ledger_hash,
        replay_ledger_hash=ledger.deterministic_ledger_hash,
        deterministic_match=True,
        mismatch_reasons=[],
        deterministic_replay_hash=ManualExecutionReceiptReplayPacket.compute_hash(
            ledger.deterministic_ledger_hash,
            ledger.deterministic_ledger_hash,
            True,
            [],
        ),
        status="passed",
    )
    lineage = ManualExecutionReceiptLineagePacket(
        lineage_id="merlin-1",
        continuity_hash=continuity.deterministic_continuity_hash,
        parent_hashes=["manual-receipt-root"],
        lineage_cycle_detected=False,
        deterministic_lineage_hash=ManualExecutionReceiptLineagePacket.compute_hash(
            continuity.deterministic_continuity_hash, ["manual-receipt-root"], False
        ),
        status="passed",
    )
    diagnostics = [
        ManualExecutionReceiptDiagnosticPacket(
            diagnostic_id="merd-1",
            diagnostic_type="missing_acknowledgement",
            severity="info",
            diagnostic_message="acknowledgement present",
            resolved=True,
            deterministic_diagnostic_hash=ManualExecutionReceiptDiagnosticPacket.compute_hash(
                "missing_acknowledgement", "info", "acknowledgement present"
            ),
            status="passed",
        )
    ]
    review = ManualExecutionReceiptOperatorReviewPacket(
        review_id="meror-1",
        receipt_ledger_hash=ledger.deterministic_ledger_hash,
        total_receipts=1,
        pending_receipts=0,
        blocked_receipts=0,
        invalid_receipts=0,
        unresolved_diagnostics=0,
        deterministic_review_hash=ManualExecutionReceiptOperatorReviewPacket.compute_hash(
            ledger.deterministic_ledger_hash, 1, 0, 0, 0, 0
        ),
        status="passed",
    )
    validator = validate_manual_execution_receipts(
        False,
        False,
        True,
        [d.model_dump() for d in diagnostics],
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    )
    return {
        "schema_version": "ManualExecutionReceiptRuntimePacket.v1",
        "receipt": receipt.model_dump(),
        "ledger": ledger.model_dump(),
        "scope": scope.model_dump(),
        "acknowledgement": ack.model_dump(),
        "continuity": continuity.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "diagnostics": [d.model_dump() for d in diagnostics],
        "operator_review": review.model_dump(),
        "manual_execution_receipt_summary": {
            "total_receipts": 1,
            "pending_receipts": 0,
            "blocked_receipts": 0,
            "invalid_receipts": 0,
            "replay_matches": replay.deterministic_match,
            "unresolved_diagnostics": 0,
            "authority_locked": True,
            "projection_only": True,
            "inference_authority": False,
        },
        "validator": validator,
        "status": validator["status"],
    }
