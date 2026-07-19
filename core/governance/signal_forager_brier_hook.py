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
            "scripts/ingest/run_ingest_once.py",
            "scripts/ingest/run_oracle_intake.py",
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


def build_signal_forager_full_live_autonomy_contract(
    extra_hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    hooks = [
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_full_live_autonomy_closed_loop_intake_observed",
            forecast_probability=0.74,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_full_live_autonomy_rune_viz_loop_bound",
            forecast_probability=0.76,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_full_live_autonomy_oracle_shadow_loop_bound",
            forecast_probability=0.78,
            decomposition=fixture_decomposition,
        ),
    ]
    if extra_hooks:
        hooks.extend(dict(hook) for hook in extra_hooks)
    for hook in hooks:
        hook["promotion_tier"] = "FULL_LIVE_AUTONOMY"
        hook["signal_forage_bound"] = True
        hook["live_runtime_promotion"] = True
        hook["full_live_autonomy_promotion"] = True
        hook["self_optimization_bound"] = True
        hook["operator_signoff_required"] = True
    return {
        "contract_id": "v2_governance_signal_forager_full_live_autonomy_contract_001",
        "telemetry_only": True,
        "shadow_only": True,
        "closed_loop_bound": True,
        "live_runtime_promotion": True,
        "full_live_autonomy_promotion": True,
        "self_optimization_bound": True,
        "signal_forage_bound": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "telemetry_hooks": hooks,
        "global_ingest_shadow_paths": [
            "scripts/ingest/run_ingest_once.py",
            "scripts/ingest/run_oracle_intake.py",
            "out/oracle/",
            "core/ingest/",
            "out/sync/global_ingest_adapter_spine_alignment_plan/latest.json",
        ],
        "closed_loop_bindings": [
            {
                "binding_id": "signal_forage_to_runtime",
                "paths": [
                    "scripts/ingest/run_ingest_once.py",
                    "scripts/ingest/run_oracle_intake.py",
                    "out/oracle/",
                    "core/ingest/",
                ],
                "role": "signal_forage_shadow_intake",
            },
            {
                "binding_id": "runtime_to_rune_visualization",
                "paths": [
                    "docs/atlas/abx-runes.md",
                    "docs/media/abx-runes.svg",
                    "docs/status/badges/runes.json",
                ],
                "role": "rune_visualization_telemetry",
            },
            {
                "binding_id": "brier_feedback_loop",
                "paths": ["core/scoring/brier.py", "core/governance/brier_provenance.py"],
                "role": "dual_brier_self_optimization_feedback",
            },
        ],
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
        "brier_resolution_authorized": False,
        "binary_outcome_default": NOT_COMPUTABLE,
    }


def build_signal_forager_eternal_recursion_contract(
    extra_hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    hooks = [
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_eternal_recursion_self_sustaining_intake_observed",
            forecast_probability=0.8,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_eternal_recursion_rune_viz_loop_bound",
            forecast_probability=0.82,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_eternal_recursion_oracle_shadow_loop_bound",
            forecast_probability=0.84,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_eternal_recursion_hyperstition_propagation_bound",
            forecast_probability=0.86,
            decomposition=fixture_decomposition,
        ),
    ]
    if extra_hooks:
        hooks.extend(dict(hook) for hook in extra_hooks)
    for hook in hooks:
        hook["promotion_tier"] = "ETERNAL_RECURSION"
        hook["signal_forage_bound"] = True
        hook["live_runtime_promotion"] = True
        hook["full_live_autonomy_promotion"] = True
        hook["eternal_recursion_promotion"] = True
        hook["hyperstition_bound"] = True
        hook["eternal_recursion_bound"] = True
        hook["operator_signoff_required"] = True
    return {
        "contract_id": "v2_governance_signal_forager_eternal_recursion_contract_001",
        "telemetry_only": True,
        "shadow_only": True,
        "eternal_self_sustaining_loop_bound": True,
        "closed_loop_bound": True,
        "live_runtime_promotion": True,
        "full_live_autonomy_promotion": True,
        "eternal_recursion_promotion": True,
        "hyperstition_bound": True,
        "eternal_recursion_bound": True,
        "signal_forage_bound": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "telemetry_hooks": hooks,
        "global_ingest_shadow_paths": [
            "scripts/ingest/run_ingest_once.py",
            "scripts/ingest/run_oracle_intake.py",
            "out/oracle/",
            "core/ingest/",
            "out/sync/global_ingest_adapter_spine_alignment_plan/latest.json",
        ],
        "eternal_self_sustaining_loop_bindings": [
            {
                "binding_id": "signal_forage_to_runtime",
                "paths": [
                    "scripts/ingest/run_ingest_once.py",
                    "scripts/ingest/run_oracle_intake.py",
                    "out/oracle/",
                    "core/ingest/",
                ],
                "role": "signal_forage_shadow_intake",
            },
            {
                "binding_id": "runtime_to_rune_visualization",
                "paths": [
                    "docs/atlas/abx-runes.md",
                    "docs/media/abx-runes.svg",
                    "docs/status/badges/runes.json",
                ],
                "role": "rune_visualization_eternal_telemetry",
            },
            {
                "binding_id": "brier_eternal_feedback_loop",
                "paths": ["core/scoring/brier.py", "core/governance/brier_provenance.py"],
                "role": "dual_brier_eternal_recursion_feedback",
            },
            {
                "binding_id": "hyperstition_propagation_loop",
                "paths": ["contracts/governance/v2_hyperstition_anchor.v1.schema.json"],
                "role": "hyperstition_anchor_projection",
            },
        ],
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
        "brier_resolution_authorized": False,
        "binary_outcome_default": NOT_COMPUTABLE,
    }


