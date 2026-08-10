"""RDI-5 synthetic fixture experiment harness.

Runs the canonical experiment loop over synthetic fixtures only:

    define H -> state t0 -> declared forecast (and optional intervention
    declaration) -> evidence t1 -> transition -> settlement -> calibration

Every stage reuses an existing contract builder: instantiation state and
transition (`core/instantiation/contracts.py`), ForecastObject.v1
(`core/forecasting/`), InterventionDeclaration.v1, SettlementVerdict.v1 via
the outcome-binding bridge (`core/settlement/binding_bridge.py`), and Brier
score telemetry (`core/brier/scores.py`).

Boundaries (PLANS.md RDI-5, RDI doctrine sections 8/11/12):
- synthetic fixtures only; no production or social-world intervention;
- calibration is telemetry, never authority and never empirical validation;
- contaminated outcomes may settle and score, but are never marked as
  independent confirmation;
- anything the fixture does not evidence stays ``NOT_COMPUTABLE``;
- the record grants no authority and the harness writes nothing to disk.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict
from typing import Any

from core.brier.scores import BrierScorePacket
from core.canonical.json import canonical_hash
from core.forecasting.forecast_object import build_forecast_object, validate_forecast_object
from core.forecasting.models import OutcomeBindingStatus
from core.settlement.binding_bridge import (
    is_score_ready,
    observed_outcome_from_verdict,
    settlement_verdict_from_outcome_binding,
)
from core.settlement.models import AuthorityRef
from core.settlement.verdict import validate_settlement_verdict

from .contracts import (
    DIMENSIONS,
    build_instantiation_state,
    build_instantiation_transition,
    build_intervention_declaration,
)
from .shadow import detect_instantiation_anomalies

SCHEMA_VERSION = "InstantiationExperimentRecord.v1"

EXPERIMENT_AUTHORITY = {
    "empirical_validation": False,
    "forecast_authority": False,
    "intervention_authority": False,
    "execution_authority": False,
    "canon_mutation": False,
}

_REQUIRED_KEYS = (
    "experiment_id",
    "construct",
    "baseline",
    "forecast",
    "observed",
    "binding",
)


def _require(spec: Mapping[str, Any]) -> None:
    missing = [key for key in _REQUIRED_KEYS if key not in spec]
    if missing:
        raise ValueError(f"experiment spec missing required keys: {missing}")


def _dimensions_from_observed(observed: set[str], reason: str) -> list[dict[str, Any]]:
    unknown = observed - set(DIMENSIONS)
    if unknown:
        raise ValueError(f"unknown dimensions in fixture: {sorted(unknown)}")
    return [
        {
            "name": name,
            "epistemic_status": "OBSERVED" if name in observed else "NOT_COMPUTABLE",
            "claim_refs": [f"fixture:claim:{name}"] if name in observed else [],
            "evidence_refs": [f"fixture:evidence:{name}"] if name in observed else [],
            "not_computable_reason": None if name in observed else reason,
        }
        for name in DIMENSIONS
    ]


def _state_from_spec(spec: Mapping[str, Any], construct: Mapping[str, str]) -> dict[str, Any]:
    return build_instantiation_state(
        state_id=spec["state_id"],
        construct_id=construct["construct_id"],
        construct_hash=construct["construct_hash"],
        observation_start=spec["window"],
        observation_end=spec["window"],
        dimensions=_dimensions_from_observed(
            set(spec.get("observed_dimensions", ())),
            reason="fixture evidence absent",
        ),
        causal_exposure=spec.get("causal_exposure", "UNKNOWN"),
    )


def _changes_from_spec(changes: list[Mapping[str, str]]) -> list[dict[str, Any]]:
    built: list[dict[str, Any]] = []
    for change in changes:
        if change["change_kind"] == "NOT_COMPUTABLE":
            built.append(
                {
                    "dimension": change["dimension"],
                    "change_kind": "NOT_COMPUTABLE",
                    "epistemic_status": "NOT_COMPUTABLE",
                    "claim_refs": [],
                    "evidence_refs": [],
                    "not_computable_reason": change.get(
                        "not_computable_reason", "fixture evidence absent"
                    ),
                }
            )
        else:
            built.append(
                {
                    "dimension": change["dimension"],
                    "change_kind": change["change_kind"],
                    "epistemic_status": "OBSERVED",
                    "claim_refs": [f"fixture:claim:{change['dimension']}"],
                    "evidence_refs": [f"fixture:evidence:{change['dimension']}"],
                    "not_computable_reason": None,
                }
            )
    return built


def _ref(object_id: str, object_hash: str) -> dict[str, str]:
    return {"object_id": object_id, "canonical_hash": object_hash}


def run_fixture_experiment(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Run one synthetic experiment loop and return a sealed record (pure)."""
    _require(spec)
    construct = dict(spec["construct"])

    # define H -> state t0
    baseline_state = _state_from_spec(spec["baseline"], construct)

    # declared forecast (SHADOW lane; bound outcome makes it calibration-ready)
    forecast_spec = dict(spec["forecast"])
    forecast = build_forecast_object(
        forecast_id=forecast_spec["forecast_id"],
        claim_statement=forecast_spec["claim"],
        probability_value=float(forecast_spec["probability"]),
        domain="rdi_fixture",
        horizon=forecast_spec.get("horizon", "fixture-t1"),
        created_by_lane="SHADOW",
        promotion_state="DRAFT",
        authority_ref=None,
        outcome_binding_status=OutcomeBindingStatus.BOUND,
        calibration_ready=True,
    )
    forecast_report = validate_forecast_object(forecast)
    if forecast_report.status not in {"PASS", "WARN"}:
        raise ValueError(f"fixture forecast failed validation: {forecast_report.status}")

    # optional bounded intervention declaration (never grants authority)
    intervention = None
    if spec.get("intervention"):
        iv = dict(spec["intervention"])
        intervention = build_intervention_declaration(
            intervention_id=iv["intervention_id"],
            construct_ref=_ref(construct["construct_id"], construct["construct_hash"]),
            baseline_state_ref=_ref(baseline_state["state_id"], baseline_state["state_hash"]),
            work_packet_ref=dict(iv["work_packet_ref"]),
            forecast_ref=_ref(forecast.forecast_id, forecast.forecast_hash),
            activation_evidence_ref=dict(iv["activation_evidence_ref"]),
            predicted_dimension_changes=[
                {
                    "dimension": change["dimension"],
                    "change_kind": change["change_kind"],
                    "epistemic_status": "SPECULATIVE",
                    "claim_refs": [f"fixture:prediction:{change['dimension']}"],
                    "not_computable_reason": None,
                }
                for change in iv["predicted_changes"]
            ],
            constraints=iv["constraints"],
            falsification_criteria=iv["falsification_criteria"],
            provenance_refs=iv["provenance_refs"],
        )

    # evidence t1
    observed_spec = dict(spec["observed"])
    observed_state = _state_from_spec(observed_spec, construct)

    # settlement: outcome binding -> SettlementVerdict.v1 (fail-closed bridge)
    binding_spec = dict(spec["binding"])
    binding_payload = {
        "schema_version": "ForecastOutcomeBindingPacket.v1",
        "binding_id": binding_spec["binding_id"],
        "forecast_hash": forecast.forecast_hash,
        "expected_outcome_hash": binding_spec.get("expected_outcome_hash", "fixture-expected"),
        "observed_outcome_hash": binding_spec.get("observed_outcome_hash"),
        "binding_status": binding_spec["binding_status"],
        "status": "open",
    }
    authority = binding_spec.get("settlement_authority")
    verdict = settlement_verdict_from_outcome_binding(
        binding_payload,
        settlement_id=f"settlement:{spec['experiment_id']}",
        forecast_id=forecast.forecast_id,
        evidence_packet_id=binding_spec.get("evidence_packet_id", f"evidence:{spec['experiment_id']}"),
        evidence_hash=canonical_hash(
            {"experiment_id": spec["experiment_id"], "observed_state_hash": observed_state["state_hash"]}
        ),
        created_by_lane="OPERATOR" if authority else "SHADOW",
        authority_ref=AuthorityRef(**authority) if authority else None,
    )
    settlement_report = validate_settlement_verdict(verdict)

    # transition binds forecast, optional intervention, and the settlement
    transition = build_instantiation_transition(
        transition_id=f"it-{spec['experiment_id']}",
        prior_state_id=baseline_state["state_id"],
        prior_state_hash=baseline_state["state_hash"],
        later_state_id=observed_state["state_id"],
        later_state_hash=observed_state["state_hash"],
        dimension_changes=_changes_from_spec(list(observed_spec.get("dimension_changes", ()))),
        causal_exposure=observed_spec.get("causal_exposure", "UNKNOWN"),
        contamination_reasons=tuple(observed_spec.get("contamination_reasons", ())),
        forecast_ref=_ref(forecast.forecast_id, forecast.forecast_hash),
        intervention_ref=(
            _ref(intervention["intervention_id"], intervention["intervention_hash"])
            if intervention
            else None
        ),
        settlement_ref=_ref(verdict.settlement_id, verdict.settlement_hash),
    )

    # calibration: Brier telemetry only, and only from a score-ready verdict
    contamination = transition["contamination"]
    if is_score_ready(verdict):
        outcome = observed_outcome_from_verdict(verdict)
        probability = forecast.probability.value
        score = BrierScorePacket.compute_score(probability, outcome)
        calibration: dict[str, Any] = {
            "status": "SCORED",
            "score_packet": BrierScorePacket(
                score_id=f"score:{spec['experiment_id']}",
                forecast_hash=forecast.forecast_hash,
                expected_probability=probability,
                observed_outcome=outcome,
                brier_score=score,
                deterministic_score_hash=BrierScorePacket.compute_hash(
                    forecast.forecast_hash, probability, outcome, score
                ),
            ).model_dump(),
            "not_computable_reason": None,
        }
    else:
        calibration = {
            "status": "NOT_COMPUTABLE",
            "score_packet": None,
            "not_computable_reason": (
                "settlement verdict is not score-ready "
                f"(decision={verdict.decision.value}, status={verdict.settlement_status.value})"
            ),
        }
    calibration.update(
        {
            "telemetry_only": True,
            "feedback_contaminated": contamination["feedback_contaminated"],
            "independent_confirmation_eligible": contamination[
                "independent_confirmation_eligible"
            ],
        }
    )

    # SHADOW pass over the produced states and transition (detection only)
    shadow_report = detect_instantiation_anomalies(
        [baseline_state, observed_state],
        [transition],
        report_id=f"shadow:{spec['experiment_id']}",
    )

    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": spec["experiment_id"],
        "evidence_environment": "LAB",
        "lane": "SHADOW",
        "synthetic_fixture_only": True,
        "construct_ref": _ref(construct["construct_id"], construct["construct_hash"]),
        "baseline_state": baseline_state,
        "forecast": {
            "payload": asdict(forecast),
            "validation_status": forecast_report.status,
        },
        "intervention": intervention,
        "observed_state": observed_state,
        "transition": transition,
        "settlement": {
            "verdict": asdict(verdict),
            "validation_status": settlement_report.status,
        },
        "calibration": calibration,
        "shadow_report": shadow_report,
        "authority": dict(EXPERIMENT_AUTHORITY),
        "record_hash": "",
    }
    body = {key: value for key, value in record.items() if key != "record_hash"}
    record["record_hash"] = canonical_hash(body)
    return record


def validate_experiment_record(record: Mapping[str, Any]) -> None:
    """Fail-closed structural validation of an experiment record payload."""
    data = dict(record)
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    if data.get("evidence_environment") != "LAB":
        raise ValueError("evidence_environment must be LAB for fixture experiments")
    if data.get("synthetic_fixture_only") is not True:
        raise ValueError("synthetic_fixture_only must be true")
    if data.get("authority") != EXPERIMENT_AUTHORITY:
        raise ValueError("experiment authority locks must all be false")
    calibration = data.get("calibration", {})
    if calibration.get("telemetry_only") is not True:
        raise ValueError("calibration must be telemetry_only")
    if (
        calibration.get("feedback_contaminated")
        and calibration.get("independent_confirmation_eligible")
    ):
        raise ValueError("contaminated calibration cannot be independent-confirmation eligible")
    expected = canonical_hash({k: v for k, v in data.items() if k != "record_hash"})
    if data.get("record_hash") != expected:
        raise ValueError("record_hash does not match canonical payload")
