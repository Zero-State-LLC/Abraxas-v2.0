from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/aal_viz_route_receipt_advisory_alerts_v1"
ALERT_SCHEMA = ROOT / "contracts/canon/aal_viz_route_receipt_advisory_alerts.v1.schema.json"
ACK_SCHEMA = ROOT / "contracts/canon/aal_viz_route_receipt_advisory_acknowledgements.v1.schema.json"
DELTA_BASELINE = ROOT / "out/projections/aal_viz_yggdrasil_topology_delta_intelligence_v1.latest.json"

SEVERITY_ORDER = {"NOT_COMPUTABLE": 0, "INFO": 1, "LOW": 2, "MEDIUM": 3, "HIGH": 4}
SUPPORTED = {"SUPPORTED", "VERIFIED"}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _typed_id(prefix: str, *identity: Any) -> str:
    return f"{prefix}:{_hash(list(identity))}"


def _alert_generation_id(artifact: dict[str, Any]) -> str:
    semantic = copy.deepcopy(artifact)
    semantic.pop("canonical_hash", None)
    semantic["generation"].pop("generated_at", None)
    semantic["generation"].pop("alert_generation_id", None)
    return _hash(semantic)


def _ack_generation_id(artifact: dict[str, Any]) -> str:
    semantic = copy.deepcopy(artifact)
    semantic.pop("canonical_hash", None)
    semantic["generation"].pop("generated_at", None)
    semantic["generation"].pop("acknowledgement_generation_id", None)
    return _hash(semantic)


def _canonical_hash(artifact: dict[str, Any]) -> str:
    return _hash({key: value for key, value in artifact.items() if key != "canonical_hash"})


def _score_tier(score: int) -> str:
    if score <= 49:
        return "BASELINE"
    if score <= 69:
        return "ELEVATED"
    if score <= 84:
        return "HIGH"
    return "CRITICAL"


def _eligibility(candidate: dict[str, Any]) -> list[str]:
    state = candidate["state"]
    severity = candidate["severity"]
    score = candidate["score"]
    confidence = candidate["confidence"]
    classes = set(candidate["structural_classes"])
    complete = candidate["evidence_complete"]
    triggers: list[str] = []
    if (
        state == "NEW"
        and severity == "HIGH"
        and score >= 70
        and confidence in SUPPORTED
        and candidate["affected_surface_ids"]
        and classes
        and complete
    ):
        triggers.append("NEW_CRITICAL_STRUCTURAL_FINDING")
    prior_severity = candidate.get("prior_severity")
    prior_score = candidate.get("prior_score")
    severity_increased = prior_severity is not None and SEVERITY_ORDER[severity] > SEVERITY_ORDER[prior_severity]
    tier_increased_to_high = prior_score is not None and prior_score < 70 <= score
    if state == "PERSISTENT" and (severity_increased or tier_increased_to_high) and severity == "HIGH" or (
        state == "PERSISTENT" and tier_increased_to_high
    ):
        if score >= 70 and confidence in SUPPORTED and complete:
            triggers.append("SEVERITY_ESCALATION")
    for structural_class in (
        "VALIDATOR_COVERAGE_LOSS",
        "BROKEN_PRODUCER_CONSUMER_PATH",
        "OWNERSHIP_DRIFT",
    ):
        if structural_class in classes and score >= 60 and confidence in SUPPORTED and complete:
            triggers.append(structural_class)
    if "TOPOLOGY_FRAGMENTATION" in classes and score >= 70 and confidence in SUPPORTED and complete:
        triggers.append("TOPOLOGY_FRAGMENTATION")
    if "UNEXPECTED_CLUSTER_FUSION" in classes and score >= 60 and confidence in SUPPORTED | {"INFERRED"} and complete:
        triggers.append("UNEXPECTED_CLUSTER_FUSION")
    if (
        state == "PERSISTENT"
        and severity in {"MEDIUM", "HIGH"}
        and score >= 70
        and confidence in SUPPORTED
        and (candidate.get("persistence_seconds_lower_bound") or 0) >= 86400
        and complete
    ):
        triggers.append("PERSISTENT_UNRESOLVED_DAMAGE")
    return sorted(triggers)