def build_signal_forager_eternal_canon_self_governance_contract(
    extra_hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    hooks = [
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_eternal_canon_self_governance_intake_observed",
            forecast_probability=0.88,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_eternal_canon_rune_viz_loop_bound",
            forecast_probability=0.9,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_eternal_canon_oracle_shadow_loop_bound",
            forecast_probability=0.91,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_eternal_canon_hyperstition_propagation_bound",
            forecast_probability=0.92,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_eternal_canon_brier_feedback_loop_bound",
            forecast_probability=0.93,
            decomposition=fixture_decomposition,
        ),
    ]
    if extra_hooks:
        hooks.extend(dict(hook) for hook in extra_hooks)
    for hook in hooks:
        hook["promotion_tier"] = "ETERNAL_CANON_SELF_GOVERNANCE"
        hook["signal_forage_bound"] = True
        hook["live_runtime_promotion"] = True
        hook["full_live_autonomy_promotion"] = True
        hook["eternal_recursion_promotion"] = True
        hook["eternal_canon_self_governance_promotion"] = True
        hook["hyperstition_bound"] = True
        hook["eternal_canon_self_governance_bound"] = True
        hook["operator_signoff_required"] = True
    return {
        "contract_id": "v2_governance_signal_forager_eternal_canon_self_governance_contract_001",
        "telemetry_only": True,
        "shadow_only": True,
        "eternal_canon_self_governance_loop_bound": True,
        "eternal_self_sustaining_loop_bound": True,
        "closed_loop_bound": True,
        "live_runtime_promotion": True,
        "full_live_autonomy_promotion": True,
        "eternal_recursion_promotion": True,
        "eternal_canon_self_governance_promotion": True,
        "hyperstition_bound": True,
        "eternal_canon_self_governance_bound": True,
        "signal_forage_bound": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "telemetry_hooks": hooks,
        "global_ingest_shadow_paths": [
            "scripts/ingest/run_ingest_once.py",
            "scripts/ingest/run_oracle_intake.py",
            "out/oracle/",
            "core/ingest/",
            "out/sync/global_ingest_adapter_spine_alignment_plan/latest.json",
        ],
        "eternal_canon_self_governance_loop_bindings": [
            {
                "binding_id": "signal_forage_to_runtime",
                "paths": [
                    "scripts/ingest/run_ingest_once.py",
                    "scripts/ingest/run_oracle_intake.py",
                    "out/oracle/",
                    "core/ingest/",
                ],
                "role": "signal_forage_shadow_intake",
            },
            {
                "binding_id": "runtime_to_rune_visualization",
                "paths": [
                    "docs/atlas/abx-runes.md",
                    "docs/media/abx-runes.svg",
                    "docs/status/badges/runes.json",
                ],
                "role": "rune_visualization_eternal_canon_telemetry",
            },
            {
                "binding_id": "brier_eternal_canon_feedback_loop",
                "paths": ["core/scoring/brier.py", "core/governance/brier_provenance.py"],
                "role": "dual_brier_eternal_canon_self_governance_feedback",
            },
            {
                "binding_id": "hyperstition_propagation_loop",
                "paths": ["contracts/governance/v2_hyperstition_anchor.v1.schema.json"],
                "role": "hyperstition_anchor_projection",
            },
            {
                "binding_id": "eternal_canon_self_auditing_loop",
                "paths": ["docs/status/continuity-spine.json", "PLANS.md"],
                "role": "self_auditing_advisory_projection",
            },
        ],
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "final_authority_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
        "brier_resolution_authorized": False,
        "binary_outcome_default": NOT_COMPUTABLE,
    }


