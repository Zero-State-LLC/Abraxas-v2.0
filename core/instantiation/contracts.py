"""Deterministic composition contracts for instantiation state and transition.

These objects reference existing CFAR, evidence, forecast, intervention receipt,
and settlement artifacts. They do not replace those contracts or grant authority.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

from core.canonical.json import canonical_dumps, canonical_hash

ROOT = Path(__file__).resolve().parents[2]
STATE_SCHEMA_PATH = (
    ROOT / "contracts" / "instantiation" / "instantiation_state.v1.schema.json"
)
TRANSITION_SCHEMA_PATH = (
    ROOT / "contracts" / "instantiation" / "instantiation_transition.v1.schema.json"
)
INTERVENTION_SCHEMA_PATH = (
    ROOT / "contracts" / "instantiation" / "intervention_declaration.v1.schema.json"
)

DIMENSIONS = (
    "symbolic_persistence",
    "cognitive_penetration",
    "behavioral_consequence",
    "network_propagation",
    "executable_embodiment",
    "economic_institutional_embodiment",
    "material_consequence",
    "recursive_reinforcement",
)
CAUSAL_EXPOSURES = ("EXOGENOUS", "ABX_MEDIATED", "MIXED", "UNKNOWN")

STATE_AUTHORITY = {
    "truth_assignment": False,
    "forecast_authority": False,
    "intervention_authority": False,
    "execution_authority": False,
    "canon_mutation": False,
}
TRANSITION_AUTHORITY = {
    "causal_attribution": False,
    "forecast_authority": False,
    "intervention_authority": False,
    "execution_authority": False,
    "canon_mutation": False,
}
INTERVENTION_AUTHORITY = {
    "declaration_grants_activation": False,
    "forecast_grants_activation": False,
    "work_packet_grants_activation": False,
    "execution_authority": False,
    "canon_mutation": False,
}


def _schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ref(object_id: str, object_hash: str) -> dict[str, str]:
    return {"object_id": object_id, "canonical_hash": object_hash}


def _normalized_strings(values: Sequence[str], *, field: str) -> list[str]:
    normalized = sorted({str(value).strip() for value in values if str(value).strip()})
    if not normalized:
        raise ValueError(f"{field} must contain at least one non-blank value")
    return normalized


def _sealed(payload: dict[str, Any], hash_field: str) -> dict[str, Any]:
    body = dict(payload)
    body.pop(hash_field, None)
    body[hash_field] = canonical_hash(body)
    return body


def _ordered_dimensions(dimensions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_name = {str(item.get("name")): dict(item) for item in dimensions}
    if set(by_name) != set(DIMENSIONS) or len(dimensions) != len(DIMENSIONS):
        raise ValueError("dimensions must contain each canonical dimension exactly once")
    return [by_name[name] for name in DIMENSIONS]


def build_instantiation_state(
    *,
    state_id: str,
    construct_id: str,
    construct_hash: str,
    observation_start: str,
    observation_end: str,
    dimensions: Sequence[Mapping[str, Any]],
    causal_exposure: str = "UNKNOWN",
) -> dict[str, Any]:
    """Build and validate a deterministic InstantiationState.v1 payload."""
    if causal_exposure not in CAUSAL_EXPOSURES:
        raise ValueError(f"unsupported causal exposure: {causal_exposure}")
    payload: dict[str, Any] = {
        "schema_version": "InstantiationState.v1",
        "state_id": state_id,
        "construct_ref": _ref(construct_id, construct_hash),
        "observation_window": {"start": observation_start, "end": observation_end},
        "dimensions": _ordered_dimensions(dimensions),
        "causal_exposure": causal_exposure,
        "aggregate_instantiation_depth": "NOT_COMPUTABLE",
        "authority": dict(STATE_AUTHORITY),
        "state_hash": "",
    }
    sealed = _sealed(payload, "state_hash")
    validate_instantiation_state(sealed)
    return sealed


def build_instantiation_transition(
    *,
    transition_id: str,
    prior_state_id: str,
    prior_state_hash: str,
    later_state_id: str,
    later_state_hash: str,
    dimension_changes: Sequence[Mapping[str, Any]],
    causal_exposure: str = "UNKNOWN",
    contamination_reasons: Sequence[str] = (),
    forecast_ref: Mapping[str, str] | None = None,
    intervention_ref: Mapping[str, str] | None = None,
    settlement_ref: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build and validate a deterministic InstantiationTransition.v1 payload."""
    if causal_exposure not in CAUSAL_EXPOSURES:
        raise ValueError(f"unsupported causal exposure: {causal_exposure}")
    contaminated = causal_exposure in {"ABX_MEDIATED", "MIXED"} or bool(
        contamination_reasons
    )
    reasons = sorted({str(reason) for reason in contamination_reasons if str(reason)})
    if contaminated and not reasons:
        reasons = ["ABX-mediated or mixed exposure requires contamination review"]
    payload: dict[str, Any] = {
        "schema_version": "InstantiationTransition.v1",
        "transition_id": transition_id,
        "prior_state_ref": _ref(prior_state_id, prior_state_hash),
        "later_state_ref": _ref(later_state_id, later_state_hash),
        "dimension_changes": sorted(
            (dict(item) for item in dimension_changes),
            key=lambda item: DIMENSIONS.index(str(item["dimension"])),
        ),
        "causal_exposure": causal_exposure,
        "contamination": {
            "feedback_contaminated": contaminated,
            "reasons": reasons,
            "independent_confirmation_eligible": False,
        },
        "forecast_ref": dict(forecast_ref) if forecast_ref else None,
        "intervention_ref": dict(intervention_ref) if intervention_ref else None,
        "settlement_ref": dict(settlement_ref) if settlement_ref else None,
        "authority": dict(TRANSITION_AUTHORITY),
        "transition_hash": "",
    }
    sealed = _sealed(payload, "transition_hash")
    validate_instantiation_transition(sealed)
    return sealed


