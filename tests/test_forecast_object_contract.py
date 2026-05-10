import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from core.forecasting import (
    build_forecast_object,
    canonical_forecast_json,
    forecast_object_hash,
    validate_forecast_object,
    write_forecast_object_contract_audit,
)
from core.forecasting.models import ForecastAuthorityRef, ForecastEvidenceRef, OutcomeBindingStatus


def _base(**kwargs):
    return build_forecast_object(
        forecast_id=kwargs.get("forecast_id", "fc-1"),
        claim_statement=kwargs.get("claim_statement", "X will happen"),
        probability_value=kwargs.get("probability_value", 0.6),
        domain=kwargs.get("domain", "general"),
        horizon=kwargs.get("horizon", "2026-Q4"),
        created_by_lane=kwargs.get("created_by_lane", "FORECAST"),
        promotion_state=kwargs.get("promotion_state", "SHADOW_ONLY"),
        authority_ref=kwargs.get("authority_ref", ForecastAuthorityRef("CANON_FIXTURE", "fixture://authority", "Fixture authority")),
        evidence_refs=kwargs.get("evidence_refs", (ForecastEvidenceRef("REPO_FILE", "README.md", "readme"),)),
        outcome_binding_status=kwargs.get("outcome_binding_status", OutcomeBindingStatus.UNBOUND),
        calibration_ready=kwargs.get("calibration_ready", False),
    )


def test_valid_unbound_draft_warn_or_pass_and_not_cal_ready():
    obj = _base(outcome_binding_status=OutcomeBindingStatus.UNBOUND, calibration_ready=False)
    report = validate_forecast_object(obj)
    assert report.status in {"PASS", "WARN"}


def test_valid_bound_can_be_calibration_ready():
    obj = _base(outcome_binding_status=OutcomeBindingStatus.BOUND, calibration_ready=True)
    assert validate_forecast_object(obj).status == "PASS"


def test_probability_out_of_range_blocked():
    obj = _base(probability_value=1.2)
    assert validate_forecast_object(obj).status == "BLOCKED"


def test_missing_authority_for_forecast_not_computable():
    obj = _base(authority_ref=None, created_by_lane="FORECAST")
    assert validate_forecast_object(obj).status in {"NOT_COMPUTABLE", "BLOCKED"}


def test_shadow_cannot_emit_finalized_authority():
    obj = _base(created_by_lane="SHADOW", promotion_state="CANON_ACTIVE")
    assert validate_forecast_object(obj).status == "BLOCKED"


def test_projection_cannot_emit_authoritative_forecast_object():
    obj = _base(created_by_lane="PROJECTION", authority_ref=ForecastAuthorityRef("X", "Y", "Z"))
    assert validate_forecast_object(obj).status == "BLOCKED"


def test_hash_stable_excludes_forecast_hash_field():
    obj = _base()
    h1 = forecast_object_hash(obj)
    payload = asdict(obj)
    payload["forecast_hash"] = "mutated"
    h2 = forecast_object_hash(payload)
    assert h1 == h2


def test_canonical_json_byte_stable():
    obj = _base()
    assert canonical_forecast_json(obj) == canonical_forecast_json(obj)


def test_schema_required_fields_and_enums_contract_shape():
    schema = json.loads(Path("contracts/forecasting/forecast_object.v1.schema.json").read_text(encoding="utf-8"))
    assert "required" in schema and "forecast_hash" in schema["required"]
    assert "UNBOUND" in schema["properties"]["outcome_binding_status"]["enum"]


def test_audit_artifact_stable_sha256_and_newline(tmp_path: Path):
    h1 = write_forecast_object_contract_audit(tmp_path)
    p = tmp_path / "out/audit/forecast_object_contract.latest.json"
    t1 = p.read_text(encoding="utf-8")
    h2 = write_forecast_object_contract_audit(tmp_path)
    t2 = p.read_text(encoding="utf-8")
    assert t1.endswith("\n")
    assert h1 == h2
    assert hashlib.sha256(t1.encode()).hexdigest() == hashlib.sha256(t2.encode()).hexdigest()
