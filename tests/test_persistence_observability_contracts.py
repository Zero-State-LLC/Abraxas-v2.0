from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "contracts" / "evaluation"
SCHEMAS = {
    "claim": CONTRACT_ROOT / "persisted_claim.v1.schema.json",
    "packet": CONTRACT_ROOT / "state_qualified_evidence_packet.v1.schema.json",
    "observation": CONTRACT_ROOT / "trajectory_observation.v1.schema.json",
    "receipt": CONTRACT_ROOT / "persistence_observability_receipt.v1.schema.json",
}
HASH = "a" * 64


def _schema(name: str) -> dict[str, Any]:
    return json.loads(SCHEMAS[name].read_text(encoding="utf-8"))


def _validate(name: str, payload: dict[str, Any]) -> None:
    Draft202012Validator(
        _schema(name), format_checker=FormatChecker()
    ).validate(payload)


def _authority() -> dict[str, bool]:
    return {
        "advisory_only": True,
        "execution_authority": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "production_activation_allowed": False,
    }


def _claim() -> dict[str, Any]:
    return {
        "schema_version": "PersistedClaim.v1",
        "claim_id": "pc-subject-status-002",
        "subject_id": "subject-001",
        "predicate": "operational_status",
        "value_digest": HASH,
        "valid_from": "2026-09-25T15:00:00Z",
        "valid_to": None,
        "recorded_at": "2026-09-25T15:00:01Z",
        "source_ref": "fixture://history-001/event-002",
        "authority_tier": "PRIMARY",
        "supersedes_claim_id": "pc-subject-status-001",
        "revoked_at": None,
        "revocation_ref": None,
        "content_classification": "INTERNAL",
        "retention_class": "STANDARD",
        "epistemic_status": "OBSERVED",
        "authority": _authority(),
    }


def _packet() -> dict[str, Any]:
    return {
        "schema_version": "StateQualifiedEvidencePacket.v1",
        "evaluation_id": "eval-history-001-seed-0",
        "as_of": "2026-09-25T15:30:00Z",
        "query_digest": HASH,
        "resolution_status": "READY",
        "claims": [
            {
                "claim_ref": "pc-subject-status-002",
                "temporal_role": "CURRENT",
                "inclusion": "INCLUDED",
                "reason_code": "CURRENT_PRIMARY",
                "authority_conflict": False,
            },
            {
                "claim_ref": "pc-subject-status-001",
                "temporal_role": "SUPERSEDED",
                "inclusion": "EXCLUDED",
                "reason_code": "SUPERSEDED_BY_CURRENT",
                "authority_conflict": False,
            },
        ],
        "not_computable_reasons": [],
        "packet_digest": HASH,
        "authority": _authority(),
    }


def _observation() -> dict[str, Any]:
    return {
        "schema_version": "TrajectoryObservation.v1",
        "trace_id": "trace-001",
        "span_id": "span-001",
        "step_index": 0,
        "timestamp": "2026-09-25T15:30:01Z",
        "layer": "RETRIEVAL",
        "input_digest": HASH,
        "output_digest": HASH,
        "permitted_metadata": {
            "model_id": "fixture-evaluator",
            "latency_ms": 4,
            "token_count": 12,
        },
        "anomaly_codes": [],
        "recoverability": "NOT_RECOVERABLE",
        "recovery_action_ref": None,
        "evidence_refs": [],
        "evaluator": {
            "evaluator_id": "persistence-layer-scorer",
            "version": "1.0.0",
        },
        "authority": _authority(),
    }


def _metric() -> dict[str, Any]:
    return {"status": "PASS", "score": 1.0, "anomaly_codes": []}


