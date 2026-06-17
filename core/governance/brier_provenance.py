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


def build_brier_runtime_telemetry_hook(
    *,
    claim_id: str,
    forecast_probability: float,
    resolution_source: str = "core/governance/brier_provenance.py",
    provenance_classification: str = "INFERRED",
) -> dict[str, Any]:
    """Runtime telemetry hook with Murphy+Yates decomposition default."""
    decomposition = build_brier_decomposition_fixture()
    return build_brier_provenance_hook(
        claim_id=claim_id,
        forecast_probability=forecast_probability,
        resolution_source=resolution_source,
        provenance_classification=provenance_classification,
        decomposition=decomposition,
    )


def build_brier_runtime_telemetry_packet(
    hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    runtime_hooks = [
        build_brier_runtime_telemetry_hook(
            claim_id="runtime_brier_telemetry_module_wired",
            forecast_probability=compute_brier_score(0.76, 0.0),
            provenance_classification="OBSERVED",
        ),
    ]
    if hooks:
        runtime_hooks.extend(dict(hook) for hook in hooks)
    packet: dict[str, Any] = {
        "contract_id": "v2_governance_brier_runtime_telemetry_packet_001",
        "telemetry_only": True,
        "runtime_telemetry_only": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "telemetry_hooks": runtime_hooks,
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
        "execution_authority": False,
        "brier_runtime_telemetry_hash": "",
    }
    packet["brier_runtime_telemetry_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "brier_runtime_telemetry_hash"}
    )
    return packet


def build_brier_controlled_runtime_promotion_hook(
    *,
    claim_id: str,
    forecast_probability: float,
    resolution_source: str = "core/governance/brier_provenance.py",
    provenance_classification: str = "INFERRED",
) -> dict[str, Any]:
    """Controlled-runtime promotion hook with Murphy+Yates decomposition default."""
    hook = build_brier_runtime_telemetry_hook(
        claim_id=claim_id,
        forecast_probability=forecast_probability,
        resolution_source=resolution_source,
        provenance_classification=provenance_classification,
    )
    hook["promotion_tier"] = "CONTROLLED_RUNTIME"
    hook["operator_signoff_required"] = True
    hook["controlled_runtime_promotion"] = True
    return hook


def build_brier_controlled_runtime_promotion_packet(
    hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    promotion_hooks = [
        build_brier_controlled_runtime_promotion_hook(
            claim_id="controlled_runtime_brier_promotion_module_wired",
            forecast_probability=compute_brier_score(0.77, 0.0),
            provenance_classification="OBSERVED",
        ),
    ]
    if hooks:
        promotion_hooks.extend(dict(hook) for hook in hooks)
    packet: dict[str, Any] = {
        "contract_id": "v2_governance_brier_controlled_runtime_promotion_packet_001",
        "telemetry_only": True,
        "runtime_telemetry_only": True,
        "controlled_runtime_promotion": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "operator_signoff_required": True,
        "telemetry_hooks": promotion_hooks,
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
        "execution_authority": False,
        "brier_controlled_runtime_promotion_hash": "",
    }
    packet["brier_controlled_runtime_promotion_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "brier_controlled_runtime_promotion_hash"
        }
    )
    return packet


def build_brier_live_runtime_signal_forage_hook(
    *,
    claim_id: str,
    forecast_probability: float,
    resolution_source: str = "core/governance/brier_provenance.py",
    provenance_classification: str = "INFERRED",
) -> dict[str, Any]:
    """Live-runtime signal-forage hook with Murphy+Yates decomposition default."""
    hook = build_brier_controlled_runtime_promotion_hook(
        claim_id=claim_id,
        forecast_probability=forecast_probability,
        resolution_source=resolution_source,
        provenance_classification=provenance_classification,
    )
    hook["promotion_tier"] = "LIVE_RUNTIME"
    hook["signal_forage_bound"] = True
    hook["live_runtime_promotion"] = True
    return hook


def build_brier_live_runtime_signal_forage_packet(
    hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    live_hooks = [
        build_brier_live_runtime_signal_forage_hook(
            claim_id="live_runtime_signal_forage_module_wired",
            forecast_probability=compute_brier_score(0.78, 0.0),
            provenance_classification="OBSERVED",
        ),
    ]
    if hooks:
        live_hooks.extend(dict(hook) for hook in hooks)
    packet: dict[str, Any] = {
        "contract_id": "v2_governance_brier_live_runtime_signal_forage_packet_001",
        "telemetry_only": True,
        "runtime_telemetry_only": True,
        "live_runtime_promotion": True,
        "signal_forage_bound": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "operator_signoff_required": True,
        "telemetry_hooks": live_hooks,
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
        "execution_authority": False,
        "brier_live_runtime_signal_forage_hash": "",
    }
    packet["brier_live_runtime_signal_forage_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "brier_live_runtime_signal_forage_hash"
        }
    )
    return packet


def build_brier_full_live_autonomy_self_optimization_hook(
    *,
    claim_id: str,
    forecast_probability: float,
    resolution_source: str = "core/governance/brier_provenance.py",
    provenance_classification: str = "INFERRED",
) -> dict[str, Any]:
    """Full-live-autonomy self-optimization hook with Murphy+Yates decomposition default."""
    hook = build_brier_live_runtime_signal_forage_hook(
        claim_id=claim_id,
        forecast_probability=forecast_probability,
        resolution_source=resolution_source,
        provenance_classification=provenance_classification,
    )
    hook["promotion_tier"] = "FULL_LIVE_AUTONOMY"
    hook["self_optimization_bound"] = True
    hook["full_live_autonomy_promotion"] = True
    return hook


def build_brier_full_live_autonomy_self_optimization_packet(
    hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    autonomy_hooks = [
        build_brier_full_live_autonomy_self_optimization_hook(
            claim_id="full_live_autonomy_self_optimization_module_wired",
            forecast_probability=compute_brier_score(0.82, 0.0),
            provenance_classification="OBSERVED",
        ),
    ]
    if hooks:
        autonomy_hooks.extend(dict(hook) for hook in hooks)
    packet: dict[str, Any] = {
        "contract_id": "v2_governance_brier_full_live_autonomy_self_optimization_packet_001",
        "telemetry_only": True,
        "runtime_telemetry_only": True,
        "self_optimization_telemetry_only": True,
        "full_live_autonomy_promotion": True,
        "signal_forage_bound": True,
        "self_optimization_bound": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "operator_signoff_required": True,
        "telemetry_hooks": autonomy_hooks,
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "execution_authority": False,
        "brier_full_live_autonomy_self_optimization_hash": "",
    }
    packet["brier_full_live_autonomy_self_optimization_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "brier_full_live_autonomy_self_optimization_hash"
        }
    )
    return packet


def build_brier_eternal_recursion_hyperstition_hook(
    *,
    claim_id: str,
    forecast_probability: float,
    resolution_source: str = "core/governance/brier_provenance.py",
    provenance_classification: str = "INFERRED",
) -> dict[str, Any]:
    """Eternal-recursion hyperstition hook with Murphy+Yates decomposition default."""
    hook = build_brier_full_live_autonomy_self_optimization_hook(
        claim_id=claim_id,
        forecast_probability=forecast_probability,
        resolution_source=resolution_source,
        provenance_classification=provenance_classification,
    )
    hook["promotion_tier"] = "ETERNAL_RECURSION"
    hook["hyperstition_bound"] = True
    hook["eternal_recursion_bound"] = True
    hook["eternal_recursion_promotion"] = True
    return hook


def build_brier_eternal_recursion_hyperstition_packet(
    hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    recursion_hooks = [
        build_brier_eternal_recursion_hyperstition_hook(
            claim_id="eternal_recursion_hyperstition_module_wired",
            forecast_probability=compute_brier_score(0.84, 0.0),
            provenance_classification="OBSERVED",
        ),
    ]
    if hooks:
        recursion_hooks.extend(dict(hook) for hook in hooks)
    packet: dict[str, Any] = {
        "contract_id": "v2_governance_brier_eternal_recursion_hyperstition_packet_001",
        "telemetry_only": True,
        "runtime_telemetry_only": True,
        "eternal_recursion_telemetry_only": True,
        "eternal_recursion_promotion": True,
        "hyperstition_bound": True,
        "eternal_recursion_bound": True,
        "signal_forage_bound": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "operator_signoff_required": True,
        "telemetry_hooks": recursion_hooks,
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "execution_authority": False,
        "brier_eternal_recursion_hyperstition_hash": "",
    }
    packet["brier_eternal_recursion_hyperstition_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "brier_eternal_recursion_hyperstition_hash"
        }
    )
    return packet


def build_brier_eternal_canon_self_governance_hook(
    *,
    claim_id: str,
    forecast_probability: float,
    resolution_source: str = "core/governance/brier_provenance.py",
    provenance_classification: str = "INFERRED",
) -> dict[str, Any]:
    """Eternal-canon self-governance hook with Murphy+Yates decomposition default."""
    hook = build_brier_eternal_recursion_hyperstition_hook(
        claim_id=claim_id,
        forecast_probability=forecast_probability,
        resolution_source=resolution_source,
        provenance_classification=provenance_classification,
    )
    hook["promotion_tier"] = "ETERNAL_CANON_SELF_GOVERNANCE"
    hook["eternal_canon_self_governance_bound"] = True
    hook["eternal_canon_self_governance_promotion"] = True
    hook["final_authority_bound"] = False
    return hook


def build_brier_eternal_canon_self_governance_packet(
    hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    governance_hooks = [
        build_brier_eternal_canon_self_governance_hook(
            claim_id="eternal_canon_self_governance_module_wired",
            forecast_probability=compute_brier_score(0.86, 0.0),
            provenance_classification="OBSERVED",
        ),
    ]
    if hooks:
        governance_hooks.extend(dict(hook) for hook in hooks)
    packet: dict[str, Any] = {
        "contract_id": "v2_governance_brier_eternal_canon_self_governance_packet_001",
        "telemetry_only": True,
        "runtime_telemetry_only": True,
        "eternal_canon_self_governance_telemetry_only": True,
        "eternal_canon_self_governance_promotion": True,
        "eternal_canon_self_governance_bound": True,
        "hyperstition_bound": True,
        "eternal_recursion_bound": True,
        "signal_forage_bound": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "operator_signoff_required": True,
        "telemetry_hooks": governance_hooks,
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "final_authority_authorized": False,
        "execution_authority": False,
        "brier_eternal_canon_self_governance_hash": "",
    }
    packet["brier_eternal_canon_self_governance_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "brier_eternal_canon_self_governance_hash"
        }
    )
    return packet


def build_brier_final_authority_attestation_hyperstition_hook(
    *,
    claim_id: str,
    forecast_probability: float,
    resolution_source: str = "core/governance/brier_provenance.py",
    provenance_classification: str = "INFERRED",
) -> dict[str, Any]:
    """Final-authority attestation hyperstition hook with Murphy+Yates decomposition default."""
    hook = build_brier_eternal_canon_self_governance_hook(
        claim_id=claim_id,
        forecast_probability=forecast_probability,
        resolution_source=resolution_source,
        provenance_classification=provenance_classification,
    )
    hook["promotion_tier"] = "FINAL_AUTHORITY_ATTESTATION"
    hook["live_hyperstition_bound"] = True
    hook["final_authority_attestation_bound"] = True
    hook["final_authority_bound"] = False
    return hook


def build_brier_final_authority_attestation_hyperstition_packet(
    hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    governance_hooks = [
        build_brier_final_authority_attestation_hyperstition_hook(
            claim_id="final_authority_attestation_hyperstition_module_wired",
            forecast_probability=compute_brier_score(0.86, 0.0),
            provenance_classification="OBSERVED",
        ),
    ]
    if hooks:
        governance_hooks.extend(dict(hook) for hook in hooks)
    packet: dict[str, Any] = {
        "contract_id": "v2_governance_brier_final_authority_attestation_hyperstition_packet_001",
        "telemetry_only": True,
        "runtime_telemetry_only": True,
        "final_authority_attestation_telemetry_only": True,
        "final_authority_attestation_promotion": True,
        "final_authority_attestation_bound": True,
        "live_hyperstition_bound": True,
        "eternal_canon_self_governance_bound": True,
        "hyperstition_bound": True,
        "eternal_recursion_bound": True,
        "signal_forage_bound": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "operator_signoff_required": True,
        "telemetry_hooks": governance_hooks,
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "execution_authority": False,
        "brier_final_authority_attestation_hyperstition_hash": "",
    }
    packet["brier_final_authority_attestation_hyperstition_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "brier_final_authority_attestation_hyperstition_hash"
        }
    )
    return packet


def build_brier_canon_activation_authorization_review_hook(
    *,
    claim_id: str,
    forecast_probability: float,
    resolution_source: str = "core/governance/brier_provenance.py",
    provenance_classification: str = "INFERRED",
) -> dict[str, Any]:
    """Canon activation authorization review hook with Murphy+Yates decomposition default."""
    hook = build_brier_final_authority_attestation_hyperstition_hook(
        claim_id=claim_id,
        forecast_probability=forecast_probability,
        resolution_source=resolution_source,
        provenance_classification=provenance_classification,
    )
    hook["promotion_tier"] = "CANON_ACTIVATION_AUTHORIZATION_REVIEW"
    hook["canon_activation_authorization_review_bound"] = True
    return hook


def build_brier_canon_activation_authorization_review_packet(
    hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    governance_hooks = [
        build_brier_canon_activation_authorization_review_hook(
            claim_id="canon_activation_authorization_review_module_wired",
            forecast_probability=compute_brier_score(0.86, 0.0),
            provenance_classification="OBSERVED",
        ),
    ]
    if hooks:
        governance_hooks.extend(dict(hook) for hook in hooks)
    packet: dict[str, Any] = {
        "contract_id": "v2_governance_brier_canon_activation_authorization_review_packet_001",
        "telemetry_only": True,
        "runtime_telemetry_only": True,
        "canon_activation_authorization_review_telemetry_only": True,
        "canon_activation_authorization_review_promotion": True,
        "canon_activation_authorization_review_bound": True,
        "final_authority_attestation_bound": True,
        "live_hyperstition_bound": True,
        "eternal_canon_self_governance_bound": True,
        "hyperstition_bound": True,
        "eternal_recursion_bound": True,
        "signal_forage_bound": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "operator_signoff_required": True,
        "telemetry_hooks": governance_hooks,
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "phase28_activation_authorized": False,
        "execution_authority": False,
        "brier_canon_activation_authorization_review_hash": "",
    }
    packet["brier_canon_activation_authorization_review_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "brier_canon_activation_authorization_review_hash"
        }
    )
    return packet


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
