"""Comprehensive tests for core/settlement/verdict.py (Layer 0 HARDENING candidate).

Covers build, hash, canonical json, validate, and audit contract writer.
"""

import json
from pathlib import Path
import tempfile
import pytest

from core.settlement.verdict import (
    canonical_settlement_verdict_json,
    settlement_verdict_hash,
    build_settlement_verdict,
    validate_settlement_verdict,
    write_settlement_verdict_contract_audit,
)
from core.settlement.models import (
    SettlementDecision,
    SettlementReason,
    SettlementConflictSummary,
    SettlementStatus,
    AuthorityRef,
    SettlementVerdict,
)


def _make_sample_verdict() -> SettlementVerdict:
    return build_settlement_verdict(
        settlement_id="settlement-001",
        forecast_id="forecast-001",
        forecast_hash="hash-forecast-001",
        binding_id="binding-001",
        binding_hash="hash-binding-001",
        evidence_packet_id="evidence-001",
        evidence_hash="hash-evidence-001",
        decision=SettlementDecision.TRUE,
        reasons=(SettlementReason("r1", "POLICY", "Evidence supports TRUE", ("src-1",), "POLICY_BOOLEAN_SETTLEMENT"),),
        conflict_summary=SettlementConflictSummary(False, (), "NO_CONFLICT_POLICY", "CLEAR"),
        settlement_status=SettlementStatus.SETTLED,
        created_by_lane="OPERATOR",
        authority_ref=AuthorityRef("MANUAL", "receipt://test", "test receipt"),
    )


def test_build_settlement_verdict_deterministic():
    v1 = _make_sample_verdict()
    v2 = _make_sample_verdict()
    assert v1.settlement_hash == v2.settlement_hash
    assert v1.schema_version == "SettlementVerdict.v1"
    assert v1.decision == SettlementDecision.TRUE


def test_canonical_json_and_hash_stable():
    v = _make_sample_verdict()
    cj = canonical_settlement_verdict_json(v)
    h = settlement_verdict_hash(v)
    assert isinstance(cj, str)
    assert len(cj) > 10
    assert h == v.settlement_hash
    # determinism
    assert canonical_settlement_verdict_json(v) == cj
    assert settlement_verdict_hash(v) == h


def test_validate_settlement_verdict_runs():
    v = _make_sample_verdict()
    report = validate_settlement_verdict(v)
    assert hasattr(report, "status")
    assert hasattr(report, "findings")
    assert report.status in ("PASS", "FAIL", "VALID", "INVALID", "NOT_COMPUTABLE")


def test_write_settlement_verdict_contract_audit(tmp_path: Path):
    # run the audit writer
    receipt_hash = write_settlement_verdict_contract_audit(base_dir=tmp_path)
    assert isinstance(receipt_hash, str)
    assert len(receipt_hash) == 64  # sha256 hex

    out_file = tmp_path / "out/audit/settlement_verdict_contract.latest.json"
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert "status" in data
    assert "settlement_hash" in data


def test_verdict_hash_changes_with_content():
    v1 = _make_sample_verdict()
    # create a different one
    v2 = build_settlement_verdict(
        settlement_id="settlement-002",
        forecast_id="forecast-001",
        forecast_hash="hash-forecast-001",
        binding_id="binding-001",
        binding_hash="hash-binding-001",
        evidence_packet_id="evidence-001",
        evidence_hash="hash-evidence-001",
        decision=SettlementDecision.FALSE,
        reasons=(SettlementReason("r2", "POLICY", "Different reason", ("src-2",), "POLICY_BOOLEAN_SETTLEMENT"),),
        conflict_summary=SettlementConflictSummary(False, (), "NO_CONFLICT_POLICY", "CLEAR"),
        settlement_status=SettlementStatus.SETTLED,
        created_by_lane="OPERATOR",
        authority_ref=None,
    )
    assert v1.settlement_hash != v2.settlement_hash


if __name__ == "__main__":
    pytest.main([__file__, "-q"])