def _receipt() -> dict[str, Any]:
    return {
        "schema_version": "PersistenceObservabilityReceipt.v1",
        "receipt_id": "por-history-001-seed-0",
        "fixture": {
            "fixture_id": "persistence-observability-synthetic",
            "fixture_version": "1.0.0",
            "scenario_id": "history-001",
            "seed": 0,
        },
        "run_id": "run-history-001-seed-0",
        "contract_versions": {
            "persisted_claim": "PersistedClaim.v1",
            "evidence_packet": "StateQualifiedEvidencePacket.v1",
            "trajectory_observation": "TrajectoryObservation.v1",
            "receipt": "PersistenceObservabilityReceipt.v1",
        },
        "evaluator_versions": [
            {"evaluator_id": "persistence-layer-scorer", "version": "1.0.0"}
        ],
        "layer_metrics": {
            "store": _metric(),
            "retrieval": _metric(),
            "interpretation": _metric(),
            "answer": _metric(),
        },
        "failed_acceptance_tests": [],
        "provenance_refs": [
            "fixture://persistence-observability-synthetic/1.0.0/history-001"
        ],
        "privacy_redaction_result": "PASS",
        "determinism_result": "PASS",
        "lane": "SHADOW",
        "forecast_binding": None,
        "terminal_state": "SHADOW_PASS",
        "research_disposition": "CANON_SHADOW",
        "disposition_reason": "Bounded contract fixture; no promotion authority.",
        "canonical_hash": HASH,
        "authority": _authority(),
    }


def test_schemas_are_valid_draft_2020_12() -> None:
    for path in SCHEMAS.values():
        Draft202012Validator.check_schema(
            json.loads(path.read_text(encoding="utf-8"))
        )


@pytest.mark.parametrize(
    ("name", "payload"),
    [
        ("claim", _claim()),
        ("packet", _packet()),
        ("observation", _observation()),
        ("receipt", _receipt()),
    ],
)
def test_positive_contract_fixtures(name: str, payload: dict[str, Any]) -> None:
    _validate(name, payload)


def test_claim_requires_exactly_one_safe_value_representation() -> None:
    payload = _claim()
    payload["approved_redacted_value"] = "approved summary"
    with pytest.raises(ValidationError):
        _validate("claim", payload)

    payload = _claim()
    payload.pop("value_digest")
    payload["approved_redacted_value"] = "approved summary"
    _validate("claim", payload)


def test_claim_revocation_fields_are_coupled() -> None:
    payload = _claim()
    payload["revoked_at"] = "2026-09-25T15:10:00Z"
    with pytest.raises(ValidationError):
        _validate("claim", payload)


def test_packet_excludes_superseded_and_revoked_claims() -> None:
    payload = _packet()
    payload["claims"][1]["inclusion"] = "INCLUDED"
    with pytest.raises(ValidationError):
        _validate("packet", payload)


def test_not_computable_packet_requires_a_reason() -> None:
    payload = _packet()
    payload["resolution_status"] = "NOT_COMPUTABLE"
    with pytest.raises(ValidationError):
        _validate("packet", payload)


def test_observation_rejects_raw_content_metadata() -> None:
    payload = _observation()
    payload["permitted_metadata"]["raw_prompt"] = "prohibited"
    with pytest.raises(ValidationError):
        _validate("observation", payload)


def test_recoverable_observation_requires_action_and_evidence() -> None:
    payload = _observation()
    payload["recoverability"] = "RECOVERABLE"
    with pytest.raises(ValidationError):
        _validate("observation", payload)


def test_shadow_receipt_rejects_forecast_binding() -> None:
    payload = _receipt()
    payload["forecast_binding"] = {
        "probability": 0.7,
        "horizon": "P7D",
        "outcome_ref": "outcome://example",
    }
    with pytest.raises(ValidationError):
        _validate("receipt", payload)


def test_forecast_receipt_requires_bound_outcome() -> None:
    payload = _receipt()
    payload["lane"] = "FORECAST"
    payload["research_disposition"] = "MERGE_CANDIDATE"
    with pytest.raises(ValidationError):
        _validate("receipt", payload)


def test_shadow_pass_rejects_failed_tests() -> None:
    payload = _receipt()
    payload["failed_acceptance_tests"] = ["AT-001"]
    with pytest.raises(ValidationError):
        _validate("receipt", payload)


def test_contracts_reject_authority_escalation() -> None:
    for name, payload in [
        ("claim", _claim()),
        ("packet", _packet()),
        ("observation", _observation()),
        ("receipt", _receipt()),
    ]:
        escalated = copy.deepcopy(payload)
        escalated["authority"]["runtime_mutation_allowed"] = True
        with pytest.raises(ValidationError):
            _validate(name, escalated)


def test_contracts_reject_unknown_top_level_fields() -> None:
    for name, payload in [
        ("claim", _claim()),
        ("packet", _packet()),
        ("observation", _observation()),
        ("receipt", _receipt()),
    ]:
        extended = copy.deepcopy(payload)
        extended["unexpected"] = True
        with pytest.raises(ValidationError):
            _validate(name, extended)