def _validate_section(name: str, section: dict[str, Any]) -> None:
    status = section["status"]
    if status == "NOT_COMPUTABLE":
        assert isinstance(section["not_computable_reason"], str)
        assert section["not_computable_reason"]
        assert section["entries"] is None
    else:
        assert section["not_computable_reason"] is None
        assert isinstance(section["entries"], list)
    assert section["validation_findings"] == sorted(section["validation_findings"])
    entries = section["entries"] or []
    assert entries == sorted(entries, key=lambda item: item["receipt_id"])
    for entry in entries:
        assert entry["score_tier"] == _score_tier(entry["score"])
        assert entry["trigger_types"] == sorted(entry["trigger_types"])
        assert entry["affected_surface_ids"] == sorted(entry["affected_surface_ids"])
        assert entry["evidence_refs"] == sorted(entry["evidence_refs"])
        assert entry["resolution_evidence_refs"] == sorted(entry["resolution_evidence_refs"])
        assert entry["suppression_reasons"] == sorted(entry["suppression_reasons"])
        expected_alert = _typed_id(
            "alert",
            "ROUTE_RECEIPT_ADVISORY_ALERTS_POLICY.v1",
            entry["source_ref"]["category"],
            entry["source_ref"]["entity_id"],
        )
        assert entry["alert_id"] == expected_alert
        if name == "resolved_alerts":
            assert entry["lifecycle"] == "RESOLVED"
            assert entry["event_type"] == "RESOLVED"
            assert entry["receipt_disposition"] == "PUBLISH"
            assert entry["resolution_evidence_refs"]
        elif name == "suppressed_candidates":
            assert entry["lifecycle"] == "ACTIVE"
            assert entry["receipt_disposition"] == "SUPPRESS"
            assert entry["suppression_reasons"]
        elif name == "active_alerts":
            assert entry["lifecycle"] == "ACTIVE"
        expected_receipt = _typed_id(
            "receipt",
            entry["alert_id"],
            entry["event_type"],
            entry["receipt_disposition"],
            VALID_PROJECTION["generation"]["delta_generation_id"],
        )
        assert entry["receipt_id"] == expected_receipt


def _validate_projection(artifact: dict[str, Any]) -> None:
    jsonschema.Draft202012Validator(ALERT_SCHEMA_JSON).validate(artifact)
    assert artifact["source_artifacts"] == sorted(artifact["source_artifacts"], key=lambda item: item["id"])
    source_ids = [source["id"] for source in artifact["source_artifacts"]]
    assert len(source_ids) == len(set(source_ids))
    assert artifact["validation_findings"] == sorted(artifact["validation_findings"])
    receipt_ids: list[str] = []
    for name, section in artifact["sections"].items():
        _validate_section(name, section)
        receipt_ids.extend(item["receipt_id"] for item in section["entries"] or [])
        for item in section["entries"] or []:
            assert set(item["evidence_refs"]).issubset(source_ids)
            assert set(item["resolution_evidence_refs"]).issubset(source_ids)
    assert len(receipt_ids) == len(set(receipt_ids))
    sections = artifact["sections"]
    active = sections["active_alerts"]["entries"] or []
    resolved = sections["resolved_alerts"]["entries"] or []
    suppressed = sections["suppressed_candidates"]["entries"] or []
    assert artifact["summary"] == {
        "candidate_count": len(active) + len(suppressed),
        "active_count": len(active),
        "resolved_count": len(resolved),
        "suppressed_count": len(suppressed),
        "not_computable_count": sum(section["status"] == "NOT_COMPUTABLE" for section in sections.values()),
        "published_receipt_count": sum(
            entry["receipt_disposition"] == "PUBLISH"
            for section in sections.values()
            for entry in section["entries"] or []
        ),
        "highest_active_score": max((entry["score"] for entry in active), default=None),
    }
    assert artifact["generation"]["alert_generation_id"] == _alert_generation_id(artifact)
    assert artifact["canonical_hash"] == _canonical_hash(artifact)


def _validate_acknowledgements(artifact: dict[str, Any]) -> None:
    jsonschema.Draft202012Validator(ACK_SCHEMA_JSON).validate(artifact)
    assert artifact["records"] == sorted(artifact["records"], key=lambda item: item["id"])
    assert len({record["id"] for record in artifact["records"]}) == len(artifact["records"])
    for record in artifact["records"]:
        assert record["id"] == _typed_id(
            "ack", record["alert_id"], record["acknowledged_at"], record["operator_ref"]
        )
    assert artifact["generation"]["acknowledgement_generation_id"] == _ack_generation_id(artifact)
    assert artifact["canonical_hash"] == _canonical_hash(artifact)


ALERT_SCHEMA_JSON = _load(ALERT_SCHEMA)
ACK_SCHEMA_JSON = _load(ACK_SCHEMA)
VALID_PROJECTION = _load(FIXTURES / "valid_projection.json")
VALID_ACKNOWLEDGEMENTS = _load(FIXTURES / "valid_acknowledgements.json")


def test_schemas_are_valid_draft_2020_12() -> None:
    jsonschema.Draft202012Validator.check_schema(ALERT_SCHEMA_JSON)
    jsonschema.Draft202012Validator.check_schema(ACK_SCHEMA_JSON)


def test_valid_contract_fixtures_and_hash_vectors() -> None:
    _validate_projection(VALID_PROJECTION)
    _validate_acknowledgements(VALID_ACKNOWLEDGEMENTS)
    vectors = _load(FIXTURES / "deterministic_vectors.json")
    assert vectors["expected_alert_id"] == VALID_PROJECTION["sections"]["suppressed_candidates"]["entries"][0]["alert_id"]
    assert vectors["expected_receipt_id"] == VALID_PROJECTION["sections"]["suppressed_candidates"]["entries"][0]["receipt_id"]
    assert vectors["expected_alert_generation_id"] == VALID_PROJECTION["generation"]["alert_generation_id"]
    assert vectors["expected_canonical_hash"] == VALID_PROJECTION["canonical_hash"]


