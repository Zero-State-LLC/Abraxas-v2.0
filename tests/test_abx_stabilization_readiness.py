from __future__ import annotations

import importlib
import json
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from core.campaign_director.stabilization_campaign import (
    CampaignClass,
    StabilizationEntryDecision,
    StabilizationPhase,
    route_stabilization_campaign,
)

PACKAGE = "skills.abx-stabilization-readiness"
BASELINE = "ceb848124677072da93bbea1f83428acf492963f"
REPO_ROOT = Path(__file__).resolve().parents[1]


def _module(name: str) -> Any:
    return importlib.import_module(f"{PACKAGE}.{name}")


def _all_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key)
            yield from _all_strings(item)
    elif isinstance(value, Iterable):
        for item in value:
            yield from _all_strings(item)


def _complete_evidence(**overrides: Any) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "python_ready": True,
        "typescript_ready": True,
        "contract_inventory_complete": True,
        "conformance_corpus_ready": True,
        "reproducibility_ready": True,
        "canonical_artifact_safety_ready": True,
        "full_suite_confidence": "FOCUSED_AND_FAST_CI_PASS",
        "blocking_findings": [],
        "bounded_exceptions": [],
        "evidence_refs": ["focused-tests", "fast-ci"],
    }
    evidence.update(overrides)
    return evidence


def test_package_import_has_no_publication_side_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    before = set(tmp_path.rglob("*"))

    imported = importlib.import_module(PACKAGE)

    assert imported is not None
    assert set(tmp_path.rglob("*")) == before


def test_campaign_class_routes_without_starting_campaign() -> None:
    route = route_stabilization_campaign(CampaignClass.STABILIZATION_READINESS)
    assert route["campaign_class"] == "STABILIZATION_READINESS"
    assert route["automatic_start_allowed"] is False
    assert route["feature_expansion_allowed"] is False
    assert route["phases"] == [phase.value for phase in StabilizationPhase]


def test_campaign_route_rejects_other_classes() -> None:
    with pytest.raises(ValueError, match="unsupported campaign class"):
        route_stabilization_campaign("FEATURE_DEVELOPMENT")


def test_state_phase_and_authority_are_validated() -> None:
    director = _module("director")
    contracts = _module("contracts")
    state = director.build_stabilization_state(BASELINE)
    assert state.phase == StabilizationPhase.BASELINE_DISCOVERY
    assert state.feature_expansion_allowed is False
    assert state.authority.is_locked()
    contracts.validate_stabilization_state(state)
    with pytest.raises(ValueError, match="invalid stabilization phase"):
        director.build_stabilization_state(BASELINE, phase="PHASE.99_UNKNOWN")


def test_contract_classification_and_not_computable_are_preserved() -> None:
    inventory_module = _module("contract_inventory")
    inventory = inventory_module.build_contract_inventory()
    typescript = next(
        item for item in inventory["contracts"] if item["language"] == "typescript"
    )
    assert typescript["classification"] == "CONTRACT.NOT_COMPUTABLE"
    assert typescript["evidence_complete"] is False
    assert inventory["inventory_status"] == "INCOMPLETE"


def test_invalid_contract_classification_is_rejected() -> None:
    contracts = _module("contracts")
    with pytest.raises(ValueError, match="invalid contract classification"):
        contracts.validate_contract_record(
            {
                "contract_id": "bad",
                "language": "python",
                "surface": "bad.surface",
                "classification": "CONTRACT.FABRICATED",
                "provenance": "OBSERVED",
            }
        )


def test_reproducibility_missing_evidence_is_not_computable() -> None:
    auditor = _module("reproducibility_auditor")
    result = auditor.audit_reproducibility()
    assert result["outcome"] == "NOT_COMPUTABLE"
    assert result["ready"] is False
    assert all(check["outcome"] == "NOT_COMPUTABLE" for check in result["checks"])


def test_reproducibility_outcome_validation() -> None:
    contracts = _module("contracts")
    contracts.validate_reproducibility_outcome("REPRODUCIBLE")
    with pytest.raises(ValueError, match="invalid reproducibility outcome"):
        contracts.validate_reproducibility_outcome("PASS")


def test_conformance_modes_and_foundation_cases() -> None:
    contracts = _module("contracts")
    harness = _module("conformance_harness")
    contracts.validate_comparison_mode("BYTE_EXACT")
    with pytest.raises(ValueError, match="invalid conformance comparison mode"):
        contracts.validate_comparison_mode("APPROXIMATE")
    manifest = harness.run_conformance_cases()
    assert manifest["case_count"] == 6
    assert manifest["passed_count"] == 6
    assert manifest["typescript_equivalence_claimed"] is False


def test_gate_holds_when_evidence_is_missing() -> None:
    gate = _module("stabilization_gate")
    decision = gate.evaluate_stabilization_entry({}).to_dict()
    assert decision["decision"] == StabilizationEntryDecision.HELD
    assert decision["operator_action_required"] is True
    assert decision["blocking_findings"]


