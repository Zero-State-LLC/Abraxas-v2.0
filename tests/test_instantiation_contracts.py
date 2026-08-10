import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from core.instantiation import (
    DIMENSIONS,
    build_instantiation_state,
    build_instantiation_transition,
    canonical_state_json,
    canonical_transition_json,
    validate_instantiation_state,
    validate_instantiation_transition,
)

HASH_A = "a" * 64
HASH_B = "b" * 64


def _schema(name: str):
    path = Path("contracts/instantiation") / name
    return json.loads(path.read_text(encoding="utf-8"))


def _dimensions(observed: set[str] | None = None):
    observed = observed or set()
    return [
        {
            "name": name,
            "epistemic_status": "OBSERVED" if name in observed else "NOT_COMPUTABLE",
            "claim_refs": [f"claim:{name}"] if name in observed else [],
            "evidence_refs": [f"evidence:{name}"] if name in observed else [],
            "not_computable_reason": None if name in observed else "fixture evidence absent",
        }
        for name in reversed(DIMENSIONS)
    ]


def _state(state_id="is-t0", observed=None, exposure="UNKNOWN"):
    return build_instantiation_state(
        state_id=state_id,
        construct_id="cfar-fixture",
        construct_hash=HASH_A,
        observation_start="fixture-t0",
        observation_end="fixture-t0",
        dimensions=_dimensions(observed),
        causal_exposure=exposure,
    )


def _change(status="OBSERVED"):
    if status == "NOT_COMPUTABLE":
        return {
            "dimension": "behavioral_consequence",
            "change_kind": "NOT_COMPUTABLE",
            "epistemic_status": "NOT_COMPUTABLE",
            "claim_refs": [],
            "evidence_refs": [],
            "not_computable_reason": "later evidence absent",
        }
    return {
        "dimension": "behavioral_consequence",
        "change_kind": "INCREASED",
        "epistemic_status": status,
        "claim_refs": ["claim:behavior-change"],
        "evidence_refs": ["evidence:fixture-log"],
        "not_computable_reason": None,
    }


def test_state_is_deterministic_schema_valid_and_orders_dimensions():
    first = _state(observed={"symbolic_persistence", "executable_embodiment"})
    second = _state(observed={"symbolic_persistence", "executable_embodiment"})
    validate_instantiation_state(first)
    assert first == second
    assert canonical_state_json(first) == canonical_state_json(second)
    assert [item["name"] for item in first["dimensions"]] == list(DIMENSIONS)
    assert first["aggregate_instantiation_depth"] == "NOT_COMPUTABLE"


def test_epistemic_labels_and_absent_dimensions_survive_round_trip():
    state = _state(observed={"symbolic_persistence"})
    restored = json.loads(json.dumps(state))
    validate_instantiation_state(restored)
    by_name = {item["name"]: item for item in restored["dimensions"]}
    assert by_name["symbolic_persistence"]["epistemic_status"] == "OBSERVED"
    assert by_name["material_consequence"]["epistemic_status"] == "NOT_COMPUTABLE"
    assert by_name["material_consequence"]["not_computable_reason"]


def test_state_requires_each_dimension_exactly_once():
    dimensions = _dimensions()
    dimensions[-1] = dict(dimensions[0])
    with pytest.raises(ValueError, match="exactly once"):
        build_instantiation_state(
            state_id="is-invalid",
            construct_id="cfar-fixture",
            construct_hash=HASH_A,
            observation_start="t0",
            observation_end="t0",
            dimensions=dimensions,
        )


def test_state_schema_rejects_duplicate_or_out_of_order_dimensions():
    validator = Draft202012Validator(_schema("instantiation_state.v1.schema.json"))
    state = _state()

    duplicate = copy.deepcopy(state)
    duplicate["dimensions"][-1] = copy.deepcopy(duplicate["dimensions"][0])
    with pytest.raises(ValidationError):
        validator.validate(duplicate)

    out_of_order = copy.deepcopy(state)
    out_of_order["dimensions"][0], out_of_order["dimensions"][1] = (
        out_of_order["dimensions"][1],
        out_of_order["dimensions"][0],
    )
    with pytest.raises(ValidationError):
        validator.validate(out_of_order)


def test_state_validator_rejects_hash_drift():
    state = _state(observed={"symbolic_persistence"})
    invalid = copy.deepcopy(state)
    invalid["causal_exposure"] = "EXOGENOUS"
    with pytest.raises(ValidationError, match="state_hash"):
        validate_instantiation_state(invalid)


def test_unknown_causal_exposure_never_becomes_independent_attribution():
    transition = build_instantiation_transition(
        transition_id="it-unknown",
        prior_state_id="is-t0",
        prior_state_hash=HASH_A,
        later_state_id="is-t1",
        later_state_hash=HASH_B,
        dimension_changes=[_change()],
        causal_exposure="UNKNOWN",
    )
    validate_instantiation_transition(transition)
    assert transition["causal_exposure"] == "UNKNOWN"
    assert transition["contamination"]["independent_confirmation_eligible"] is False
    assert transition["authority"]["causal_attribution"] is False