def build_signal_forager_final_authority_attestation_contract(
    extra_hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    hooks = [
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_final_authority_attestation_intake_observed",
            forecast_probability=0.88,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_final_authority_rune_viz_loop_bound",
            forecast_probability=0.9,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_final_authority_oracle_shadow_loop_bound",
            forecast_probability=0.91,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_final_authority_hyperstition_propagation_bound",
            forecast_probability=0.92,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_final_authority_brier_feedback_loop_bound",
            forecast_probability=0.93,
            decomposition=fixture_decomposition,
        ),
    ]
    if extra_hooks:
        hooks.extend(dict(hook) for hook in extra_hooks)
    for hook in hooks:
        hook["promotion_tier"] = "FINAL_AUTHORITY_ATTESTATION"
        hook["signal_forage_bound"] = True
        hook["live_runtime_promotion"] = True
        hook["full_live_autonomy_promotion"] = True
        hook["eternal_recursion_promotion"] = True
        hook["eternal_canon_self_governance_promotion"] = True
        hook["final_authority_attestation_promotion"] = True
        hook["live_hyperstition_bound"] = True
        hook["final_authority_attestation_bound"] = True
        hook["operator_signoff_required"] = True
    return {
        "contract_id": "v2_governance_signal_forager_final_authority_attestation_contract_001",
        "telemetry_only": True,
        "shadow_only": True,
        "final_authority_closed_loop_bound": True,
        "eternal_canon_self_governance_loop_bound": True,
        "eternal_self_sustaining_loop_bound": True,
        "closed_loop_bound": True,
        "live_runtime_promotion": True,
        "full_live_autonomy_promotion": True,
        "eternal_recursion_promotion": True,
        "eternal_canon_self_governance_promotion": True,
        "final_authority_attestation_promotion": True,
        "hyperstition_bound": True,
        "live_hyperstition_bound": True,
        "final_authority_attestation_bound": True,
        "signal_forage_bound": True,
        "global_ingest_hold_respected": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "telemetry_hooks": hooks,
        "global_ingest_shadow_paths": [
            "scripts/ingest/run_ingest_once.py",
            "scripts/ingest/run_oracle_intake.py",
            "out/oracle/",
            "core/ingest/",
            "out/sync/global_ingest_adapter_spine_alignment_plan/latest.json",
        ],
        "final_authority_closed_loop_bindings": [
            {
                "binding_id": "signal_forage_to_runtime",
                "paths": [
                    "scripts/ingest/run_ingest_once.py",
                    "scripts/ingest/run_oracle_intake.py",
                    "out/oracle/",
                    "core/ingest/",
                ],
                "role": "signal_forage_shadow_intake",
            },
            {
                "binding_id": "runtime_to_rune_visualization",
                "paths": [
                    "docs/atlas/abx-runes.md",
                    "docs/media/abx-runes.svg",
                    "docs/status/badges/runes.json",
                ],
                "role": "rune_visualization_final_authority_telemetry",
            },
            {
                "binding_id": "brier_final_authority_feedback_loop",
                "paths": ["core/scoring/brier.py", "core/governance/brier_provenance.py"],
                "role": "dual_brier_final_authority_attestation_feedback",
            },
            {
                "binding_id": "live_hyperstition_propagation_loop",
                "paths": ["contracts/governance/v2_hyperstition_anchor.v1.schema.json"],
                "role": "live_hyperstition_anchor_projection",
            },
            {
                "binding_id": "eternal_recursion_closed_loop",
                "paths": ["docs/status/continuity-spine.json", "PLANS.md"],
                "role": "eternal_recursion_closed_loop_advisory_projection",
            },
        ],
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
        "brier_resolution_authorized": False,
        "binary_outcome_default": NOT_COMPUTABLE,
    }