def test_gate_allows_ready_recommendation_without_granting_authority() -> None:
    gate = _module("stabilization_gate")
    decision = gate.evaluate_stabilization_entry(_complete_evidence()).to_dict()
    assert decision["decision"] == StabilizationEntryDecision.READY
    assert decision["operator_action_required"] is True


def test_gate_classifies_bounded_exceptions() -> None:
    gate = _module("stabilization_gate")
    decision = gate.evaluate_stabilization_entry(
        _complete_evidence(bounded_exceptions=["typescript lint script unavailable"])
    ).to_dict()
    assert decision["decision"] == (
        StabilizationEntryDecision.READY_WITH_BOUNDED_EXCEPTIONS
    )


def test_gate_holds_when_supplied_authority_is_permissive() -> None:
    gate = _module("stabilization_gate")
    decision = gate.evaluate_stabilization_entry(
        _complete_evidence(authority={"production_activation": True})
    ).to_dict()
    assert decision["decision"] == StabilizationEntryDecision.HELD
    assert decision["blocking_findings"] == [
        "AUTHORITY_NOT_LOCKED:production_activation"
    ]


def test_gate_accepts_explicitly_locked_advisory_authority() -> None:
    gate = _module("stabilization_gate")
    decision = gate.evaluate_stabilization_entry(
        _complete_evidence(
            authority={"advisory_only": True, "production_activation": False}
        )
    ).to_dict()
    assert decision["decision"] == StabilizationEntryDecision.READY
    assert decision["blocking_findings"] == []


def test_state_and_artifact_publication_are_deterministic(tmp_path: Path) -> None:
    director = _module("director")
    state_one = director.build_stabilization_state(BASELINE)
    state_two = director.build_stabilization_state(BASELINE)
    assert state_one.deterministic_hash() == state_two.deterministic_hash()

    director.emit_foundation_artifacts(tmp_path, baseline_commit=BASELINE)
    first = {path.name: path.read_bytes() for path in tmp_path.glob("*.json")}
    director.emit_foundation_artifacts(tmp_path, baseline_commit=BASELINE)
    second = {path.name: path.read_bytes() for path in tmp_path.glob("*.json")}
    assert first == second


def test_director_uses_canonical_writer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    director = _module("director")
    calls: list[Path] = []

    def record(path: Path, _value: Any) -> None:
        calls.append(path)

    monkeypatch.setattr(director, "write_canonical_json", record)
    director.emit_foundation_artifacts(tmp_path, baseline_commit=BASELINE)
    assert sorted(path.name for path in calls) == sorted(director.ARTIFACT_NAMES)


def test_generated_and_committed_artifacts_have_no_absolute_paths(tmp_path: Path) -> None:
    director = _module("director")
    director.emit_foundation_artifacts(tmp_path, baseline_commit=BASELINE)
    fixture = json.loads(
        (REPO_ROOT / "skills/abx-stabilization-readiness/fixtures/foundation_cases.v1.json").read_text(
            encoding="utf-8"
        )
    )
    payloads = [fixture]
    payloads.extend(
        json.loads(path.read_text(encoding="utf-8")) for path in tmp_path.glob("*.json")
    )
    assert not any(text.startswith("/") for payload in payloads for text in _all_strings(payload))


