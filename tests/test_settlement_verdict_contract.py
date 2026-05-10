import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from core.settlement import (
    build_settlement_verdict,
    canonical_settlement_verdict_json,
    settlement_verdict_hash,
    validate_settlement_verdict,
    write_settlement_verdict_contract_audit,
)
from core.settlement.models import AuthorityRef, SettlementConflictSummary, SettlementDecision, SettlementReason, SettlementStatus


def _base(**kwargs):
    return build_settlement_verdict(
        settlement_id=kwargs.get("settlement_id", "sv-1"),
        forecast_id=kwargs.get("forecast_id", "fc-1"),
        forecast_hash=kwargs.get("forecast_hash", "fhash"),
        binding_id=kwargs.get("binding_id", "ob-1"),
        binding_hash=kwargs.get("binding_hash", "bhash"),
        evidence_packet_id=kwargs.get("evidence_packet_id", "ep-1"),
        evidence_hash=kwargs.get("evidence_hash", "ehash"),
        decision=kwargs.get("decision", SettlementDecision.TRUE),
        reasons=kwargs.get("reasons", (SettlementReason("r1", "EVENT", "Reason", ("src-1",), "POLICY"),)),
        conflict_summary=kwargs.get("conflict_summary", SettlementConflictSummary(False, (), "NO_CONFLICT", "CLEAR")),
        settlement_status=kwargs.get("settlement_status", SettlementStatus.DRAFT),
        created_by_lane=kwargs.get("created_by_lane", "FORECAST"),
        authority_ref=kwargs.get("authority_ref", AuthorityRef("MANUAL_RECEIPT", "receipt://1", "op")),
    )


def test_valid_draft_warn_or_pass_not_score_ready():
    assert validate_settlement_verdict(_base(settlement_status=SettlementStatus.DRAFT)).status in {"PASS", "WARN"}


def test_valid_settled_decisions_pass_with_reason_and_authority():
    for d in (SettlementDecision.TRUE, SettlementDecision.FALSE, SettlementDecision.PARTIAL):
        assert validate_settlement_verdict(_base(settlement_status=SettlementStatus.SETTLED, decision=d)).status == "PASS"


def test_settled_without_reason_blocked_or_not_computable():
    s = validate_settlement_verdict(_base(settlement_status=SettlementStatus.SETTLED, reasons=())).status
    assert s in {"BLOCKED", "NOT_COMPUTABLE"}


def test_settled_without_authority_blocked_or_not_computable():
    s = validate_settlement_verdict(_base(settlement_status=SettlementStatus.SETTLED, authority_ref=None)).status
    assert s in {"BLOCKED", "NOT_COMPUTABLE"}


def test_settled_with_unresolved_conflicts_blocked_or_not_computable():
    cs = SettlementConflictSummary(True, ("c1",), "MANUAL_REVIEW", "UNRESOLVED")
    s = validate_settlement_verdict(_base(settlement_status=SettlementStatus.SETTLED, conflict_summary=cs)).status
    assert s in {"BLOCKED", "NOT_COMPUTABLE"}


def test_conflicting_without_conflict_flag_blocked_or_not_computable():
    cs = SettlementConflictSummary(False, (), "NONE", "NONE")
    s = validate_settlement_verdict(_base(settlement_status=SettlementStatus.CONFLICTING, decision=SettlementDecision.CONFLICTING, conflict_summary=cs)).status
    assert s in {"BLOCKED", "NOT_COMPUTABLE"}


def test_void_without_reason_blocked_or_not_computable():
    s = validate_settlement_verdict(_base(settlement_status=SettlementStatus.VOID, decision=SettlementDecision.VOID, reasons=())).status
    assert s in {"BLOCKED", "NOT_COMPUTABLE"}


def test_missing_refs_blocked_or_not_computable():
    s = validate_settlement_verdict(_base(forecast_id="", forecast_hash="", binding_id="", binding_hash="", evidence_packet_id="", evidence_hash="")).status
    assert s in {"BLOCKED", "NOT_COMPUTABLE"}


def test_shadow_cannot_mark_settled():
    assert validate_settlement_verdict(_base(created_by_lane="SHADOW", settlement_status=SettlementStatus.SETTLED)).status == "BLOCKED"


def test_projection_cannot_create_authoritative_settlement_verdict():
    assert validate_settlement_verdict(_base(created_by_lane="PROJECTION", settlement_status=SettlementStatus.SETTLED)).status == "BLOCKED"


def test_settlement_hash_stable_excludes_settlement_hash_field():
    obj = _base(settlement_status=SettlementStatus.SETTLED)
    h1 = settlement_verdict_hash(obj)
    payload = asdict(obj)
    payload["settlement_hash"] = "mutated"
    h2 = settlement_verdict_hash(payload)
    assert h1 == h2


def test_canonical_json_byte_stable():
    obj = _base(settlement_status=SettlementStatus.SETTLED)
    assert canonical_settlement_verdict_json(obj) == canonical_settlement_verdict_json(obj)


def test_schema_accepts_shape_and_required_fields_present():
    schema = json.loads(Path("contracts/settlement/settlement_verdict.v1.schema.json").read_text(encoding="utf-8"))
    assert "required" in schema and "settlement_hash" in schema["required"]


def test_audit_artifact_stable_sha256_and_newline(tmp_path: Path):
    h1 = write_settlement_verdict_contract_audit(tmp_path)
    p = tmp_path / "out/audit/settlement_verdict_contract.latest.json"
    t1 = p.read_text(encoding="utf-8")
    h2 = write_settlement_verdict_contract_audit(tmp_path)
    t2 = p.read_text(encoding="utf-8")
    assert t1.endswith("\n")
    assert h1 == h2
    assert hashlib.sha256(t1.encode()).hexdigest() == hashlib.sha256(t2.encode()).hexdigest()
