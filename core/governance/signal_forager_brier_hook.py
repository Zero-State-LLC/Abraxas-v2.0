"""Thin adapter emitting telemetry hooks compatible with v2 hygiene brier_scoring_contract."""

from __future__ import annotations

from typing import Any, Mapping

from core.governance.brier_provenance import (
    NOT_COMPUTABLE,
    build_brier_decomposition_fixture,
    build_brier_provenance_hook,
    build_brier_provenance_packet,
)

CONTRACT_ID = "v2_governance_signal_forager_brier_hook_001"


def emit_signal_forager_brier_hook(
    *,
    claim_id: str,
    forecast_probability: float,
    resolution_source: str = "core/governance/signal_forager_brier_hook.py",
    decomposition: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return build_brier_provenance_hook(
        claim_id=claim_id,
        forecast_probability=forecast_probability,
        resolution_source=resolution_source,
        provenance_classification="INFERRED",
        decomposition=decomposition or build_brier_decomposition_fixture(),
    )


def build_signal_forager_brier_contract(
    extra_hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    hooks = [
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_shadow_intake_observed",
            forecast_probability=0.65,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_governance_trace_complete",
            forecast_probability=0.7,
            decomposition=fixture_decomposition,
        ),
    ]
    if extra_hooks:
        hooks.extend(dict(hook) for hook in extra_hooks)
    provenance_packet = build_brier_provenance_packet(hooks)
    return {
        "contract_id": CONTRACT_ID,
        "telemetry_only": provenance_packet["telemetry_only"],
        "brier_score_formula": provenance_packet["brier_score_formula"],
        "decomposition_mode": provenance_packet["decomposition_mode"],
        "telemetry_hooks": provenance_packet["telemetry_hooks"],
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
        "brier_resolution_authorized": False,
        "binary_outcome_default": NOT_COMPUTABLE,
    }


def build_signal_forager_live_runtime_contract(
    extra_hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    hooks = [
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_live_runtime_shadow_intake_observed",
            forecast_probability=0.68,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_live_runtime_governance_trace_complete",
            forecast_probability=0.72,
            decomposition=fixture_decomposition,
        ),
    ]
    if extra_hooks:
        hooks.extend(dict(hook) for hook in extra_hooks)
    for hook in hooks:
        hook["promotion_tier"] = "LIVE_RUNTIME"
        hook["signal_forage_bound"] = True
        hook["live_runtime_promotion"] = True
        hook["operator_signoff_required"] = True
    return {
        "contract_id": "v2_governance_signal_forager_live_runtime_contract_001",
        "telemetry_only": True,
        "shadow_only": True,
        "live_runtime_promotion": True,
        "signal_forage_bound": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "telemetry_hooks": hooks,
        "global_ingest_shadow_paths": [
            "scripts/run_ingest_once.py",
            "scripts/run_oracle_intake.py",
            "out/oracle/",
            "core/ingest/",
            "out/sync/global_ingest_adapter_spine_alignment_plan/latest.json",
        ],
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
        "brier_resolution_authorized": False,
        "binary_outcome_default": NOT_COMPUTABLE,
    }