def build_intervention_declaration(
    *,
    intervention_id: str,
    construct_ref: Mapping[str, str],
    baseline_state_ref: Mapping[str, str],
    work_packet_ref: Mapping[str, str],
    forecast_ref: Mapping[str, str],
    activation_evidence_ref: Mapping[str, str],
    predicted_dimension_changes: Sequence[Mapping[str, Any]],
    constraints: Sequence[str],
    falsification_criteria: Sequence[str],
    provenance_refs: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Build a bounded declaration that never grants intervention authority."""
    changes = sorted(
        (dict(item) for item in predicted_dimension_changes),
        key=lambda item: DIMENSIONS.index(str(item["dimension"])),
    )
    dimensions = [str(item["dimension"]) for item in changes]
    if len(dimensions) != len(set(dimensions)):
        raise ValueError("predicted_dimension_changes must target unique dimensions")
    payload: dict[str, Any] = {
        "schema_version": "InterventionDeclaration.v1",
        "intervention_id": intervention_id,
        "construct_ref": dict(construct_ref),
        "baseline_state_ref": dict(baseline_state_ref),
        "work_packet_ref": dict(work_packet_ref),
        "forecast_ref": dict(forecast_ref),
        "activation_evidence_ref": dict(activation_evidence_ref),
        "target_dimensions": dimensions,
        "predicted_dimension_changes": changes,
        "constraints": _normalized_strings(constraints, field="constraints"),
        "falsification_criteria": _normalized_strings(
            falsification_criteria, field="falsification_criteria"
        ),
        "provenance_refs": sorted(
            {
                (str(item["object_id"]), str(item["canonical_hash"]))
                for item in provenance_refs
            },
            key=lambda item: item,
        ),
        "authority": dict(INTERVENTION_AUTHORITY),
        "intervention_hash": "",
    }
    payload["provenance_refs"] = [
        {"object_id": object_id, "canonical_hash": object_hash}
        for object_id, object_hash in payload["provenance_refs"]
    ]
    for change in payload["predicted_dimension_changes"]:
        change["claim_refs"] = _normalized_strings(
            change["claim_refs"], field="claim_refs"
        ) if change["epistemic_status"] != "NOT_COMPUTABLE" else []
    sealed = _sealed(payload, "intervention_hash")
    validate_intervention_declaration(sealed)
    return sealed


def validate_instantiation_state(payload: Mapping[str, Any]) -> None:
    data = dict(payload)
    Draft202012Validator(_schema(STATE_SCHEMA_PATH)).validate(data)
    dimensions = data["dimensions"]
    names = [item["name"] for item in dimensions]
    if names != list(DIMENSIONS):
        raise ValidationError("dimensions must be in canonical order and unique")
    expected_hash = canonical_hash({key: value for key, value in data.items() if key != "state_hash"})
    if data["state_hash"] != expected_hash:
        raise ValidationError("state_hash does not match canonical payload")


def validate_instantiation_transition(payload: Mapping[str, Any]) -> None:
    data = dict(payload)
    Draft202012Validator(_schema(TRANSITION_SCHEMA_PATH)).validate(data)
    dimensions = [item["dimension"] for item in data["dimension_changes"]]
    expected_order = sorted(dimensions, key=DIMENSIONS.index)
    if dimensions != expected_order or len(dimensions) != len(set(dimensions)):
        raise ValidationError("dimension_changes must be in canonical order and unique")
    expected_hash = canonical_hash(
        {key: value for key, value in data.items() if key != "transition_hash"}
    )
    if data["transition_hash"] != expected_hash:
        raise ValidationError("transition_hash does not match canonical payload")


def validate_intervention_declaration(payload: Mapping[str, Any]) -> None:
    data = dict(payload)
    Draft202012Validator(_schema(INTERVENTION_SCHEMA_PATH)).validate(data)
    dimensions = [item["dimension"] for item in data["predicted_dimension_changes"]]
    expected_order = sorted(dimensions, key=DIMENSIONS.index)
    if dimensions != expected_order or len(dimensions) != len(set(dimensions)):
        raise ValidationError(
            "predicted_dimension_changes must be in canonical order and unique"
        )
    if data["target_dimensions"] != dimensions:
        raise ValidationError(
            "target_dimensions must exactly match predicted_dimension_changes"
        )
    expected_hash = canonical_hash(
        {key: value for key, value in data.items() if key != "intervention_hash"}
    )
    if data["intervention_hash"] != expected_hash:
        raise ValidationError("intervention_hash does not match canonical payload")


def canonical_state_json(payload: Mapping[str, Any]) -> str:
    body = dict(payload)
    body.pop("state_hash", None)
    return canonical_dumps(body)


def canonical_transition_json(payload: Mapping[str, Any]) -> str:
    body = dict(payload)
    body.pop("transition_hash", None)
    return canonical_dumps(body)


def canonical_intervention_json(payload: Mapping[str, Any]) -> str:
    body = dict(payload)
    body.pop("intervention_hash", None)
    return canonical_dumps(body)