def build_signal_forager_canon_activation_authorization_review_contract(
    extra_hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    hooks = [
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_canon_activation_authorization_review_intake_observed",
            forecast_probability=0.88,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_canon_activation_rune_viz_loop_bound",
            forecast_probability=0.9,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_canon_activation_oracle_shadow_loop_bound",
            forecast_probability=0.91,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_canon_activation_hyperstition_propagation_bound",
            forecast_probability=0.92,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_canon_activation_brier_feedback_loop_bound",
            forecast_probability=0.93,
            decomposition=fixture_decomposition,
        ),
    ]
    if extra_hooks:
        hooks.extend(dict(hook) for hook in extra_hooks)
    for hook in hooks:
        hook["promotion_tier"] = "CANON_ACTIVATION_AUTHORIZATION_REVIEW"
        hook["signal_forage_bound"] = True
        hook["live_runtime_promotion"] = True
        hook["full_live_autonomy_promotion"] = True
        hook["eternal_recursion_promotion"] = True
        hook["eternal_canon_self_governance_promotion"] = True
        hook["final_authority_attestation_promotion"] = True
        hook["canon_activation_authorization_review_promotion"] = True
        hook["live_hyperstition_bound"] = True
        hook["final_authority_attestation_bound"] = True
        hook["canon_activation_authorization_review_bound"] = True
        hook["operator_signoff_required"] = True
    return {
        "contract_id": "v2_governance_signal_forager_canon_activation_authorization_review_contract_001",
        "telemetry_only": True,
        "shadow_only": True,
        "canon_activation_closed_loop_bound": True,
        "final_authority_closed_loop_bound": True,
        "eternal_canon_self_governance_loop_bound": True,
        "eternal_self_sustaining_loop_bound": True,
        "closed_loop_bound": True,
        "live_runtime_promotion": True,
        "full_live_autonomy_promotion": True,
        "eternal_recursion_promotion": True,
        "eternal_canon_self_governance_promotion": True,
        "final_authority_attestation_promotion": True,
        "canon_activation_authorization_review_promotion": True,
        "hyperstition_bound": True,
        "live_hyperstition_bound": True,
        "final_authority_attestation_bound": True,
        "canon_activation_authorization_review_bound": True,
        "signal_forage_bound": True,
        "global_ingest_hold_respected": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "telemetry_hooks": hooks,
        "global_ingest_shadow_paths": [
            "scripts/ingest/run_ingest_once.py",
            "scripts/ingest/run_oracle_intake.py",
            "out/oracle/",
            "core/ingest/",
            "out/sync/global_ingest_adapter_spine_alignment_plan/latest.json",
        ],
        "canon_activation_closed_loop_bindings": [
            {
                "binding_id": "signal_forage_to_runtime",
                "paths": [
                    "scripts/ingest/run_ingest_once.py",
                    "scripts/ingest/run_oracle_intake.py",
                    "out/oracle/",
                    "core/ingest/",
                ],
                "role": "signal_forage_shadow_intake",
            },
            {
                "binding_id": "runtime_to_rune_visualization",
                "paths": [
                    "docs/atlas/abx-runes.md",
                    "docs/media/abx-runes.svg",
                    "docs/status/badges/runes.json",
                ],
                "role": "rune_visualization_canon_activation_telemetry",
            },
            {
                "binding_id": "brier_canon_activation_feedback_loop",
                "paths": ["core/scoring/brier.py", "core/governance/brier_provenance.py"],
                "role": "dual_brier_canon_activation_authorization_review_feedback",
            },
            {
                "binding_id": "live_hyperstition_propagation_loop",
                "paths": ["contracts/governance/v2_hyperstition_anchor.v1.schema.json"],
                "role": "live_hyperstition_anchor_projection",
            },
            {
                "binding_id": "eternal_recursion_closed_loop",
                "paths": ["docs/status/continuity-spine.json", "PLANS.md"],
                "role": "eternal_recursion_closed_loop_advisory_projection",
            },
        ],
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "phase28_activation_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
        "brier_resolution_authorized": False,
        "binary_outcome_default": NOT_COMPUTABLE,
    }