@pytest.mark.parametrize("case", _load(FIXTURES / "policy_vectors.json")["eligibility"], ids=lambda case: case["name"])
def test_locked_eligibility_matrix(case: dict[str, Any]) -> None:
    assert _eligibility(case["candidate"]) == case["expected_triggers"]


@pytest.mark.parametrize("case", _load(FIXTURES / "policy_vectors.json")["score_tiers"], ids=lambda case: str(case["score"]))
def test_locked_score_tiers(case: dict[str, Any]) -> None:
    assert _score_tier(case["score"]) == case["expected"]


@pytest.mark.parametrize("case", _load(FIXTURES / "policy_vectors.json")["cooldown"], ids=lambda case: case["name"])
def test_locked_cooldown_boundaries(case: dict[str, Any]) -> None:
    if case["resolved"]:
        actual = ("RESOLVED", "PUBLISH")
    elif case["changed"]:
        actual = ("UPDATED", "PUBLISH")
    elif case["elapsed_seconds"] >= 86400:
        actual = ("REFRESHED", "PUBLISH")
    else:
        actual = ("CARRIED_FORWARD", "SUPPRESS")
    assert actual == (case["expected_event"], case["expected_disposition"])


def test_v1_140_baseline_has_no_eligible_candidate() -> None:
    delta = _load(DELTA_BASELINE)
    correlations = {
        item["id"]: item for item in delta["sections"]["finding_correlation"]["entries"]
    }
    priorities = delta["sections"]["review_priorities"]["entries"]
    assert len(priorities) == 162
    for priority in priorities:
        correlation = correlations[priority["source_ref"]["entity_id"]]
        candidate = {
            "state": correlation["state"],
            "severity": priority["severity"],
            "prior_severity": correlation["prior_severity"],
            "score": priority["score"],
            "confidence": priority["confidence"],
            "structural_classes": priority["structural_classes"],
            "affected_surface_ids": priority["affected_surface_ids"],
            "persistence_seconds_lower_bound": correlation["persistence_seconds_lower_bound"],
            "evidence_complete": True,
        }
        assert _eligibility(candidate) == []


def _replace_pointer(document: dict[str, Any], pointer: str, value: Any) -> None:
    target: Any = document
    parts = pointer.lstrip("/").split("/")
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    final = parts[-1]
    if isinstance(target, list):
        target[int(final)] = value
    else:
        target[final] = value


@pytest.mark.parametrize("case", _load(FIXTURES / "invalid_cases.json")["cases"], ids=lambda case: case["name"])
def test_invalid_projection_cases_fail_closed(case: dict[str, Any]) -> None:
    artifact = copy.deepcopy(VALID_PROJECTION)
    _replace_pointer(artifact, case["pointer"], case["value"])
    with pytest.raises((AssertionError, jsonschema.ValidationError)):
        _validate_projection(artifact)


def test_acknowledgement_metadata_is_non_authorizing() -> None:
    artifact = copy.deepcopy(VALID_ACKNOWLEDGEMENTS)
    artifact["authority"]["suppression_allowed"] = True
    with pytest.raises(jsonschema.ValidationError):
        _validate_acknowledgements(artifact)


def test_duplicate_receipt_and_source_ids_fail_closed() -> None:
    duplicate_receipt = copy.deepcopy(VALID_PROJECTION)
    entry = copy.deepcopy(duplicate_receipt["sections"]["suppressed_candidates"]["entries"][0])
    duplicate_receipt["sections"]["active_alerts"]["entries"].append(entry)
    with pytest.raises(AssertionError):
        _validate_projection(duplicate_receipt)

    duplicate_source = copy.deepcopy(VALID_PROJECTION)
    duplicate_source["source_artifacts"].append(copy.deepcopy(duplicate_source["source_artifacts"][0]))
    with pytest.raises(AssertionError):
        _validate_projection(duplicate_source)


def test_dangling_acknowledgement_and_duplicate_ack_id_fail_closed() -> None:
    dangling = copy.deepcopy(VALID_ACKNOWLEDGEMENTS)
    dangling["records"][0]["alert_id"] = "alert:" + "0" * 64
    with pytest.raises(AssertionError):
        assert dangling["records"][0]["alert_id"] in {
            item["alert_id"]
            for section in VALID_PROJECTION["sections"].values()
            for item in section["entries"] or []
        }

    duplicate = copy.deepcopy(VALID_ACKNOWLEDGEMENTS)
    duplicate["records"].append(copy.deepcopy(duplicate["records"][0]))
    with pytest.raises((AssertionError, jsonschema.ValidationError)):
        _validate_acknowledgements(duplicate)


def test_delivery_and_remediation_fields_are_forbidden() -> None:
    artifact = copy.deepcopy(VALID_PROJECTION)
    artifact["delivery_destination"] = "external"
    with pytest.raises(jsonschema.ValidationError):
        _validate_projection(artifact)

    artifact = copy.deepcopy(VALID_PROJECTION)
    artifact["remediation_command"] = "mutate"
    with pytest.raises(jsonschema.ValidationError):
        _validate_projection(artifact)