def test_state_and_gate_match_json_schemas() -> None:
    director = _module("director")
    gate = _module("stabilization_gate")
    contract_root = REPO_ROOT / "contracts/stabilization_readiness"
    state_schema = json.loads(
        (contract_root / "stabilization_state.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    gate_schema = json.loads(
        (contract_root / "stabilization_entry_gate.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(director.build_stabilization_state(BASELINE).to_dict(), state_schema)
    jsonschema.validate(
        gate.evaluate_stabilization_entry(_complete_evidence()).to_dict(), gate_schema
    )


def test_stabilization_metrics_preserve_null_missing_and_bounded_values() -> None:
    evolution_path = REPO_ROOT / "skills/abx-hermes-skill-evolution"
    sys.path.insert(0, str(evolution_path))
    try:
        contracts = importlib.import_module("abx_skill_stabilization_evolution_contracts")
        empty = contracts.empty_stabilization_metrics()
        metrics = contracts.normalize_stabilization_metrics(
            {
                "determinism_rate": None,
                "clean_worktree_rate": 0.0,
                "contract_compatibility_rate": 1.0,
                "replay_pass_rate": 0.625,
            }
        )
    finally:
        sys.path.remove(str(evolution_path))
    assert all(value is None for value in empty.values())
    assert metrics["determinism_rate"] is None
    assert metrics["clean_worktree_rate"] == 0.0
    assert metrics["contract_compatibility_rate"] == 1.0
    assert metrics["replay_pass_rate"] == 0.625
    assert metrics["flake_rate"] is None


@pytest.mark.parametrize("value", [-0.1, 1.1, "0.5", True, float("nan")])
def test_stabilization_metrics_reject_invalid_values(value: Any) -> None:
    evolution_path = REPO_ROOT / "skills/abx-hermes-skill-evolution"
    sys.path.insert(0, str(evolution_path))
    try:
        contracts = importlib.import_module("abx_skill_stabilization_evolution_contracts")
        with pytest.raises(ValueError, match="stabilization metric"):
            contracts.normalize_stabilization_metrics({"determinism_rate": value})
    finally:
        sys.path.remove(str(evolution_path))


def test_stabilization_metrics_schema_matches_runtime_validation() -> None:
    evolution_path = REPO_ROOT / "skills/abx-hermes-skill-evolution"
    sys.path.insert(0, str(evolution_path))
    try:
        contracts = importlib.import_module("abx_skill_stabilization_evolution_contracts")
        metrics_schema = json.loads(
            (
                REPO_ROOT
                / "contracts/stabilization_readiness/stabilization_metrics.v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        for payload in (
            {},
            {"determinism_rate": None},
            {"determinism_rate": 0.0},
            {"determinism_rate": 1.0},
            {"determinism_rate": 0.5},
        ):
            jsonschema.validate(payload, metrics_schema)
            contracts.normalize_stabilization_metrics(payload)
        for payload in (
            {"determinism_rate": -0.1},
            {"determinism_rate": 1.1},
            {"determinism_rate": "0.5"},
            {"unknown_rate": 0.5},
        ):
            with pytest.raises(jsonschema.ValidationError):
                jsonschema.validate(payload, metrics_schema)
            with pytest.raises(ValueError):
                contracts.normalize_stabilization_metrics(payload)
    finally:
        sys.path.remove(str(evolution_path))


def test_minimal_compatibility_patch_rejects_broad_sweeps() -> None:
    evolution_path = REPO_ROOT / "skills/abx-hermes-skill-evolution"
    sys.path.insert(0, str(evolution_path))
    try:
        contracts = importlib.import_module("abx_skill_stabilization_evolution_contracts")
        candidate = {
            "failure_class": "FAILURE.CLASS.CONTRACT_DRIFT",
            "exact_regression_test": "tests/test_contract.py::test_compatibility",
        }
        patch = contracts.build_minimal_compatibility_patch(candidate)
        assert patch["patch_mode"] == "PATCH_MODE.MINIMAL_COMPATIBILITY_REPAIR"
        assert patch["authority_conferred"] is False
        with pytest.raises(ValueError, match="broad sweeps"):
            contracts.build_minimal_compatibility_patch(
                {**candidate, "broad_sweep": True}
            )
    finally:
        sys.path.remove(str(evolution_path))


def test_operator_decision_types_are_validation_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    evolution_path = REPO_ROOT / "skills/abx-hermes-skill-evolution"
    sys.path.insert(0, str(evolution_path))
    try:
        contracts = importlib.import_module("abx_skill_stabilization_evolution_contracts")
        validator = importlib.import_module("abx_skill_formal_operator_decision_validator")
    finally:
        sys.path.remove(str(evolution_path))
    assert contracts.STABILIZATION_OPERATOR_DECISIONS <= validator.ALLOWED_DECISIONS
    output_root = tmp_path / "audit"
    operator_root = tmp_path / "operator_input"
    output_root.mkdir()
    operator_root.mkdir()
    decision_path = operator_root / "decision.json"
    review_path = output_root / "review.json"
    review_path.write_text(
        json.dumps({"formal_review_id": "stabilization-review", "deterministic_hash": "h1"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "OUT", output_root)
    monkeypatch.setattr(validator, "OPERATOR_DIR", operator_root)
    monkeypatch.setattr(validator, "COMPLETED_PATH", decision_path)
    monkeypatch.setattr(validator, "REVIEW_PACKET_PATH", review_path)
    decision_schema = json.loads(
        (
            REPO_ROOT
            / "contracts/stabilization_readiness/"
            "stabilization_operator_decision.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    for decision_value in sorted(contracts.STABILIZATION_OPERATOR_DECISIONS):
        decision_payload = {
            "formal_review_id": "stabilization-review",
            "review_packet_hash": "h1",
            "decision_value": decision_value,
            "acknowledgements": {key: True for key in validator.REQUIRED_ACKS},
            "authority_boundary": {
                "promotion_authorized": False,
                "production_activation_allowed": False,
                "active_skill_replacement_allowed": False,
                "automatic_transition_allowed": False,
            },
            "operator": {
                "operator_id": "test-operator",
                "operator_display_name": "Test Operator",
            },
        }
        jsonschema.validate(decision_payload, decision_schema)
        decision_path.write_text(
            json.dumps(decision_payload),
            encoding="utf-8",
        )
        result = validator.main()
        assert result["status"] == "VALIDATED"
        assert result["authority_all_blocked"] is True
    invalid_authority = {**decision_payload}
    invalid_authority["authority_boundary"] = {
        **decision_payload["authority_boundary"],
        "production_activation_allowed": True,
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(invalid_authority, decision_schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {
                "decision_value": "HOLD_STABILIZATION_ENTRY",
                "authority_boundary": decision_payload["authority_boundary"],
            },
            decision_schema,
        )
    assert contracts.empty_stabilization_metrics()["determinism_rate"] is None