def test_abx_mediated_provenance_and_contamination_survive_round_trip():
    transition = build_instantiation_transition(
        transition_id="it-abx",
        prior_state_id="is-t0",
        prior_state_hash=HASH_A,
        later_state_id="is-t1",
        later_state_hash=HASH_B,
        dimension_changes=[_change("INFERRED")],
        causal_exposure="ABX_MEDIATED",
        contamination_reasons=["Abraxas recommended the sandbox perturbation"],
        intervention_ref={"object_id": "intervention-001", "canonical_hash": "c" * 64},
        settlement_ref={"object_id": "settlement-001", "canonical_hash": "d" * 64},
    )
    restored = json.loads(json.dumps(transition))
    validate_instantiation_transition(restored)
    assert restored["causal_exposure"] == "ABX_MEDIATED"
    assert restored["intervention_ref"]["object_id"] == "intervention-001"
    assert restored["contamination"]["feedback_contaminated"] is True
    assert restored["contamination"]["independent_confirmation_eligible"] is False
    assert restored["dimension_changes"][0]["epistemic_status"] == "INFERRED"


def test_abx_mediated_transition_requires_intervention_reference():
    with pytest.raises(ValidationError):
        build_instantiation_transition(
            transition_id="it-abx-invalid",
            prior_state_id="is-t0",
            prior_state_hash=HASH_A,
            later_state_id="is-t1",
            later_state_hash=HASH_B,
            dimension_changes=[_change()],
            causal_exposure="ABX_MEDIATED",
        )


def test_schema_rejects_unknown_promoted_to_independent_confirmation():
    transition = build_instantiation_transition(
        transition_id="it-unknown",
        prior_state_id="is-t0",
        prior_state_hash=HASH_A,
        later_state_id="is-t1",
        later_state_hash=HASH_B,
        dimension_changes=[_change()],
    )
    invalid = copy.deepcopy(transition)
    invalid["contamination"]["independent_confirmation_eligible"] = True
    with pytest.raises(ValidationError):
        validate_instantiation_transition(invalid)


def test_transition_schema_rejects_reasons_without_contamination():
    validator = Draft202012Validator(_schema("instantiation_transition.v1.schema.json"))
    transition = build_instantiation_transition(
        transition_id="it-clean",
        prior_state_id="is-t0",
        prior_state_hash=HASH_A,
        later_state_id="is-t1",
        later_state_hash=HASH_B,
        dimension_changes=[_change()],
    )
    transition["contamination"]["reasons"] = ["inconsistent contamination claim"]
    with pytest.raises(ValidationError):
        validator.validate(transition)


def test_transition_validator_rejects_duplicate_dimension_and_hash_drift():
    transition = build_instantiation_transition(
        transition_id="it-duplicate",
        prior_state_id="is-t0",
        prior_state_hash=HASH_A,
        later_state_id="is-t1",
        later_state_hash=HASH_B,
        dimension_changes=[_change()],
    )
    duplicate = copy.deepcopy(transition)
    duplicate["dimension_changes"].append(copy.deepcopy(duplicate["dimension_changes"][0]))
    with pytest.raises(ValidationError, match="unique"):
        validate_instantiation_transition(duplicate)

    drifted = copy.deepcopy(transition)
    drifted["later_state_ref"]["object_id"] = "is-t2"
    with pytest.raises(ValidationError, match="transition_hash"):
        validate_instantiation_transition(drifted)


def test_not_computable_transition_change_has_no_phantom_evidence():
    transition = build_instantiation_transition(
        transition_id="it-nc",
        prior_state_id="is-t0",
        prior_state_hash=HASH_A,
        later_state_id="is-t1",
        later_state_hash=HASH_B,
        dimension_changes=[_change("NOT_COMPUTABLE")],
    )
    change = transition["dimension_changes"][0]
    assert change["change_kind"] == "NOT_COMPUTABLE"
    assert change["claim_refs"] == []
    assert change["evidence_refs"] == []


def test_transition_canonical_serialization_is_stable():
    kwargs = {
        "transition_id": "it-stable",
        "prior_state_id": "is-t0",
        "prior_state_hash": HASH_A,
        "later_state_id": "is-t1",
        "later_state_hash": HASH_B,
        "dimension_changes": [_change()],
        "contamination_reasons": ["z", "a", "z"],
    }
    first = build_instantiation_transition(**kwargs)
    second = build_instantiation_transition(**kwargs)
    assert first == second
    assert canonical_transition_json(first) == canonical_transition_json(second)
    assert first["contamination"]["reasons"] == ["a", "z"]


def test_three_synthetic_requirement_fixtures_are_present_and_bounded():
    base = Path("input/fixtures/instantiation")
    fixtures = {
        json.loads(path.read_text(encoding="utf-8"))["scenario"]
        for path in sorted(base.glob("*.json"))
    }
    assert fixtures == {
        "state_only",
        "no_intervention_transition",
        "abx_mediated_settlement",
    }
