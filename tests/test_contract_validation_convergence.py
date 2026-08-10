"""Shared validation-report convergence: one shape, byte-identical receipts.

Golden hashes below were captured from the pre-convergence per-layer
implementations (duplicated dataclasses + local canonical/sha256 helpers).
The shared ``core.contract_validation`` layer must reproduce them exactly.
"""

from core.contract_validation import (
    ContractValidationFinding,
    ContractValidationReport,
    build_validation_report,
)
from core.replay_execution.models import (
    AuthorityRef as ReplayAuthorityRef,
    ReplayDeterminismReport,
    ReplayExecutionEnvelope,
    ReplayExecutionReceipt,
    ReplayInputRef,
    ReplayMutationPlan,
    ReplayRollbackPlan,
    ReplayValidationFinding,
    ReplayValidationReport,
)
from core.replay_execution.validator import validate_replay_execution_envelope
from core.replay_ledger.models import (
    ReplayLedger,
    ReplayLedgerEntry,
    ReplayLedgerValidationFinding,
    ReplayLedgerValidationReport,
    ReplayTemporalDiff,
    ReplayTemporalStabilityScore,
)
from core.replay_ledger.validator import validate_replay_ledger, validate_replay_temporal_diff
from core.settlement import build_settlement_verdict, validate_settlement_verdict
from core.settlement.models import (
    AuthorityRef,
    SettlementConflictSummary,
    SettlementDecision,
    SettlementReason,
    SettlementStatus,
    SettlementValidationFinding,
    SettlementValidationReport,
)

GOLDEN_SETTLEMENT = "8a7d45ff814be7ed4e9914041f14ab7796e5bd7524f62f83cabdda7b2c2cf597"
GOLDEN_REPLAY_EXEC = "8d88d31278b1c98598f47e5b58ce2807f969612ca0c0cbca365d5adcb2afb81d"
GOLDEN_LEDGER = "31f3d5ba798b99c672a4e919605fc7ef97bd6bf6e744a07b56c2c5146fae7bb9"
GOLDEN_DIFF = "745b9f31a0c3fee85f37cf01302f4bcc14f490af8d3eda62707e08303915cff5"


def test_layers_share_one_report_shape():
    assert SettlementValidationReport is ContractValidationReport
    assert ReplayValidationReport is ContractValidationReport
    assert ReplayLedgerValidationReport is ContractValidationReport
    assert SettlementValidationFinding is ContractValidationFinding
    assert ReplayValidationFinding is ContractValidationFinding
    assert ReplayLedgerValidationFinding is ContractValidationFinding


def test_settlement_receipt_hash_golden():
    verdict = build_settlement_verdict(
        "sv-1",
        "fc-1",
        "fhash",
        "ob-1",
        "bhash",
        "ep-1",
        "ehash",
        SettlementDecision.TRUE,
        (SettlementReason("r1", "EVENT", "Reason", ("src-1",), "POLICY"),),
        SettlementConflictSummary(False, (), "NO_CONFLICT", "CLEAR"),
        SettlementStatus.SETTLED,
        "OPERATOR",
        AuthorityRef("MANUAL_RECEIPT", "receipt://1", "op"),
    )
    report = validate_settlement_verdict(verdict)
    assert report.status == "PASS"
    assert report.receipt_hash == GOLDEN_SETTLEMENT


def test_replay_execution_receipt_hash_golden():
    envelope = ReplayExecutionEnvelope(
        "ReplayExecutionEnvelope.v1",
        "rp-1",
        "auth-1",
        "ahash",
        "cl-1",
        "clhash",
        (ReplayInputRef("ARTIFACT", "a-1", "h1"),),
        ReplayMutationPlan("mp-1", "SCOPE", ("a-1",), ("OP",), 1, False),
        ReplayRollbackPlan("rb-1", True, ("UNDO",), 1, "POLICY", True),
        ReplayExecutionReceipt("rc-1", "SANDBOX", ("oh-1",), False, "rchash"),
        ReplayDeterminismReport("dr-1", 3, True, ("c1",), False, "POLICY"),
        "REPLAY_PASSED",
        "OPERATOR",
        ReplayAuthorityRef("MANUAL_RECEIPT", "receipt://1", "op"),
        False,
        False,
        False,
        False,
        "rhash",
    )
    report = validate_replay_execution_envelope(envelope)
    assert report.status == "PASS"
    assert report.receipt_hash == GOLDEN_REPLAY_EXEC


def test_replay_ledger_receipt_hash_golden():
    ledger = ReplayLedger(
        "ReplayLedger.v1",
        "lg-1",
        (ReplayLedgerEntry("e1", "rp-1", "rh", "REPLAY_PASSED", "auth-1", "ah", "dh", "rbh", 0, "POL"),),
        (),
        "LEDGER_READY",
        "POL",
        "OPERATOR",
        None,
        False,
        False,
        False,
        "lh",
    )
    report = validate_replay_ledger(ledger)
    assert report.status == "PASS"
    assert report.receipt_hash == GOLDEN_LEDGER


def test_replay_temporal_diff_receipt_hash_golden():
    diff = ReplayTemporalDiff(
        "ReplayTemporalDiff.v1",
        "df-1",
        "rp-1",
        "h1",
        "rp-2",
        "h2",
        (),
        (),
        ReplayTemporalStabilityScore("s1", 3, 3, 0, 1.0, "STABLE", False),
        "NO_DIVERGENCE",
        "OPERATOR",
        None,
        False,
        False,
        False,
        "dh",
    )
    report = validate_replay_temporal_diff(diff)
    assert report.status == "PASS"
    assert report.receipt_hash == GOLDEN_DIFF


def test_builder_receipt_hash_matches_layer_output():
    report = build_validation_report("PASS", [], subject_key="settlement_id", subject_id="sv-1")
    assert report.receipt_hash == GOLDEN_SETTLEMENT
    assert report.findings == ()
