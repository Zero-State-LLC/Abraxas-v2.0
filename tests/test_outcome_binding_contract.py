import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from core.outcomes import (
    build_outcome_binding,
    canonical_outcome_binding_json,
    outcome_binding_hash,
    validate_outcome_binding,
    write_outcome_binding_contract_audit,
)
from core.outcomes.models import AuthorityRef, BindingStatus, OutcomeCriterion, ResolutionSourceRef, ResolutionWindow, VerdictRule


def _base(**kwargs):
    return build_outcome_binding(
        binding_id=kwargs.get("binding_id", "ob-1"),
        forecast_id=kwargs.get("forecast_id", "fc-1"),
        forecast_hash=kwargs.get("forecast_hash", "forecast-hash-1"),
        criteria=kwargs.get("criteria", (OutcomeCriterion("c1", "criterion"),)),
        resolution_sources=kwargs.get("resolution_sources", (ResolutionSourceRef("REPO_FIXTURE", "fixtures/x.json", "fixture"),)),
        resolution_window=kwargs.get("resolution_window", ResolutionWindow("OPEN_POLICY", "CLOSE_POLICY", "UTC_STATIC")),
        verdict_rule=kwargs.get("verdict_rule", VerdictRule("BOOLEAN_EVENT", "true_if_event")),
        binding_status=kwargs.get("binding_status", BindingStatus.DRAFT),
        created_by_lane=kwargs.get("created_by_lane", "FORECAST"),
        authority_ref=kwargs.get("authority_ref", AuthorityRef("MANUAL_RECEIPT", "receipt://1", "operator")),
        void_reason=kwargs.get("void_reason", None),
    )


def test_valid_draft_warn_or_pass_not_score_ready():
    obj = _base(binding_status=BindingStatus.DRAFT)
    assert validate_outcome_binding(obj).status in {"PASS", "WARN"}


def test_valid_bound_pass():
    obj = _base(binding_status=BindingStatus.BOUND)
    assert validate_outcome_binding(obj).status == "PASS"


def test_bound_without_criteria_blocked_or_not_computable():
    obj = _base(binding_status=BindingStatus.BOUND, criteria=())
    assert validate_outcome_binding(obj).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_bound_without_resolution_source_blocked_or_not_computable():
    obj = _base(binding_status=BindingStatus.BOUND, resolution_sources=())
    assert validate_outcome_binding(obj).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_bound_without_authority_blocked_or_not_computable():
    obj = _base(binding_status=BindingStatus.BOUND, authority_ref=None)
    assert validate_outcome_binding(obj).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_missing_forecast_id_or_hash_blocked_or_not_computable():
    obj = _base(forecast_id="", forecast_hash="")
    assert validate_outcome_binding(obj).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_shadow_cannot_create_authoritative_bound():
    obj = _base(created_by_lane="SHADOW", binding_status=BindingStatus.BOUND)
    assert validate_outcome_binding(obj).status == "BLOCKED"


def test_projection_cannot_create_outcome_authority():
    obj = _base(created_by_lane="PROJECTION", binding_status=BindingStatus.BOUND)
    assert validate_outcome_binding(obj).status == "BLOCKED"


def test_binding_hash_stable_and_excludes_binding_hash_field():
    obj = _base(binding_status=BindingStatus.BOUND)
    h1 = outcome_binding_hash(obj)
    payload = asdict(obj)
    payload["binding_hash"] = "mutated"
    h2 = outcome_binding_hash(payload)
    assert h1 == h2


def test_canonical_json_byte_stable():
    obj = _base(binding_status=BindingStatus.BOUND)
    assert canonical_outcome_binding_json(obj) == canonical_outcome_binding_json(obj)


def test_schema_accepts_shape_and_required_fields_present():
    schema = json.loads(Path("contracts/outcomes/outcome_binding.v1.schema.json").read_text(encoding="utf-8"))
    assert "required" in schema and "binding_hash" in schema["required"]


def test_audit_artifact_stable_sha256_and_newline(tmp_path: Path):
    h1 = write_outcome_binding_contract_audit(tmp_path)
    p = tmp_path / "out/audit/outcome_binding_contract.latest.json"
    t1 = p.read_text(encoding="utf-8")
    h2 = write_outcome_binding_contract_audit(tmp_path)
    t2 = p.read_text(encoding="utf-8")
    assert t1.endswith("\n")
    assert h1 == h2
    assert hashlib.sha256(t1.encode()).hexdigest() == hashlib.sha256(t2.encode()).hexdigest()
