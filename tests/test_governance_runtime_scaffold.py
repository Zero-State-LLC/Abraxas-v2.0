from core.governance_runtime.authority import assert_lane_allowed, classify_authority_scope
from core.governance_runtime.models import AuthorityScope, GovernanceLane, PromotionState
from core.governance_runtime.receipt import canonical_json, sha256_text
from core.governance_runtime.validator import validate_governance_runtime_scaffold


def test_canonical_json_is_byte_stable() -> None:
    payload = {"b": 2, "a": {"z": 3, "x": 1}}
    first = canonical_json(payload)
    second = canonical_json(payload)
    assert first == second


def test_sha256_hash_is_stable() -> None:
    text = "governance-runtime"
    assert sha256_text(text) == sha256_text(text)


def test_shadow_cannot_claim_forecast_authority() -> None:
    finding = assert_lane_allowed(GovernanceLane.SHADOW, AuthorityScope.FORECAST)
    assert finding is not None
    assert finding.code == "LANE_SCOPE_DENIED"


def test_projection_cannot_claim_inference_authority() -> None:
    finding = assert_lane_allowed(GovernanceLane.PROJECTION, AuthorityScope.INFERENCE)
    assert finding is not None
    assert finding.code == "LANE_SCOPE_DENIED"


def test_unknown_lane_not_computable_or_finding() -> None:
    scope = classify_authority_scope("UNKNOWN", PromotionState.SHADOW_ONLY)
    finding = assert_lane_allowed("UNKNOWN", AuthorityScope.OBSERVATION)
    assert scope == AuthorityScope.NOT_COMPUTABLE or finding is not None


def test_validator_emits_pass_and_deterministic_hash() -> None:
    report_one = validate_governance_runtime_scaffold()
    report_two = validate_governance_runtime_scaffold()
    assert report_one.status == "PASS"
    assert report_one.receipt_hash == report_two.receipt_hash
