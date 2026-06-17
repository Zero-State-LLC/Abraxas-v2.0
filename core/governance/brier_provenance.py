"""Deterministic Brier provenance calculator — telemetry-only, no resolution."""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.scoring.brier import compute_brier_score, compute_full_decomposition

NOT_COMPUTABLE = "NOT_COMPUTABLE"
PROVENANCE_CLASSIFICATIONS = ("OBSERVED", "INFERRED", "SPECULATIVE")
DEFAULT_DECOMPOSITION_FIXTURE_PREDICTIONS = (0.7, 0.8, 0.6)
DEFAULT_DECOMPOSITION_FIXTURE_TARGETS = (1.0, 0.0, 1.0)


def build_brier_decomposition_fixture(*, rounding_policy: str = "ROUND_10_DP") -> dict[str, Any]:
    return compute_full_decomposition(
        list(DEFAULT_DECOMPOSITION_FIXTURE_PREDICTIONS),
        list(DEFAULT_DECOMPOSITION_FIXTURE_TARGETS),
        rounding_policy=rounding_policy,
    )


def build_brier_provenance_hook(
    *,
    claim_id: str,
    forecast_probability: float,
    binary_outcome: str | float = NOT_COMPUTABLE,
    resolution_source: str = NOT_COMPUTABLE,
    provenance_classification: str = "INFERRED",
    resolution_allowed: bool = False,
    decomposition: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if provenance_classification not in PROVENANCE_CLASSIFICATIONS:
        provenance_classification = "SPECULATIVE"
    if resolution_allowed:
        raise ValueError("resolution_allowed must remain False for telemetry-only provenance")
    if binary_outcome == "":
        outcome_value: str | float = ""
        brier_score: str | float = NOT_COMPUTABLE
    elif isinstance(binary_outcome, (int, float)):
        brier_score = compute_brier_score(forecast_probability, float(binary_outcome))
        outcome_value = float(binary_outcome)
    else:
        brier_score = NOT_COMPUTABLE
        outcome_value = NOT_COMPUTABLE
    hook: dict[str, Any] = {
        "claim_id": claim_id,
        "forecast_probability": forecast_probability,
        "binary_outcome": outcome_value,
        "brier_score": brier_score,
        "resolution_source": resolution_source,
        "resolution_allowed": False,
        "provenance_classification": provenance_classification,
        "brier_resolution_authorized": False,
    }
    if decomposition is not None:
        hook["decomposition"] = dict(decomposition)
    return hook


def build_brier_provenance_packet(
    hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    telemetry_hooks = [
        build_brier_provenance_hook(
            claim_id="brier_provenance_module_wired",
            forecast_probability=compute_brier_score(0.75, 0.0),
            resolution_source="core/governance/brier_provenance.py",
            provenance_classification="OBSERVED",
            decomposition=fixture_decomposition,
        ),
        build_brier_provenance_hook(
            claim_id="operator_resolution_lane_required",
            forecast_probability=0.5,
            provenance_classification="INFERRED",
            decomposition=fixture_decomposition,
        ),
    ]
    if hooks:
        telemetry_hooks.extend(dict(hook) for hook in hooks)
    packet: dict[str, Any] = {
        "contract_id": "v2_governance_brier_provenance_packet_001",
        "telemetry_only": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "telemetry_hooks": telemetry_hooks,
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
        "adaptive_learning_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
        "brier_provenance_hash": "",
    }
    packet["brier_provenance_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "brier_provenance_hash"}
    )
    return packet


def validate_adversarial_calibration(hook: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if hook.get("resolution_allowed") is True:
        blockers.append("resolution_allowed_must_remain_false")
    if hook.get("brier_resolution_authorized") is True:
        blockers.append("brier_resolution_authorized_must_remain_false")
    outcome = hook.get("binary_outcome")
    if outcome in ("", None):
        blockers.append("empty_outcome_not_scorable")
    if outcome == NOT_COMPUTABLE and hook.get("brier_score") not in (NOT_COMPUTABLE, None):
        blockers.append("unresolved_outcome_with_computed_score")
    if isinstance(outcome, (int, float)) and isinstance(hook.get("brier_score"), str):
        if hook.get("brier_score") == NOT_COMPUTABLE:
            blockers.append("resolved_outcome_missing_score")
    settlement_conflict = (
        isinstance(outcome, (int, float))
        and hook.get("settlement_decision") == "CONFLICTING"
    )
    if settlement_conflict:
        blockers.append("conflicting_settlement_with_binary_outcome")
    return sorted(blockers)
