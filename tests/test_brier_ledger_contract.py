import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from core.scoring import (
    build_brier_ledger_entry,
    canonical_brier_ledger_json,
    compute_brier_score,
    brier_ledger_hash,
    validate_brier_ledger_entry,
    write_brier_ledger_contract_audit,
)
from core.scoring.models import AuthorityRef, BrierScorePolicy


def _policy(partial_policy: str = "PARTIAL_LINEAR") -> BrierScorePolicy:
    return BrierScorePolicy("BRIER_BINARY_V1", "ROUND_10_DP", partial_policy, "VOID_NOT_SCORABLE", "CONFLICT_NOT_SCORABLE")


def _base(**kwargs):
    return build_brier_ledger_entry(
        ledger_entry_id=kwargs.get("ledger_entry_id", "bl-1"),
        forecast_id=kwargs.get("forecast_id", "fc-1"),
        forecast_hash=kwargs.get("forecast_hash", "fhash"),
        settlement_id=kwargs.get("settlement_id", "sv-1"),
        settlement_hash=kwargs.get("settlement_hash", "shash"),
        probability=kwargs.get("probability", 0.8),
        settlement_decision=kwargs.get("settlement_decision", "TRUE"),
        outcome_value=kwargs.get("outcome_value", 1.0),
        score_policy=kwargs.get("score_policy", _policy()),
        created_by_lane=kwargs.get("created_by_lane", "OPERATOR"),
        authority_ref=kwargs.get("authority_ref", AuthorityRef("MANUAL_RECEIPT", "receipt://1", "op")),
    )


def test_true_decision_score_fixed_rounding():
    assert compute_brier_score(0.8, 1.0) == 0.04


def test_false_decision_score_fixed_rounding():
    assert compute_brier_score(0.8, 0.0) == 0.64


def test_partial_decision_supports_explicit_outcome_value():
    obj = _base(settlement_decision="PARTIAL", outcome_value=0.3)
    assert validate_brier_ledger_entry(obj).status == "PASS"


def test_probability_outside_range_blocked_or_not_computable():
    assert validate_brier_ledger_entry(_base(probability=1.1)).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_outcome_value_outside_range_blocked_or_not_computable():
    assert validate_brier_ledger_entry(_base(outcome_value=1.1)).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_non_scorable_decisions_not_score_ready():
    for d in ("VOID", "CONFLICTING", "NOT_COMPUTABLE"):
        assert validate_brier_ledger_entry(_base(settlement_decision=d)).status in {"NOT_COMPUTABLE", "BLOCKED"}


def test_true_cannot_use_zero_outcome():
    assert validate_brier_ledger_entry(_base(settlement_decision="TRUE", outcome_value=0.0)).status == "BLOCKED"


def test_false_cannot_use_one_outcome():
    assert validate_brier_ledger_entry(_base(settlement_decision="FALSE", outcome_value=1.0)).status == "BLOCKED"


def test_missing_forecast_settlement_hashes_blocked_or_not_computable():
    assert validate_brier_ledger_entry(_base(forecast_id="", forecast_hash="", settlement_id="", settlement_hash="")).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_shadow_cannot_finalize_ledger_entry():
    assert validate_brier_ledger_entry(_base(created_by_lane="SHADOW")).status == "BLOCKED"


def test_projection_cannot_create_scoring_authority():
    assert validate_brier_ledger_entry(_base(created_by_lane="PROJECTION")).status == "BLOCKED"


def test_ledger_hash_stable_excludes_ledger_hash_field():
    obj = _base()
    h1 = brier_ledger_hash(obj)
    payload = asdict(obj)
    payload["ledger_hash"] = "mutated"
    h2 = brier_ledger_hash(payload)
    assert h1 == h2


def test_canonical_json_byte_stable():
    obj = _base()
    assert canonical_brier_ledger_json(obj) == canonical_brier_ledger_json(obj)


def test_schema_accepts_shape_and_required_fields_present():
    schema = json.loads(Path("contracts/scoring/brier_ledger_entry.v1.schema.json").read_text(encoding="utf-8"))
    assert "required" in schema and "ledger_hash" in schema["required"]


def test_audit_artifact_stable_sha256_and_newline(tmp_path: Path):
    h1 = write_brier_ledger_contract_audit(tmp_path)
    p = tmp_path / "out/audit/brier_ledger_contract.latest.json"
    t1 = p.read_text(encoding="utf-8")
    h2 = write_brier_ledger_contract_audit(tmp_path)
    t2 = p.read_text(encoding="utf-8")
    assert t1.endswith("\n")
    assert h1 == h2
    assert hashlib.sha256(t1.encode()).hexdigest() == hashlib.sha256(t2.encode()).hexdigest()