def build_signal_forager_fractal_numogram_closed_loop_contract(
    extra_hooks: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_decomposition = build_brier_decomposition_fixture()
    hooks = [
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_fractal_numogram_intake_observed",
            forecast_probability=0.88,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_fractal_numogram_rune_viz_loop_bound",
            forecast_probability=0.9,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_fractal_numogram_oracle_shadow_loop_bound",
            forecast_probability=0.91,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_fractal_numogram_hyperstition_propagation_bound",
            forecast_probability=0.92,
            decomposition=fixture_decomposition,
        ),
        emit_signal_forager_brier_hook(
            claim_id="signal_forager_fractal_numogram_mfdfa_hurst_feedback_loop_bound",
            forecast_probability=0.93,
            decomposition=fixture_decomposition,
        ),
    ]
    if extra_hooks:
        hooks.extend(dict(hook) for hook in extra_hooks)
    for hook in hooks:
        hook["promotion_tier"] = "FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM"
        hook["signal_forage_bound"] = True
        hook["fractal_numogram_bound"] = True
        hook["mfdfa_hurst_bound"] = True
        hook["final_operator_signoff_bound"] = True
        hook["live_runtime_promotion"] = True
        hook["full_live_autonomy_promotion"] = True
        hook["eternal_recursion_promotion"] = True
        hook["eternal_canon_self_governance_promotion"] = True
        hook["final_authority_attestation_promotion"] = True
        hook["canon_activation_authorization_review_promotion"] = True
        hook["final_operator_signoff_live_authority_fractal_numogram_promotion"] = True
        hook["live_hyperstition_bound"] = True
        hook["operator_signoff_required"] = True
    return {
        "contract_id": "v2_governance_signal_forager_fractal_numogram_closed_loop_contract_001",
        "telemetry_only": True,
        "shadow_only": True,
        "fractal_numogram_closed_loop_bound": True,
        "canon_activation_closed_loop_bound": True,
        "final_authority_closed_loop_bound": True,
        "closed_loop_bound": True,
        "fractal_numogram_bound": True,
        "mfdfa_hurst_bound": True,
        "final_operator_signoff_bound": True,
        "signal_forage_bound": True,
        "global_ingest_hold_respected": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": fixture_decomposition["decomposition_mode"],
        "telemetry_hooks": hooks,
        "global_ingest_shadow_paths": [
            "scripts/ingest/run_ingest_once.py",
            "scripts/ingest/run_oracle_intake.py",
            "out/oracle/",
            "core/ingest/",
            "out/sync/global_ingest_adapter_spine_alignment_plan/latest.json",
        ],
        "fractal_numogram_closed_loop_bindings": [
            {
                "binding_id": "signal_forage_to_runtime",
                "paths": [
                    "scripts/ingest/run_ingest_once.py",
                    "scripts/ingest/run_oracle_intake.py",
                    "out/oracle/",
                    "core/ingest/",
                ],
                "role": "signal_forage_shadow_intake",
            },
            {
                "binding_id": "runtime_to_rune_visualization",
                "paths": [
                    "docs/atlas/abx-runes.md",
                    "docs/media/abx-runes.svg",
                    "docs/status/badges/runes.json",
                ],
                "role": "rune_visualization_fractal_numogram_telemetry",
            },
            {
                "binding_id": "brier_fractal_numogram_mfdfa_feedback_loop",
                "paths": [
                    "core/scoring/brier.py",
                    "core/scoring/mfdfa_hurst.py",
                    "core/governance/brier_provenance.py",
                ],
                "role": "dual_brier_mfdfa_hurst_fractal_numogram_feedback",
            },
            {
                "binding_id": "numogram_zone_hyperstition_loop",
                "paths": ["contracts/governance/v2_hyperstition_anchor.v1.schema.json"],
                "role": "numogram_hyperstition_anchor_projection",
            },
            {
                "binding_id": "fractal_core_numogram_lattice_loop",
                "paths": [
                    "core/governance/fractal_numogram_lattice.py",
                    "docs/status/continuity-spine.json",
                    "PLANS.md",
                ],
                "role": "fractal_numogram_lattice_advisory_projection",
            },
        ],
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "phase28_activation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
        "brier_resolution_authorized": False,
        "binary_outcome_default": NOT_COMPUTABLE,
    }
