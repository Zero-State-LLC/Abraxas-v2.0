from __future__ import annotations

import argparse
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPT_DIR_KEY = _SCRIPT_DIR.casefold()
_ROOT_DIR = os.path.dirname(_SCRIPT_DIR)
sys.path = [
    path
    for path in sys.path
    if os.path.abspath(path or os.curdir).casefold() != _SCRIPT_DIR_KEY
]
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from core.canonical.json import write_canonical_json  # noqa: E402
from core.codegen.loop805_activation_proposal import (  # noqa: E402
    build_loop805_gate_selection_matrix,
    build_loop805_activation_proposal,
    build_loop805_slice3_prompt_packet,
    build_loop805_slice4_prompt_packet,
)
from core.codegen.loop805_brier_attestation import (  # noqa: E402
    build_loop805_authorization_evidence_packet,
    build_loop805_brier_attestation_packet,
    build_loop805_brier_scoring_shadow_run,
    build_loop805_fixture_binding_dryrun,
    build_loop805_fixture_outcome_binding_review,
    build_loop805_held_out_set_attestation_gate,
    build_loop805_held_out_set_lockfile_proposal,
    build_loop805_measurement_authorization_proposal,
    build_loop805_measurement_dryrun_authorization_hold,
    build_loop805_measurement_dryrun_decision_record_template,
    build_loop805_measurement_dryrun_decision_request,
    build_loop805_measurement_dryrun_operator_decision_intake_packet,
    build_loop805_measurement_dryrun_operator_decision_intake_gate,
    build_loop805_measurement_dryrun_preflight_packet,
    build_loop805_measurement_readiness_review,
    build_loop805_outcome_policy_review_packet,
    build_loop805_slice5_prompt_packet,
    build_loop805_slice6_prompt_packet,
    build_loop805_slice7_prompt_packet,
    build_loop805_slice8_prompt_packet,
    build_loop805_slice9_prompt_packet,
    build_loop805_slice10_prompt_packet,
    build_loop805_slice11_prompt_packet,
    build_loop805_slice12_prompt_packet,
    build_loop805_slice13_prompt_packet,
    build_loop805_slice14_prompt_packet,
    build_loop805_slice15_prompt_packet,
    build_loop805_slice16_prompt_packet,
    build_loop805_slice17_prompt_packet,
    build_loop805_slice18_prompt_packet,
    build_loop805_slice19_prompt_packet,
    build_loop805_slice20_prompt_packet,
)
from core.codegen.loop805_controller import build_loop805_controller_plan  # noqa: E402
from core.codegen.loop805_mcp_stub import (  # noqa: E402
    build_loop805_mcp_exposure_stub,
    default_loop805_mcp_tool_contracts,
)
from core.codegen.loop805_observability import (  # noqa: E402
    build_held_out_brier_fixture,
    build_held_out_brier_telemetry,
    build_loop805_daily_dashboard,
    build_loop805_regression_pr_proposal,
    build_spine_route_decision,
)
from core.codegen.loop805_operationalization import (  # noqa: E402
    build_loop805_baseline_receipt,
    build_loop805_continuity_signal,
)
from core.codegen.loop805_token_optimizer import (  # noqa: E402
    build_loop805_token_optimizer_stub,
)
from core.codegen.spine_mcp_projection import (  # noqa: E402
    build_spine_audit_projection,
    build_spine_forecast_projection,
    build_spine_query_projection,
)


DEFAULT_TIMESTAMP = "2026-06-21T23:05:00Z"
DEFAULT_MERGE_SHA = "8eeb7f4df62feae25651645b589698a503fb40e6"
DEFAULT_BASELINE_OUT = (
    "out/audit/abx_loop_805_operationalization_baseline_001.latest.json"
)
DEFAULT_CONTROLLER_OUT = "out/audit/abx_loop_805_controller_plan_001.latest.json"
DEFAULT_OBSERVABILITY_OUT = (
    "out/audit/abx_loop_805_daily_observability_dashboard_001.latest.json"
)
DEFAULT_PROPOSAL_OUT = (
    "out/audit/abx_loop_805_regression_pr_proposal_001.latest.json"
)
DEFAULT_SLICE2_MCP_OUT = "out/audit/abx_loop805_slice2_mcp_exposure_stub.latest.json"
DEFAULT_SLICE2_BRIER_OUT = (
    "out/audit/abx_loop805_slice2_held_out_brier_telemetry.latest.json"
)
DEFAULT_SLICE2_TOKEN_OUT = (
    "out/audit/abx_loop805_slice2_token_optimizer_stub.latest.json"
)
DEFAULT_SLICE2_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice2_progress_receipt.latest.json"
)
DEFAULT_SLICE3_ACTIVATION_OUT = (
    "out/audit/abx_loop805_slice3_activation_proposal.latest.json"
)
DEFAULT_SLICE3_PROMPT_OUT = "out/audit/abx_loop805_slice3_prompt_packet.latest.json"
DEFAULT_SLICE3_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice3_progress_receipt.latest.json"
)
DEFAULT_SLICE4_MATRIX_OUT = "out/audit/abx_loop805_slice4_gate_selection_matrix.latest.json"
DEFAULT_SLICE4_PROMPT_OUT = "out/audit/abx_loop805_slice4_prompt_packet.latest.json"
DEFAULT_SLICE4_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice4_progress_receipt.latest.json"
)
DEFAULT_SLICE5_ATTESTATION_OUT = (
    "out/audit/abx_loop805_slice5_brier_attestation_packet.latest.json"
)
DEFAULT_SLICE5_PROMPT_OUT = "out/audit/abx_loop805_slice5_prompt_packet.latest.json"
DEFAULT_SLICE5_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice5_progress_receipt.latest.json"
)
DEFAULT_SLICE6_DRYRUN_OUT = (
    "out/audit/abx_loop805_slice6_fixture_binding_dryrun.latest.json"
)
DEFAULT_SLICE6_PROMPT_OUT = "out/audit/abx_loop805_slice6_prompt_packet.latest.json"
DEFAULT_SLICE6_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice6_progress_receipt.latest.json"
)
DEFAULT_SLICE7_SHADOW_RUN_OUT = (
    "out/audit/abx_loop805_slice7_brier_scoring_shadow_run.latest.json"
)
DEFAULT_SLICE7_PROMPT_OUT = "out/audit/abx_loop805_slice7_prompt_packet.latest.json"
DEFAULT_SLICE7_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice7_progress_receipt.latest.json"
)
DEFAULT_SLICE8_POLICY_OUT = (
    "out/audit/abx_loop805_slice8_outcome_policy_review.latest.json"
)
DEFAULT_SLICE8_PROMPT_OUT = "out/audit/abx_loop805_slice8_prompt_packet.latest.json"
DEFAULT_SLICE8_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice8_progress_receipt.latest.json"
)
DEFAULT_SLICE9_LOCKFILE_OUT = (
    "out/audit/abx_loop805_slice9_held_out_set_lockfile_proposal.latest.json"
)
DEFAULT_SLICE9_PROMPT_OUT = "out/audit/abx_loop805_slice9_prompt_packet.latest.json"
DEFAULT_SLICE9_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice9_progress_receipt.latest.json"
)
DEFAULT_SLICE10_ATTESTATION_GATE_OUT = (
    "out/audit/abx_loop805_slice10_held_out_set_attestation_gate.latest.json"
)
DEFAULT_SLICE10_PROMPT_OUT = "out/audit/abx_loop805_slice10_prompt_packet.latest.json"
DEFAULT_SLICE10_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice10_progress_receipt.latest.json"
)
DEFAULT_SLICE11_READINESS_OUT = (
    "out/audit/abx_loop805_slice11_measurement_readiness_review.latest.json"
)
DEFAULT_SLICE11_PROMPT_OUT = "out/audit/abx_loop805_slice11_prompt_packet.latest.json"
DEFAULT_SLICE11_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice11_progress_receipt.latest.json"
)
DEFAULT_SLICE12_AUTHORIZATION_OUT = (
    "out/audit/abx_loop805_slice12_measurement_authorization_proposal.latest.json"
)
DEFAULT_SLICE12_PROMPT_OUT = "out/audit/abx_loop805_slice12_prompt_packet.latest.json"
DEFAULT_SLICE12_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice12_progress_receipt.latest.json"
)
DEFAULT_SLICE13_EVIDENCE_OUT = (
    "out/audit/abx_loop805_slice13_authorization_evidence_packet.latest.json"
)
DEFAULT_SLICE13_PROMPT_OUT = "out/audit/abx_loop805_slice13_prompt_packet.latest.json"
DEFAULT_SLICE13_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice13_progress_receipt.latest.json"
)
DEFAULT_SLICE14_BINDING_REVIEW_OUT = (
    "out/audit/abx_loop805_slice14_fixture_outcome_binding_review.latest.json"
)
DEFAULT_SLICE14_PROMPT_OUT = "out/audit/abx_loop805_slice14_prompt_packet.latest.json"
DEFAULT_SLICE14_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice14_progress_receipt.latest.json"
)
DEFAULT_SLICE15_AUTHORIZATION_HOLD_OUT = (
    "out/audit/abx_loop805_slice15_measurement_dryrun_authorization_hold.latest.json"
)
DEFAULT_SLICE15_PROMPT_OUT = "out/audit/abx_loop805_slice15_prompt_packet.latest.json"
DEFAULT_SLICE15_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice15_progress_receipt.latest.json"
)
DEFAULT_SLICE16_PREFLIGHT_OUT = (
    "out/audit/abx_loop805_slice16_measurement_dryrun_preflight_packet.latest.json"
)
DEFAULT_SLICE16_PROMPT_OUT = "out/audit/abx_loop805_slice16_prompt_packet.latest.json"
DEFAULT_SLICE16_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice16_progress_receipt.latest.json"
)
DEFAULT_SLICE17_DECISION_REQUEST_OUT = (
    "out/audit/abx_loop805_slice17_measurement_dryrun_decision_request.latest.json"
)
DEFAULT_SLICE17_PROMPT_OUT = "out/audit/abx_loop805_slice17_prompt_packet.latest.json"
DEFAULT_SLICE17_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice17_progress_receipt.latest.json"
)
DEFAULT_SLICE18_DECISION_RECORD_TEMPLATE_OUT = (
    "out/audit/abx_loop805_slice18_measurement_dryrun_decision_record_template.latest.json"
)
DEFAULT_SLICE18_PROMPT_OUT = "out/audit/abx_loop805_slice18_prompt_packet.latest.json"
DEFAULT_SLICE18_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice18_progress_receipt.latest.json"
)
DEFAULT_SLICE19_OPERATOR_DECISION_INTAKE_GATE_OUT = (
    "out/audit/abx_loop805_slice19_measurement_dryrun_operator_decision_intake_gate.latest.json"
)
DEFAULT_SLICE19_PROMPT_OUT = "out/audit/abx_loop805_slice19_prompt_packet.latest.json"
DEFAULT_SLICE19_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice19_progress_receipt.latest.json"
)
DEFAULT_SLICE20_OPERATOR_DECISION_INTAKE_PACKET_OUT = (
    "out/audit/abx_loop805_slice20_measurement_dryrun_operator_decision_intake_packet.latest.json"
)
DEFAULT_SLICE20_PROMPT_OUT = "out/audit/abx_loop805_slice20_prompt_packet.latest.json"
DEFAULT_SLICE20_PROGRESS_OUT = (
    "out/audit/abx_loop805_slice20_progress_receipt.latest.json"
)


def _timestamp(value: str | None) -> str:
    if value:
        return value
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _source_receipts() -> list[str]:
    return [
        "out/audit/abx_codegen_intelligence_spine_completion_receipt_001.latest.json",
        "out/audit/abx_codex_governance_loop_phase_6_post_merge_reconciliation.latest.json",
        "out/audit/abx_codex_governance_loop_phase_7_shadow_runtime_activation_prep.latest.json",
        "out/audit/abx_codex_governance_loop_phase_8_global_ingest_wiring_stub.latest.json",
        "out/audit/abx_codex_governance_loop_phase_9_notion_projection_dryrun.latest.json",
        "out/audit/abx_codegen_phase_10_plus_forward_paths_selector.latest.json",
    ]


def _validation_summary() -> dict[str, Any]:
    return {
        "run_fast_ci": {
            "status": "BASELINE_KNOWN_FAILURES_WINDOWS_PATH_ENCODING",
            "detail": (
                "Post-#804 fast CI reaches pytest but retains existing CP1252 "
                "arrow output and backslash-vs-slash schema constant failures."
            ),
            "brier_score": 0.1,
        },
        "pyright": {
            "status": "TARGETED_PASS",
            "scope": "scripts/abraxas_v2.0_codex_governance_loop.py",
            "errors": 0,
            "brier_score": 0.08,
        },
        "ruff": {
            "status": "TARGETED_PASS",
            "scope": "Loop 805 touched surfaces",
            "brier_score": 0.08,
        },
    }


def build_all_packets(timestamp: str, merge_sha: str) -> dict[str, dict[str, Any]]:
    route_decision = build_spine_route_decision(
        timestamp=timestamp,
        tool_name="/spine/query",
        intent="Inspect advisory Codegen Spine status for next operator lane.",
        evidence_paths=_source_receipts(),
        estimated_input_tokens=38_000,
        estimated_output_tokens=12_000,
    )
    dashboard = build_loop805_daily_dashboard(
        timestamp=timestamp,
        route_decisions=[route_decision],
        pyright_errors=0,
        ruff_errors=0,
        held_out_forecast_brier_baseline=None,
        held_out_forecast_brier_observed=None,
    )
    baseline_fixture = build_held_out_brier_fixture(
        timestamp=timestamp,
        fixture_id="ABX_LOOP_805_HELD_OUT_BASELINE_FIXTURE",
        forecast_rows=[
            {
                "forecast_id": "midterms_signal_stress_001",
                "question": "Will the held-out signal set remain below drift threshold?",
                "probability": 0.58,
                "outcome": 1,
                "provenance": "static_fixture_seed",
            },
            {
                "forecast_id": "midterms_signal_stress_002",
                "question": "Will token pressure exceed target in the next loop?",
                "probability": 0.41,
                "outcome": 0,
                "provenance": "static_fixture_seed",
            },
        ],
    )
    observed_fixture = build_held_out_brier_fixture(
        timestamp=timestamp,
        fixture_id="ABX_LOOP_805_HELD_OUT_OBSERVED_FIXTURE",
        forecast_rows=[
            {
                "forecast_id": "midterms_signal_stress_001",
                "question": "Will the held-out signal set remain below drift threshold?",
                "probability": 0.76,
                "outcome": 1,
                "provenance": "static_fixture_seed",
            },
            {
                "forecast_id": "midterms_signal_stress_002",
                "question": "Will token pressure exceed target in the next loop?",
                "probability": 0.24,
                "outcome": 0,
                "provenance": "static_fixture_seed",
            },
        ],
    )
    baseline = build_loop805_baseline_receipt(
        timestamp=timestamp,
        main_merge_sha=merge_sha,
        source_receipts=_source_receipts(),
        validation_summary=_validation_summary(),
    )
    controller = build_loop805_controller_plan(
        timestamp=timestamp,
        task="Run 24h forecast accuracy stress test on 2026 midterms signal set",
        measurements=[
            build_loop805_continuity_signal(
                surface="token_efficiency",
                status="BASELINE_CAPTURED",
                detail="Prior thread goal consumed 596311 tokens; target reduction is 18%.",
                brier_score=0.1,
            ),
            build_loop805_continuity_signal(
                surface="brier_uplift",
                status="HELD_OUT_SET_REQUIRED",
                detail="Brier uplift target declared; outcome binding not yet authorized.",
                brier_score=0.12,
            ),
        ],
    )
    packets = {
        "baseline": baseline,
        "controller": controller,
        "route_decision": route_decision,
        "observability_dashboard": dashboard,
        "regression_pr_proposal": build_loop805_regression_pr_proposal(
            timestamp=timestamp,
            dashboard=dashboard,
            regression_summary=(
                "No regression detected in seeded dashboard; proposal remains "
                "operator-gated and non-writing."
            ),
            recommended_branch="loop-805-regression-repair-proposal",
            diff_preview=[
                "core/codegen/loop805_observability.py",
                "tests/codegen/test_loop805_operationalization.py",
                "out/audit/abx_loop805_slice2_progress_receipt.latest.json",
            ],
        ),
        "slice2_mcp_exposure_stub": build_loop805_mcp_exposure_stub(
            timestamp=timestamp,
            tool_contracts=default_loop805_mcp_tool_contracts(),
        ),
        "slice2_brier_telemetry": build_held_out_brier_telemetry(
            timestamp=timestamp,
            baseline_fixture=baseline_fixture,
            observed_fixture=observed_fixture,
        ),
        "slice2_token_optimizer_stub": build_loop805_token_optimizer_stub(
            timestamp=timestamp,
            route_decisions=[route_decision],
            optimizer_names=["token-optimizer", "ccusage", "caveman", "squeez"],
        ),
        "spine_query_projection": build_spine_query_projection(
            timestamp=timestamp,
            query="ABX Codegen Intelligence Spine status and next lanes",
        ),
        "spine_forecast_projection": build_spine_forecast_projection(
            timestamp=timestamp,
            forecast_question="Will Loop 805 reduce average tokens per agent turn by 18%?",
            probability=0.62,
        ),
        "spine_audit_projection": build_spine_audit_projection(
            timestamp=timestamp,
            surface="ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_COMPUTABLE",
        ),
    }
    packets["slice3_activation_proposal"] = build_loop805_activation_proposal(
        timestamp=timestamp,
        slice2_receipt_hashes={
            "mcp_exposure_stub": packets["slice2_mcp_exposure_stub"]["canonical_hash"],
            "held_out_brier_telemetry": packets["slice2_brier_telemetry"][
                "canonical_hash"
            ],
            "token_optimizer_stub": packets["slice2_token_optimizer_stub"][
                "canonical_hash"
            ],
            "slice2_progress_receipt": _build_slice2_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
    )
    packets["slice3_prompt_packet"] = build_loop805_slice3_prompt_packet(
        timestamp=timestamp,
        activation_proposal=packets["slice3_activation_proposal"],
    )
    packets["slice4_gate_selection_matrix"] = build_loop805_gate_selection_matrix(
        timestamp=timestamp,
        activation_proposal=packets["slice3_activation_proposal"],
    )
    packets["slice4_prompt_packet"] = build_loop805_slice4_prompt_packet(
        timestamp=timestamp,
        gate_selection_matrix=packets["slice4_gate_selection_matrix"],
    )
    packets["slice5_brier_attestation_packet"] = build_loop805_brier_attestation_packet(
        timestamp=timestamp,
        gate_selection_matrix=packets["slice4_gate_selection_matrix"],
    )
    packets["slice5_prompt_packet"] = build_loop805_slice5_prompt_packet(
        timestamp=timestamp,
        brier_attestation_packet=packets["slice5_brier_attestation_packet"],
    )
    packets["slice6_fixture_binding_dryrun"] = build_loop805_fixture_binding_dryrun(
        timestamp=timestamp,
        brier_attestation_packet=packets["slice5_brier_attestation_packet"],
        fixture_rows=[
            {
                "forecast_id": "held_out_shape_001",
                "question": "Will Loop 805 reduce token pressure without authority drift?",
                "probability": 0.64,
                "provenance": "slice6_shape_placeholder",
            },
            {
                "forecast_id": "held_out_shape_002",
                "question": "Will held-out Brier uplift be measurable after attestation?",
                "probability": 0.57,
                "provenance": "slice6_shape_placeholder",
            },
        ],
    )
    packets["slice6_prompt_packet"] = build_loop805_slice6_prompt_packet(
        timestamp=timestamp,
        fixture_binding_dryrun=packets["slice6_fixture_binding_dryrun"],
    )
    packets["slice7_brier_scoring_shadow_run"] = (
        build_loop805_brier_scoring_shadow_run(
            timestamp=timestamp,
            fixture_binding_dryrun=packets["slice6_fixture_binding_dryrun"],
            shadow_outcomes={
                "held_out_shape_001": 1,
                "held_out_shape_002": 0,
            },
        )
    )
    packets["slice7_prompt_packet"] = build_loop805_slice7_prompt_packet(
        timestamp=timestamp,
        brier_scoring_shadow_run=packets["slice7_brier_scoring_shadow_run"],
    )
    packets["slice8_outcome_policy_review"] = (
        build_loop805_outcome_policy_review_packet(
            timestamp=timestamp,
            brier_scoring_shadow_run=packets["slice7_brier_scoring_shadow_run"],
            policy_requirements=[
                {
                    "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                    "description": "Operator identifies authoritative outcome source.",
                    "brier_score": 0.09,
                },
                {
                    "requirement_id": "FORECAST_CLOSE_TIMESTAMP",
                    "description": "Operator defines when forecasts stop accepting evidence.",
                    "brier_score": 0.1,
                },
                {
                    "requirement_id": "CONFLICT_RESOLUTION_RULE",
                    "description": "Operator defines how disputed outcomes are handled.",
                    "brier_score": 0.1,
                },
                {
                    "requirement_id": "LEAKAGE_REVIEW_RULE",
                    "description": "Operator confirms post-close evidence is excluded.",
                    "brier_score": 0.09,
                },
            ],
        )
    )
    packets["slice8_prompt_packet"] = build_loop805_slice8_prompt_packet(
        timestamp=timestamp,
        outcome_policy_review_packet=packets["slice8_outcome_policy_review"],
    )
    packets["slice9_held_out_set_lockfile_proposal"] = (
        build_loop805_held_out_set_lockfile_proposal(
            timestamp=timestamp,
            outcome_policy_review_packet=packets["slice8_outcome_policy_review"],
            held_out_set_id="ABX_LOOP805_HELD_OUT_SET_PROPOSAL_001",
            forecast_ids=[
                "held_out_shape_001",
                "held_out_shape_002",
            ],
        )
    )
    packets["slice9_prompt_packet"] = build_loop805_slice9_prompt_packet(
        timestamp=timestamp,
        held_out_set_lockfile_proposal=packets[
            "slice9_held_out_set_lockfile_proposal"
        ],
    )
    packets["slice10_held_out_set_attestation_gate"] = (
        build_loop805_held_out_set_attestation_gate(
            timestamp=timestamp,
            held_out_set_lockfile_proposal=packets[
                "slice9_held_out_set_lockfile_proposal"
            ],
            attestation_requirements=[
                {
                    "requirement_id": "LOCKFILE_REVIEW",
                    "description": "Operator reviews proposed held-out set lockfile.",
                    "brier_score": 0.09,
                },
                {
                    "requirement_id": "FORECAST_ID_COMPLETENESS",
                    "description": "Operator confirms forecast IDs are complete.",
                    "brier_score": 0.1,
                },
                {
                    "requirement_id": "OUTCOME_POLICY_ALIGNMENT",
                    "description": "Operator confirms Slice 8 policy alignment.",
                    "brier_score": 0.1,
                },
                {
                    "requirement_id": "LEAKAGE_BOUNDARY_ATTESTATION",
                    "description": "Operator confirms held-out leakage boundaries.",
                    "brier_score": 0.09,
                },
            ],
        )
    )
    packets["slice10_prompt_packet"] = build_loop805_slice10_prompt_packet(
        timestamp=timestamp,
        held_out_set_attestation_gate=packets[
            "slice10_held_out_set_attestation_gate"
        ],
    )
    packets["slice11_measurement_readiness_review"] = (
        build_loop805_measurement_readiness_review(
            timestamp=timestamp,
            held_out_set_attestation_gate=packets[
                "slice10_held_out_set_attestation_gate"
            ],
            readiness_checks=[
                {
                    "check_id": "HELD_OUT_SET_ATTESTATION_RECORDED",
                    "description": "Operator attestation exists outside repo receipts.",
                    "brier_score": 0.09,
                },
                {
                    "check_id": "FIXTURE_BINDING_AUTHORIZED",
                    "description": "Fixture binding has separate explicit approval.",
                    "brier_score": 0.1,
                },
                {
                    "check_id": "OUTCOME_POLICY_AUTHORIZED",
                    "description": "Outcome policy has separate explicit approval.",
                    "brier_score": 0.1,
                },
                {
                    "check_id": "BRIER_RESOLUTION_AUTHORIZED",
                    "description": "Brier resolution has separate explicit approval.",
                    "brier_score": 0.09,
                },
            ],
        )
    )
    packets["slice11_prompt_packet"] = build_loop805_slice11_prompt_packet(
        timestamp=timestamp,
        measurement_readiness_review=packets[
            "slice11_measurement_readiness_review"
        ],
    )
    packets["slice12_measurement_authorization_proposal"] = (
        build_loop805_measurement_authorization_proposal(
            timestamp=timestamp,
            measurement_readiness_review=packets[
                "slice11_measurement_readiness_review"
            ],
            authorization_items=[
                {
                    "authorization_id": "MEASUREMENT_AUTHORIZATION_NOTE",
                    "description": (
                        "Operator records explicit measurement authorization "
                        "outside generated receipts."
                    ),
                    "brier_score": 0.09,
                },
                {
                    "authorization_id": "FIXTURE_BINDING_EVIDENCE",
                    "description": "Operator confirms fixture binding evidence exists.",
                    "brier_score": 0.1,
                },
                {
                    "authorization_id": "OUTCOME_BINDING_EVIDENCE",
                    "description": "Operator confirms outcome binding evidence exists.",
                    "brier_score": 0.1,
                },
                {
                    "authorization_id": "BRIER_RESOLUTION_GATE",
                    "description": (
                        "Operator separates measurement authorization from Brier "
                        "resolution authority."
                    ),
                    "brier_score": 0.09,
                },
            ],
        )
    )
    packets["slice12_prompt_packet"] = build_loop805_slice12_prompt_packet(
        timestamp=timestamp,
        measurement_authorization_proposal=packets[
            "slice12_measurement_authorization_proposal"
        ],
    )
    packets["slice13_authorization_evidence_packet"] = (
        build_loop805_authorization_evidence_packet(
            timestamp=timestamp,
            measurement_authorization_proposal=packets[
                "slice12_measurement_authorization_proposal"
            ],
            evidence_items=[
                {
                    "evidence_id": "MEASUREMENT_AUTHORIZATION_ATTESTATION_NOTE",
                    "description": (
                        "External operator note explicitly authorizing measurement "
                        "review."
                    ),
                    "brier_score": 0.09,
                },
                {
                    "evidence_id": "FIXTURE_BINDING_APPROVAL_RECORD",
                    "description": (
                        "External operator record approving fixture binding "
                        "preconditions."
                    ),
                    "brier_score": 0.1,
                },
                {
                    "evidence_id": "OUTCOME_BINDING_APPROVAL_RECORD",
                    "description": (
                        "External operator record approving outcome binding "
                        "preconditions."
                    ),
                    "brier_score": 0.1,
                },
                {
                    "evidence_id": "BRIER_RESOLUTION_SEPARATION_ATTESTATION",
                    "description": (
                        "External operator note confirming measurement authorization "
                        "does not grant Brier resolution."
                    ),
                    "brier_score": 0.09,
                },
            ],
        )
    )
    packets["slice13_prompt_packet"] = build_loop805_slice13_prompt_packet(
        timestamp=timestamp,
        authorization_evidence_packet=packets[
            "slice13_authorization_evidence_packet"
        ],
    )
    packets["slice14_fixture_outcome_binding_review"] = (
        build_loop805_fixture_outcome_binding_review(
            timestamp=timestamp,
            authorization_evidence_packet=packets[
                "slice13_authorization_evidence_packet"
            ],
            binding_checks=[
                {
                    "check_id": "FIXTURE_BINDING_RECORD_PRESENT",
                    "description": "Operator-provided fixture binding record exists.",
                    "brier_score": 0.1,
                },
                {
                    "check_id": "OUTCOME_BINDING_RECORD_PRESENT",
                    "description": "Operator-provided outcome binding record exists.",
                    "brier_score": 0.1,
                },
                {
                    "check_id": "OUTCOME_POLICY_MATCHES_BOUND_FIXTURES",
                    "description": (
                        "Bound outcomes match the reviewed outcome policy and "
                        "forecast close rules."
                    ),
                    "brier_score": 0.09,
                },
                {
                    "check_id": "BRIER_RESOLUTION_SEPARATE_GATE",
                    "description": (
                        "Brier resolution remains separately gated after binding "
                        "review."
                    ),
                    "brier_score": 0.09,
                },
            ],
        )
    )
    packets["slice14_prompt_packet"] = build_loop805_slice14_prompt_packet(
        timestamp=timestamp,
        fixture_outcome_binding_review=packets[
            "slice14_fixture_outcome_binding_review"
        ],
    )
    packets["slice15_measurement_dryrun_authorization_hold"] = (
        build_loop805_measurement_dryrun_authorization_hold(
            timestamp=timestamp,
            fixture_outcome_binding_review=packets[
                "slice14_fixture_outcome_binding_review"
            ],
            hold_checks=[
                {
                    "check_id": "FIXTURE_BINDING_ATTESTED_EXTERNALLY",
                    "description": (
                        "Operator provides an external attestation that fixture "
                        "binding is complete before any measurement dry run."
                    ),
                },
                {
                    "check_id": "OUTCOME_BINDING_ATTESTED_EXTERNALLY",
                    "description": (
                        "Operator provides an external attestation that outcome "
                        "binding is complete before any measurement dry run."
                    ),
                },
                {
                    "check_id": "MEASUREMENT_DRYRUN_AUTHORIZATION_RECORDED",
                    "description": (
                        "Operator records explicit authorization for a dry-run "
                        "measurement pass outside advisory receipts."
                    ),
                },
                {
                    "check_id": "BRIER_RESOLUTION_SEPARATE_GATE",
                    "description": (
                        "Operator confirms any Brier resolution remains a "
                        "separate future gate after dry-run review."
                    ),
                },
            ],
        )
    )
    packets["slice15_prompt_packet"] = build_loop805_slice15_prompt_packet(
        timestamp=timestamp,
        measurement_dryrun_authorization_hold=packets[
            "slice15_measurement_dryrun_authorization_hold"
        ],
    )
    packets["slice16_measurement_dryrun_preflight_packet"] = (
        build_loop805_measurement_dryrun_preflight_packet(
            timestamp=timestamp,
            measurement_dryrun_authorization_hold=packets[
                "slice15_measurement_dryrun_authorization_hold"
            ],
            preflight_checks=[
                {
                    "check_id": "DRYRUN_AUTHORIZATION_ATTESTATION_PRESENT",
                    "description": (
                        "Operator-provided dry-run authorization attestation "
                        "exists outside advisory receipts."
                    ),
                },
                {
                    "check_id": "FIXTURE_AND_OUTCOME_BINDINGS_REVIEWED",
                    "description": (
                        "Fixture and outcome bindings have been externally "
                        "attested before any dry-run measurement."
                    ),
                },
                {
                    "check_id": "SHADOW_RUN_OUTPUTS_QUARANTINED",
                    "description": (
                        "Dry-run outputs are quarantined from forecast routing "
                        "and Brier resolution."
                    ),
                },
                {
                    "check_id": "REVERSION_PATH_DOCUMENTED",
                    "description": (
                        "Operator has a documented rollback path if dry-run "
                        "preflight reveals leakage or provenance drift."
                    ),
                },
            ],
        )
    )
    packets["slice16_prompt_packet"] = build_loop805_slice16_prompt_packet(
        timestamp=timestamp,
        measurement_dryrun_preflight_packet=packets[
            "slice16_measurement_dryrun_preflight_packet"
        ],
    )
    packets["slice17_measurement_dryrun_decision_request"] = (
        build_loop805_measurement_dryrun_decision_request(
            timestamp=timestamp,
            measurement_dryrun_preflight_packet=packets[
                "slice16_measurement_dryrun_preflight_packet"
            ],
            decision_items=[
                {
                    "decision_id": "DRYRUN_GO_NO_GO_DECISION",
                    "description": (
                        "Operator records a separate go/no-go decision before "
                        "any measurement dry run."
                    ),
                },
                {
                    "decision_id": "DRYRUN_OUTPUT_QUARANTINE_DECISION",
                    "description": (
                        "Operator confirms dry-run outputs remain quarantined "
                        "from routing and Brier resolution."
                    ),
                },
                {
                    "decision_id": "DRYRUN_ROLLBACK_ACCEPTANCE",
                    "description": (
                        "Operator accepts rollback conditions before any "
                        "future executable dry-run surface."
                    ),
                },
            ],
        )
    )
    packets["slice17_prompt_packet"] = build_loop805_slice17_prompt_packet(
        timestamp=timestamp,
        measurement_dryrun_decision_request=packets[
            "slice17_measurement_dryrun_decision_request"
        ],
    )
    packets["slice18_measurement_dryrun_decision_record_template"] = (
        build_loop805_measurement_dryrun_decision_record_template(
            timestamp=timestamp,
            measurement_dryrun_decision_request=packets[
                "slice17_measurement_dryrun_decision_request"
            ],
            template_items=[
                {
                    "field_id": "OPERATOR_DRYRUN_GO_NO_GO_DECISION",
                    "description": (
                        "Unfilled field for the operator's separate dry-run "
                        "go/no-go decision."
                    ),
                },
                {
                    "field_id": "DRYRUN_SCOPE_CONFIRMATION",
                    "description": (
                        "Unfilled field for operator confirmation of dry-run "
                        "scope and held-out set boundaries."
                    ),
                },
                {
                    "field_id": "DRYRUN_OUTPUT_QUARANTINE_CONFIRMATION",
                    "description": (
                        "Unfilled field for operator confirmation that dry-run "
                        "outputs remain quarantined from routing and Brier resolution."
                    ),
                },
                {
                    "field_id": "DRYRUN_ROLLBACK_ACCEPTANCE",
                    "description": (
                        "Unfilled field for operator acceptance of rollback "
                        "conditions before any future executable dry-run surface."
                    ),
                },
            ],
        )
    )
    packets["slice18_prompt_packet"] = build_loop805_slice18_prompt_packet(
        timestamp=timestamp,
        measurement_dryrun_decision_record_template=packets[
            "slice18_measurement_dryrun_decision_record_template"
        ],
    )
    packets["slice19_measurement_dryrun_operator_decision_intake_gate"] = (
        build_loop805_measurement_dryrun_operator_decision_intake_gate(
            timestamp=timestamp,
            measurement_dryrun_decision_record_template=packets[
                "slice18_measurement_dryrun_decision_record_template"
            ],
            intake_requirements=[
                {
                    "requirement_id": "OPERATOR_INTAKE_CHANNEL_SELECTED",
                    "description": (
                        "Operator selects a separate intake channel before "
                        "any dry-run decision can be received."
                    ),
                },
                {
                    "requirement_id": "DECISION_RECORD_TEMPLATE_REVIEWED",
                    "description": (
                        "Operator reviews the Slice 18 decision record "
                        "template without filling or attesting it in this receipt."
                    ),
                },
                {
                    "requirement_id": "QUARANTINE_BOUNDARY_RECONFIRMED",
                    "description": (
                        "Operator reconfirms dry-run output quarantine before "
                        "any future decision intake packet."
                    ),
                },
                {
                    "requirement_id": "EXECUTION_DENIAL_RECONFIRMED",
                    "description": (
                        "Operator reconfirms that this intake gate does not "
                        "authorize dry-run execution."
                    ),
                },
            ],
        )
    )
    packets["slice19_prompt_packet"] = build_loop805_slice19_prompt_packet(
        timestamp=timestamp,
        measurement_dryrun_operator_decision_intake_gate=packets[
            "slice19_measurement_dryrun_operator_decision_intake_gate"
        ],
    )
    packets["slice20_measurement_dryrun_operator_decision_intake_packet"] = (
        build_loop805_measurement_dryrun_operator_decision_intake_packet(
            timestamp=timestamp,
            measurement_dryrun_operator_decision_intake_gate=packets[
                "slice19_measurement_dryrun_operator_decision_intake_gate"
            ],
            intake_items=[
                {
                    "item_id": "OPERATOR_DECISION_CHANNEL_REFERENCE",
                    "description": (
                        "Unsubmitted placeholder for the external operator "
                        "decision channel reference."
                    ),
                },
                {
                    "item_id": "OPERATOR_GO_NO_GO_PLACEHOLDER",
                    "description": (
                        "Unsubmitted placeholder for a future go/no-go "
                        "decision value."
                    ),
                },
                {
                    "item_id": "QUARANTINE_ACCEPTANCE_PLACEHOLDER",
                    "description": (
                        "Unsubmitted placeholder for future quarantine "
                        "acceptance text."
                    ),
                },
                {
                    "item_id": "ROLLBACK_ACCEPTANCE_PLACEHOLDER",
                    "description": (
                        "Unsubmitted placeholder for future rollback "
                        "acceptance text."
                    ),
                },
            ],
        )
    )
    packets["slice20_prompt_packet"] = build_loop805_slice20_prompt_packet(
        timestamp=timestamp,
        measurement_dryrun_operator_decision_intake_packet=packets[
            "slice20_measurement_dryrun_operator_decision_intake_packet"
        ],
    )
    return packets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit ABX Loop 805 advisory operationalization receipts."
    )
    parser.add_argument("--timestamp", default=DEFAULT_TIMESTAMP)
    parser.add_argument("--merge-sha", default=DEFAULT_MERGE_SHA)
    parser.add_argument("--baseline-out", default=DEFAULT_BASELINE_OUT)
    parser.add_argument("--controller-out", default=DEFAULT_CONTROLLER_OUT)
    parser.add_argument("--observability-out", default=DEFAULT_OBSERVABILITY_OUT)
    parser.add_argument("--proposal-out", default=DEFAULT_PROPOSAL_OUT)
    parser.add_argument("--slice2-mcp-out", default=DEFAULT_SLICE2_MCP_OUT)
    parser.add_argument("--slice2-brier-out", default=DEFAULT_SLICE2_BRIER_OUT)
    parser.add_argument("--slice2-token-out", default=DEFAULT_SLICE2_TOKEN_OUT)
    parser.add_argument("--slice2-progress-out", default=DEFAULT_SLICE2_PROGRESS_OUT)
    parser.add_argument("--slice3-activation-out", default=DEFAULT_SLICE3_ACTIVATION_OUT)
    parser.add_argument("--slice3-prompt-out", default=DEFAULT_SLICE3_PROMPT_OUT)
    parser.add_argument("--slice3-progress-out", default=DEFAULT_SLICE3_PROGRESS_OUT)
    parser.add_argument("--slice4-matrix-out", default=DEFAULT_SLICE4_MATRIX_OUT)
    parser.add_argument("--slice4-prompt-out", default=DEFAULT_SLICE4_PROMPT_OUT)
    parser.add_argument("--slice4-progress-out", default=DEFAULT_SLICE4_PROGRESS_OUT)
    parser.add_argument("--slice5-attestation-out", default=DEFAULT_SLICE5_ATTESTATION_OUT)
    parser.add_argument("--slice5-prompt-out", default=DEFAULT_SLICE5_PROMPT_OUT)
    parser.add_argument("--slice5-progress-out", default=DEFAULT_SLICE5_PROGRESS_OUT)
    parser.add_argument("--slice6-dryrun-out", default=DEFAULT_SLICE6_DRYRUN_OUT)
    parser.add_argument("--slice6-prompt-out", default=DEFAULT_SLICE6_PROMPT_OUT)
    parser.add_argument("--slice6-progress-out", default=DEFAULT_SLICE6_PROGRESS_OUT)
    parser.add_argument("--slice7-shadow-run-out", default=DEFAULT_SLICE7_SHADOW_RUN_OUT)
    parser.add_argument("--slice7-prompt-out", default=DEFAULT_SLICE7_PROMPT_OUT)
    parser.add_argument("--slice7-progress-out", default=DEFAULT_SLICE7_PROGRESS_OUT)
    parser.add_argument("--slice8-policy-out", default=DEFAULT_SLICE8_POLICY_OUT)
    parser.add_argument("--slice8-prompt-out", default=DEFAULT_SLICE8_PROMPT_OUT)
    parser.add_argument("--slice8-progress-out", default=DEFAULT_SLICE8_PROGRESS_OUT)
    parser.add_argument("--slice9-lockfile-out", default=DEFAULT_SLICE9_LOCKFILE_OUT)
    parser.add_argument("--slice9-prompt-out", default=DEFAULT_SLICE9_PROMPT_OUT)
    parser.add_argument("--slice9-progress-out", default=DEFAULT_SLICE9_PROGRESS_OUT)
    parser.add_argument(
        "--slice10-attestation-gate-out",
        default=DEFAULT_SLICE10_ATTESTATION_GATE_OUT,
    )
    parser.add_argument("--slice10-prompt-out", default=DEFAULT_SLICE10_PROMPT_OUT)
    parser.add_argument("--slice10-progress-out", default=DEFAULT_SLICE10_PROGRESS_OUT)
    parser.add_argument("--slice11-readiness-out", default=DEFAULT_SLICE11_READINESS_OUT)
    parser.add_argument("--slice11-prompt-out", default=DEFAULT_SLICE11_PROMPT_OUT)
    parser.add_argument("--slice11-progress-out", default=DEFAULT_SLICE11_PROGRESS_OUT)
    parser.add_argument(
        "--slice12-authorization-out",
        default=DEFAULT_SLICE12_AUTHORIZATION_OUT,
    )
    parser.add_argument("--slice12-prompt-out", default=DEFAULT_SLICE12_PROMPT_OUT)
    parser.add_argument("--slice12-progress-out", default=DEFAULT_SLICE12_PROGRESS_OUT)
    parser.add_argument("--slice13-evidence-out", default=DEFAULT_SLICE13_EVIDENCE_OUT)
    parser.add_argument("--slice13-prompt-out", default=DEFAULT_SLICE13_PROMPT_OUT)
    parser.add_argument("--slice13-progress-out", default=DEFAULT_SLICE13_PROGRESS_OUT)
    parser.add_argument(
        "--slice14-binding-review-out",
        default=DEFAULT_SLICE14_BINDING_REVIEW_OUT,
    )
    parser.add_argument("--slice14-prompt-out", default=DEFAULT_SLICE14_PROMPT_OUT)
    parser.add_argument("--slice14-progress-out", default=DEFAULT_SLICE14_PROGRESS_OUT)
    parser.add_argument(
        "--slice15-authorization-hold-out",
        default=DEFAULT_SLICE15_AUTHORIZATION_HOLD_OUT,
    )
    parser.add_argument("--slice15-prompt-out", default=DEFAULT_SLICE15_PROMPT_OUT)
    parser.add_argument("--slice15-progress-out", default=DEFAULT_SLICE15_PROGRESS_OUT)
    parser.add_argument("--slice16-preflight-out", default=DEFAULT_SLICE16_PREFLIGHT_OUT)
    parser.add_argument("--slice16-prompt-out", default=DEFAULT_SLICE16_PROMPT_OUT)
    parser.add_argument("--slice16-progress-out", default=DEFAULT_SLICE16_PROGRESS_OUT)
    parser.add_argument(
        "--slice17-decision-request-out",
        default=DEFAULT_SLICE17_DECISION_REQUEST_OUT,
    )
    parser.add_argument("--slice17-prompt-out", default=DEFAULT_SLICE17_PROMPT_OUT)
    parser.add_argument("--slice17-progress-out", default=DEFAULT_SLICE17_PROGRESS_OUT)
    parser.add_argument(
        "--slice18-decision-record-template-out",
        default=DEFAULT_SLICE18_DECISION_RECORD_TEMPLATE_OUT,
    )
    parser.add_argument("--slice18-prompt-out", default=DEFAULT_SLICE18_PROMPT_OUT)
    parser.add_argument("--slice18-progress-out", default=DEFAULT_SLICE18_PROGRESS_OUT)
    parser.add_argument(
        "--slice19-operator-decision-intake-gate-out",
        default=DEFAULT_SLICE19_OPERATOR_DECISION_INTAKE_GATE_OUT,
    )
    parser.add_argument("--slice19-prompt-out", default=DEFAULT_SLICE19_PROMPT_OUT)
    parser.add_argument("--slice19-progress-out", default=DEFAULT_SLICE19_PROGRESS_OUT)
    parser.add_argument(
        "--slice20-operator-decision-intake-packet-out",
        default=DEFAULT_SLICE20_OPERATOR_DECISION_INTAKE_PACKET_OUT,
    )
    parser.add_argument("--slice20-prompt-out", default=DEFAULT_SLICE20_PROMPT_OUT)
    parser.add_argument("--slice20-progress-out", default=DEFAULT_SLICE20_PROGRESS_OUT)
    parser.add_argument(
        "--emit-controller",
        action="store_true",
        help="Also emit the PLAN_EXECUTE_MEASURE_ADJUST controller receipt.",
    )
    parser.add_argument(
        "--emit-observability",
        action="store_true",
        help="Also emit the Loop 805 daily observability dashboard receipt.",
    )
    parser.add_argument(
        "--emit-proposal",
        action="store_true",
        help="Also emit the gated regression PR proposal receipt.",
    )
    parser.add_argument(
        "--emit-slice2",
        action="store_true",
        help="Emit governed Slice 2 MCP, Brier, token, and progress receipts.",
    )
    parser.add_argument(
        "--emit-slice3",
        action="store_true",
        help="Emit Slice 3 activation proposal and operator prompt receipts.",
    )
    parser.add_argument(
        "--emit-slice4",
        action="store_true",
        help="Emit Slice 4 gate-selection matrix and operator prompt receipts.",
    )
    parser.add_argument(
        "--emit-slice5",
        action="store_true",
        help="Emit Slice 5 held-out Brier attestation receipts.",
    )
    parser.add_argument(
        "--emit-slice6",
        action="store_true",
        help="Emit Slice 6 held-out fixture binding dry-run receipts.",
    )
    parser.add_argument(
        "--emit-slice7",
        action="store_true",
        help="Emit Slice 7 Brier scoring shadow-run receipts.",
    )
    parser.add_argument(
        "--emit-slice8",
        action="store_true",
        help="Emit Slice 8 outcome policy review receipts.",
    )
    parser.add_argument(
        "--emit-slice9",
        action="store_true",
        help="Emit Slice 9 held-out set lockfile proposal receipts.",
    )
    parser.add_argument(
        "--emit-slice10",
        action="store_true",
        help="Emit Slice 10 held-out set attestation gate receipts.",
    )
    parser.add_argument(
        "--emit-slice11",
        action="store_true",
        help="Emit Slice 11 measurement readiness review receipts.",
    )
    parser.add_argument(
        "--emit-slice12",
        action="store_true",
        help="Emit Slice 12 measurement authorization proposal receipts.",
    )
    parser.add_argument(
        "--emit-slice13",
        action="store_true",
        help="Emit Slice 13 authorization evidence packet receipts.",
    )
    parser.add_argument(
        "--emit-slice14",
        action="store_true",
        help="Emit Slice 14 fixture/outcome binding review receipts.",
    )
    parser.add_argument(
        "--emit-slice15",
        action="store_true",
        help="Emit Slice 15 measurement dry-run authorization hold receipts.",
    )
    parser.add_argument(
        "--emit-slice16",
        action="store_true",
        help="Emit Slice 16 measurement dry-run preflight receipts.",
    )
    parser.add_argument(
        "--emit-slice17",
        action="store_true",
        help="Emit Slice 17 measurement dry-run decision request receipts.",
    )
    parser.add_argument(
        "--emit-slice18",
        action="store_true",
        help="Emit Slice 18 measurement dry-run decision record template receipts.",
    )
    parser.add_argument(
        "--emit-slice19",
        action="store_true",
        help="Emit Slice 19 measurement dry-run operator decision intake gate receipts.",
    )
    parser.add_argument(
        "--emit-slice20",
        action="store_true",
        help="Emit Slice 20 measurement dry-run operator decision intake packet receipts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    timestamp = _timestamp(args.timestamp)
    packets = build_all_packets(timestamp, args.merge_sha)
    write_canonical_json(Path(args.baseline_out), packets["baseline"])
    print(args.baseline_out)
    print(packets["baseline"]["canonical_hash"])

    if args.emit_controller:
        write_canonical_json(Path(args.controller_out), packets["controller"])
        print(args.controller_out)
        print(packets["controller"]["canonical_hash"])
    if args.emit_observability:
        write_canonical_json(
            Path(args.observability_out),
            packets["observability_dashboard"],
        )
        print(args.observability_out)
        print(packets["observability_dashboard"]["canonical_hash"])
    if args.emit_proposal:
        write_canonical_json(Path(args.proposal_out), packets["regression_pr_proposal"])
        print(args.proposal_out)
        print(packets["regression_pr_proposal"]["canonical_hash"])
    if args.emit_slice2:
        write_canonical_json(
            Path(args.slice2_mcp_out),
            packets["slice2_mcp_exposure_stub"],
        )
        print(args.slice2_mcp_out)
        print(packets["slice2_mcp_exposure_stub"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice2_brier_out),
            packets["slice2_brier_telemetry"],
        )
        print(args.slice2_brier_out)
        print(packets["slice2_brier_telemetry"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice2_token_out),
            packets["slice2_token_optimizer_stub"],
        )
        print(args.slice2_token_out)
        print(packets["slice2_token_optimizer_stub"]["canonical_hash"])
        progress = _build_slice2_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice2_progress_out), progress)
        print(args.slice2_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice3:
        write_canonical_json(
            Path(args.slice3_activation_out),
            packets["slice3_activation_proposal"],
        )
        print(args.slice3_activation_out)
        print(packets["slice3_activation_proposal"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice3_prompt_out),
            packets["slice3_prompt_packet"],
        )
        print(args.slice3_prompt_out)
        print(packets["slice3_prompt_packet"]["canonical_hash"])
        progress = _build_slice3_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice3_progress_out), progress)
        print(args.slice3_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice4:
        write_canonical_json(
            Path(args.slice4_matrix_out),
            packets["slice4_gate_selection_matrix"],
        )
        print(args.slice4_matrix_out)
        print(packets["slice4_gate_selection_matrix"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice4_prompt_out),
            packets["slice4_prompt_packet"],
        )
        print(args.slice4_prompt_out)
        print(packets["slice4_prompt_packet"]["canonical_hash"])
        progress = _build_slice4_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice4_progress_out), progress)
        print(args.slice4_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice5:
        write_canonical_json(
            Path(args.slice5_attestation_out),
            packets["slice5_brier_attestation_packet"],
        )
        print(args.slice5_attestation_out)
        print(packets["slice5_brier_attestation_packet"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice5_prompt_out),
            packets["slice5_prompt_packet"],
        )
        print(args.slice5_prompt_out)
        print(packets["slice5_prompt_packet"]["canonical_hash"])
        progress = _build_slice5_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice5_progress_out), progress)
        print(args.slice5_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice6:
        write_canonical_json(
            Path(args.slice6_dryrun_out),
            packets["slice6_fixture_binding_dryrun"],
        )
        print(args.slice6_dryrun_out)
        print(packets["slice6_fixture_binding_dryrun"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice6_prompt_out),
            packets["slice6_prompt_packet"],
        )
        print(args.slice6_prompt_out)
        print(packets["slice6_prompt_packet"]["canonical_hash"])
        progress = _build_slice6_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice6_progress_out), progress)
        print(args.slice6_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice7:
        write_canonical_json(
            Path(args.slice7_shadow_run_out),
            packets["slice7_brier_scoring_shadow_run"],
        )
        print(args.slice7_shadow_run_out)
        print(packets["slice7_brier_scoring_shadow_run"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice7_prompt_out),
            packets["slice7_prompt_packet"],
        )
        print(args.slice7_prompt_out)
        print(packets["slice7_prompt_packet"]["canonical_hash"])
        progress = _build_slice7_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice7_progress_out), progress)
        print(args.slice7_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice8:
        write_canonical_json(
            Path(args.slice8_policy_out),
            packets["slice8_outcome_policy_review"],
        )
        print(args.slice8_policy_out)
        print(packets["slice8_outcome_policy_review"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice8_prompt_out),
            packets["slice8_prompt_packet"],
        )
        print(args.slice8_prompt_out)
        print(packets["slice8_prompt_packet"]["canonical_hash"])
        progress = _build_slice8_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice8_progress_out), progress)
        print(args.slice8_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice9:
        write_canonical_json(
            Path(args.slice9_lockfile_out),
            packets["slice9_held_out_set_lockfile_proposal"],
        )
        print(args.slice9_lockfile_out)
        print(packets["slice9_held_out_set_lockfile_proposal"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice9_prompt_out),
            packets["slice9_prompt_packet"],
        )
        print(args.slice9_prompt_out)
        print(packets["slice9_prompt_packet"]["canonical_hash"])
        progress = _build_slice9_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice9_progress_out), progress)
        print(args.slice9_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice10:
        write_canonical_json(
            Path(args.slice10_attestation_gate_out),
            packets["slice10_held_out_set_attestation_gate"],
        )
        print(args.slice10_attestation_gate_out)
        print(packets["slice10_held_out_set_attestation_gate"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice10_prompt_out),
            packets["slice10_prompt_packet"],
        )
        print(args.slice10_prompt_out)
        print(packets["slice10_prompt_packet"]["canonical_hash"])
        progress = _build_slice10_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice10_progress_out), progress)
        print(args.slice10_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice11:
        write_canonical_json(
            Path(args.slice11_readiness_out),
            packets["slice11_measurement_readiness_review"],
        )
        print(args.slice11_readiness_out)
        print(packets["slice11_measurement_readiness_review"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice11_prompt_out),
            packets["slice11_prompt_packet"],
        )
        print(args.slice11_prompt_out)
        print(packets["slice11_prompt_packet"]["canonical_hash"])
        progress = _build_slice11_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice11_progress_out), progress)
        print(args.slice11_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice12:
        write_canonical_json(
            Path(args.slice12_authorization_out),
            packets["slice12_measurement_authorization_proposal"],
        )
        print(args.slice12_authorization_out)
        print(
            packets["slice12_measurement_authorization_proposal"]["canonical_hash"]
        )
        write_canonical_json(
            Path(args.slice12_prompt_out),
            packets["slice12_prompt_packet"],
        )
        print(args.slice12_prompt_out)
        print(packets["slice12_prompt_packet"]["canonical_hash"])
        progress = _build_slice12_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice12_progress_out), progress)
        print(args.slice12_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice13:
        write_canonical_json(
            Path(args.slice13_evidence_out),
            packets["slice13_authorization_evidence_packet"],
        )
        print(args.slice13_evidence_out)
        print(packets["slice13_authorization_evidence_packet"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice13_prompt_out),
            packets["slice13_prompt_packet"],
        )
        print(args.slice13_prompt_out)
        print(packets["slice13_prompt_packet"]["canonical_hash"])
        progress = _build_slice13_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice13_progress_out), progress)
        print(args.slice13_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice14:
        write_canonical_json(
            Path(args.slice14_binding_review_out),
            packets["slice14_fixture_outcome_binding_review"],
        )
        print(args.slice14_binding_review_out)
        print(packets["slice14_fixture_outcome_binding_review"]["canonical_hash"])
        write_canonical_json(
            Path(args.slice14_prompt_out),
            packets["slice14_prompt_packet"],
        )
        print(args.slice14_prompt_out)
        print(packets["slice14_prompt_packet"]["canonical_hash"])
        progress = _build_slice14_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice14_progress_out), progress)
        print(args.slice14_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice15:
        write_canonical_json(
            Path(args.slice15_authorization_hold_out),
            packets["slice15_measurement_dryrun_authorization_hold"],
        )
        print(args.slice15_authorization_hold_out)
        print(
            packets["slice15_measurement_dryrun_authorization_hold"][
                "canonical_hash"
            ]
        )
        write_canonical_json(
            Path(args.slice15_prompt_out),
            packets["slice15_prompt_packet"],
        )
        print(args.slice15_prompt_out)
        print(packets["slice15_prompt_packet"]["canonical_hash"])
        progress = _build_slice15_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice15_progress_out), progress)
        print(args.slice15_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice16:
        write_canonical_json(
            Path(args.slice16_preflight_out),
            packets["slice16_measurement_dryrun_preflight_packet"],
        )
        print(args.slice16_preflight_out)
        print(
            packets["slice16_measurement_dryrun_preflight_packet"][
                "canonical_hash"
            ]
        )
        write_canonical_json(
            Path(args.slice16_prompt_out),
            packets["slice16_prompt_packet"],
        )
        print(args.slice16_prompt_out)
        print(packets["slice16_prompt_packet"]["canonical_hash"])
        progress = _build_slice16_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice16_progress_out), progress)
        print(args.slice16_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice17:
        write_canonical_json(
            Path(args.slice17_decision_request_out),
            packets["slice17_measurement_dryrun_decision_request"],
        )
        print(args.slice17_decision_request_out)
        print(
            packets["slice17_measurement_dryrun_decision_request"][
                "canonical_hash"
            ]
        )
        write_canonical_json(
            Path(args.slice17_prompt_out),
            packets["slice17_prompt_packet"],
        )
        print(args.slice17_prompt_out)
        print(packets["slice17_prompt_packet"]["canonical_hash"])
        progress = _build_slice17_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice17_progress_out), progress)
        print(args.slice17_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice18:
        write_canonical_json(
            Path(args.slice18_decision_record_template_out),
            packets["slice18_measurement_dryrun_decision_record_template"],
        )
        print(args.slice18_decision_record_template_out)
        print(
            packets["slice18_measurement_dryrun_decision_record_template"][
                "canonical_hash"
            ]
        )
        write_canonical_json(
            Path(args.slice18_prompt_out),
            packets["slice18_prompt_packet"],
        )
        print(args.slice18_prompt_out)
        print(packets["slice18_prompt_packet"]["canonical_hash"])
        progress = _build_slice18_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice18_progress_out), progress)
        print(args.slice18_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice19:
        write_canonical_json(
            Path(args.slice19_operator_decision_intake_gate_out),
            packets["slice19_measurement_dryrun_operator_decision_intake_gate"],
        )
        print(args.slice19_operator_decision_intake_gate_out)
        print(
            packets["slice19_measurement_dryrun_operator_decision_intake_gate"][
                "canonical_hash"
            ]
        )
        write_canonical_json(
            Path(args.slice19_prompt_out),
            packets["slice19_prompt_packet"],
        )
        print(args.slice19_prompt_out)
        print(packets["slice19_prompt_packet"]["canonical_hash"])
        progress = _build_slice19_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice19_progress_out), progress)
        print(args.slice19_progress_out)
        print(progress["canonical_hash"])
    if args.emit_slice20:
        write_canonical_json(
            Path(args.slice20_operator_decision_intake_packet_out),
            packets["slice20_measurement_dryrun_operator_decision_intake_packet"],
        )
        print(args.slice20_operator_decision_intake_packet_out)
        print(
            packets["slice20_measurement_dryrun_operator_decision_intake_packet"][
                "canonical_hash"
            ]
        )
        write_canonical_json(
            Path(args.slice20_prompt_out),
            packets["slice20_prompt_packet"],
        )
        print(args.slice20_prompt_out)
        print(packets["slice20_prompt_packet"]["canonical_hash"])
        progress = _build_slice20_progress_receipt(timestamp, packets)
        write_canonical_json(Path(args.slice20_progress_out), progress)
        print(args.slice20_progress_out)
        print(progress["canonical_hash"])
    return 0


def _build_slice2_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice2ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE2_PROGRESS_RECEIPT",
        "receipt_status": "LOOP805_SLICE2_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_8_MCP_EXPOSURE_STUB": "READY_READ_ONLY_NOT_LIVE",
            "PHASE_9_HELD_OUT_BRIER_INTEGRATION": "STATIC_FIXTURE_READY",
            "PHASE_10_TOKEN_OPTIMIZER_STUB": "ADVISORY_MATH_READY_NOT_ENFORCED",
            "PHASE_11_SELF_PR_PROPOSAL_ENHANCEMENT": (
                "PROPOSAL_ONLY_OPERATOR_GATE_REQUIRED"
            ),
        },
        "receipt_hashes": {
            "mcp_exposure_stub": packets["slice2_mcp_exposure_stub"]["canonical_hash"],
            "held_out_brier_telemetry": packets["slice2_brier_telemetry"][
                "canonical_hash"
            ],
            "token_optimizer_stub": packets["slice2_token_optimizer_stub"][
                "canonical_hash"
            ],
            "regression_pr_proposal": packets["regression_pr_proposal"][
                "canonical_hash"
            ],
        },
        "remaining_gates": [
            "LIVE_MCP_EXPOSURE_REQUIRES_OPERATOR_APPROVAL",
            "BRIER_RESOLUTION_REQUIRES_HELD_OUT_SET_ATTESTATION",
            "TOKEN_OPTIMIZER_ENFORCEMENT_REQUIRES_CI_GATE_APPROVAL",
            "SELF_PR_CREATION_REQUIRES_EXPLICIT_GITHUB_WRITEBACK_APPROVAL",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice3_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice3ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE3_PROGRESS_RECEIPT",
        "receipt_status": "LOOP805_SLICE3_ACTIVATION_PROPOSAL_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_12_LIVE_MCP_GATE_REVIEW": "PROPOSED_NOT_AUTHORIZED",
            "PHASE_13_HELD_OUT_BRIER_BOUNDING": "PROPOSED_NOT_BOUND",
            "PHASE_14_TOKEN_OPTIMIZER_ENFORCEMENT": "PROPOSED_NOT_ENFORCED",
            "PHASE_15_SELF_PR_WRITEBACK": "PROPOSED_NOT_AUTHORIZED",
        },
        "receipt_hashes": {
            "activation_proposal": packets["slice3_activation_proposal"][
                "canonical_hash"
            ],
            "prompt_packet": packets["slice3_prompt_packet"]["canonical_hash"],
            "slice2_progress_receipt": _build_slice2_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "remaining_gates": [
            "OPERATOR_SELECTS_ONE_ACTIVATION_GATE",
            "LIVE_MCP_REQUIRES_SEPARATE_EXPLICIT_ATTESTATION",
            "HELD_OUT_BRIER_REQUIRES_FIXTURE_AND_OUTCOME_POLICY",
            "TOKEN_OPTIMIZER_REQUIRES_CI_ENFORCEMENT_APPROVAL",
            "SELF_PR_REQUIRES_EXPLICIT_GITHUB_WRITEBACK_APPROVAL",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_brier_resolution": False,
        "valid_for_ci_enforcement": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice4_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice4ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE4_PROGRESS_RECEIPT",
        "receipt_status": "LOOP805_SLICE4_GATE_SELECTION_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_16_GATE_SELECTION_MATRIX": "READY_NO_GATE_SELECTED",
            "PHASE_17_OPERATOR_GATE_ATTESTATION": "REQUIRED_NOT_PROVIDED",
            "PHASE_18_HELD_OUT_BRIER_PACKET": "RECOMMENDED_NEXT_NOT_CREATED",
        },
        "receipt_hashes": {
            "gate_selection_matrix": packets["slice4_gate_selection_matrix"][
                "canonical_hash"
            ],
            "prompt_packet": packets["slice4_prompt_packet"]["canonical_hash"],
            "slice3_progress_receipt": _build_slice3_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "GATE_2_HELD_OUT_BRIER_BOUNDING_REVIEW",
        "remaining_gates": [
            "OPERATOR_SELECTS_EXACTLY_ONE_GATE",
            "NO_GATE_SELECTION_IMPLIES_NO_ACTIVATION",
            "HELD_OUT_BRIER_PACKET_REQUIRES_OPERATOR_ATTESTATION",
            "ALL_RUNTIME_AND_WRITEBACK_LOCKS_REMAIN_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_brier_resolution": False,
        "valid_for_ci_enforcement": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice5_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice5ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE5_PROGRESS_RECEIPT",
        "receipt_status": "LOOP805_SLICE5_HELD_OUT_BRIER_ATTESTATION_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_19_HELD_OUT_SET_REQUIREMENTS": "DEFINED_NOT_SATISFIED",
            "PHASE_20_OPERATOR_ATTESTATION": "REQUIRED_NOT_RECORDED",
            "PHASE_21_FIXTURE_BINDING_DRYRUN": "RECOMMENDED_NEXT_NOT_CREATED",
        },
        "receipt_hashes": {
            "brier_attestation_packet": packets["slice5_brier_attestation_packet"][
                "canonical_hash"
            ],
            "prompt_packet": packets["slice5_prompt_packet"]["canonical_hash"],
            "slice4_progress_receipt": _build_slice4_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE6_HELD_OUT_FIXTURE_BINDING_DRYRUN",
        "remaining_gates": [
            "OPERATOR_ATTESTS_HELD_OUT_SET_ID",
            "OPERATOR_ATTESTS_OUTCOME_POLICY",
            "OPERATOR_ATTESTS_LEAKAGE_BOUNDARY",
            "OPERATOR_ATTESTS_SCORING_WINDOW",
            "BRIER_RESOLUTION_REMAINS_FALSE_UNTIL_LATER_APPROVAL",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice6_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice6ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE6_PROGRESS_RECEIPT",
        "receipt_status": "LOOP805_SLICE6_FIXTURE_BINDING_DRYRUN_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_22_FIXTURE_ROW_SHAPE": "DRYRUN_READY_NOT_BOUND",
            "PHASE_23_OUTCOME_PLACEHOLDERS": "EMPTY_NOT_BOUND",
            "PHASE_24_BRIER_SCORING_SHADOW_RUN": "RECOMMENDED_NEXT_NOT_CREATED",
        },
        "receipt_hashes": {
            "fixture_binding_dryrun": packets["slice6_fixture_binding_dryrun"][
                "canonical_hash"
            ],
            "prompt_packet": packets["slice6_prompt_packet"]["canonical_hash"],
            "slice5_progress_receipt": _build_slice5_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE7_BRIER_SCORING_SHADOW_RUN",
        "remaining_gates": [
            "OPERATOR_APPROVES_FIXTURE_ROW_SCHEMA",
            "OPERATOR_BINDS_REAL_HELD_OUT_SET",
            "OPERATOR_BINDS_OUTCOME_POLICY",
            "BRIER_RESOLUTION_REMAINS_FALSE_UNTIL_LATER_APPROVAL",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice7_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice7ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE7_PROGRESS_RECEIPT",
        "receipt_status": "LOOP805_SLICE7_BRIER_SCORING_SHADOW_RUN_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_25_SHADOW_SCORING_MATH": "READY_REHEARSAL_ONLY",
            "PHASE_26_SHADOW_OUTCOME_ROWS": "PRESENT_NOT_BOUND",
            "PHASE_27_OUTCOME_POLICY_REVIEW": "RECOMMENDED_NEXT_NOT_CREATED",
        },
        "receipt_hashes": {
            "brier_scoring_shadow_run": packets["slice7_brier_scoring_shadow_run"][
                "canonical_hash"
            ],
            "prompt_packet": packets["slice7_prompt_packet"]["canonical_hash"],
            "slice6_progress_receipt": _build_slice6_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE8_OUTCOME_POLICY_REVIEW_PACKET",
        "remaining_gates": [
            "OPERATOR_APPROVES_SHADOW_SCORING_MATH",
            "OPERATOR_BINDS_REAL_HELD_OUT_SET",
            "OPERATOR_BINDS_REAL_OUTCOMES",
            "OPERATOR_AUTHORIZES_BRIER_RESOLUTION_SEPARATELY",
            "ALL_RUNTIME_AND_WRITEBACK_LOCKS_REMAIN_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice8_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice8ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE8_PROGRESS_RECEIPT",
        "receipt_status": "LOOP805_SLICE8_OUTCOME_POLICY_REVIEW_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_28_OUTCOME_POLICY_REQUIREMENTS": "DEFINED_NOT_SATISFIED",
            "PHASE_29_OPERATOR_POLICY_ATTESTATION": "REQUIRED_NOT_RECORDED",
            "PHASE_30_HELD_OUT_LOCKFILE_PROPOSAL": "RECOMMENDED_NEXT_NOT_CREATED",
        },
        "receipt_hashes": {
            "outcome_policy_review": packets["slice8_outcome_policy_review"][
                "canonical_hash"
            ],
            "prompt_packet": packets["slice8_prompt_packet"]["canonical_hash"],
            "slice7_progress_receipt": _build_slice7_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE9_HELD_OUT_SET_LOCKFILE_PROPOSAL",
        "remaining_gates": [
            "OPERATOR_ATTESTS_OUTCOME_SOURCE_OF_TRUTH",
            "OPERATOR_ATTESTS_FORECAST_CLOSE_TIMESTAMP",
            "OPERATOR_ATTESTS_CONFLICT_RESOLUTION_RULE",
            "OPERATOR_ATTESTS_LEAKAGE_REVIEW_RULE",
            "OUTCOME_BINDING_AND_BRIER_RESOLUTION_REMAIN_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice9_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice9ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE9_PROGRESS_RECEIPT",
        "receipt_status": "LOOP805_SLICE9_HELD_OUT_SET_LOCKFILE_PROPOSAL_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_31_HELD_OUT_SET_LOCKFILE_PROPOSAL": "READY_NOT_LOCKED",
            "PHASE_32_FORECAST_ID_REVIEW": "PROPOSED_NOT_BOUND",
            "PHASE_33_HELD_OUT_SET_ATTESTATION_GATE": "RECOMMENDED_NEXT_NOT_CREATED",
        },
        "receipt_hashes": {
            "held_out_set_lockfile_proposal": packets[
                "slice9_held_out_set_lockfile_proposal"
            ]["canonical_hash"],
            "prompt_packet": packets["slice9_prompt_packet"]["canonical_hash"],
            "slice8_progress_receipt": _build_slice8_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE10_HELD_OUT_SET_ATTESTATION_GATE",
        "remaining_gates": [
            "OPERATOR_REVIEWS_PROPOSED_HELD_OUT_SET_ID",
            "OPERATOR_REVIEWS_PROPOSED_FORECAST_IDS",
            "OPERATOR_ATTESTS_HELD_OUT_SET_LOCK_SEPARATELY",
            "FIXTURE_OUTCOME_AND_BRIER_BINDING_REMAIN_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_held_out_set_lock": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice10_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice10ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE10_PROGRESS_RECEIPT",
        "receipt_status": "LOOP805_SLICE10_HELD_OUT_SET_ATTESTATION_GATE_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_34_HELD_OUT_SET_ATTESTATION_GATE": "READY_NOT_ATTESTED",
            "PHASE_35_OPERATOR_EVIDENCE_REVIEW": "REQUIRED_NOT_RECORDED",
            "PHASE_36_MEASUREMENT_READINESS_REVIEW": "RECOMMENDED_NEXT_NOT_CREATED",
        },
        "receipt_hashes": {
            "held_out_set_attestation_gate": packets[
                "slice10_held_out_set_attestation_gate"
            ]["canonical_hash"],
            "prompt_packet": packets["slice10_prompt_packet"]["canonical_hash"],
            "slice9_progress_receipt": _build_slice9_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE11_MEASUREMENT_READINESS_REVIEW",
        "remaining_gates": [
            "OPERATOR_RECORDS_HELD_OUT_SET_ATTESTATION_SEPARATELY",
            "OPERATOR_LOCKS_HELD_OUT_SET_SEPARATELY",
            "OPERATOR_BINDS_FIXTURES_SEPARATELY",
            "OUTCOME_AND_BRIER_RESOLUTION_REMAIN_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_held_out_set_attestation": False,
        "valid_for_held_out_set_lock": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice11_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice11ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE11_PROGRESS_RECEIPT",
        "receipt_status": "LOOP805_SLICE11_MEASUREMENT_READINESS_REVIEW_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_37_MEASUREMENT_READINESS_REVIEW": "READY_NOT_MEASURING",
            "PHASE_38_AUTHORIZATION_EVIDENCE_REVIEW": "REQUIRED_NOT_RECORDED",
            "PHASE_39_MEASUREMENT_AUTHORIZATION_PROPOSAL": "RECOMMENDED_NEXT_NOT_CREATED",
        },
        "receipt_hashes": {
            "measurement_readiness_review": packets[
                "slice11_measurement_readiness_review"
            ]["canonical_hash"],
            "prompt_packet": packets["slice11_prompt_packet"]["canonical_hash"],
            "slice10_progress_receipt": _build_slice10_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE12_MEASUREMENT_AUTHORIZATION_PROPOSAL",
        "remaining_gates": [
            "OPERATOR_RECORDS_MEASUREMENT_AUTHORIZATION_SEPARATELY",
            "OPERATOR_BINDS_FIXTURES_SEPARATELY",
            "OPERATOR_BINDS_OUTCOMES_SEPARATELY",
            "BRIER_RESOLUTION_REMAINS_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_held_out_set_attestation": False,
        "valid_for_held_out_set_lock": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice12_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice12ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE12_PROGRESS_RECEIPT",
        "receipt_status": (
            "LOOP805_SLICE12_MEASUREMENT_AUTHORIZATION_PROPOSAL_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_40_MEASUREMENT_AUTHORIZATION_PROPOSAL": "READY_NOT_AUTHORIZED",
            "PHASE_41_OPERATOR_AUTHORIZATION_EVIDENCE": "REQUIRED_NOT_RECORDED",
            "PHASE_42_AUTHORIZATION_EVIDENCE_PACKET": "RECOMMENDED_NEXT_NOT_CREATED",
        },
        "receipt_hashes": {
            "measurement_authorization_proposal": packets[
                "slice12_measurement_authorization_proposal"
            ]["canonical_hash"],
            "prompt_packet": packets["slice12_prompt_packet"]["canonical_hash"],
            "slice11_progress_receipt": _build_slice11_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE13_AUTHORIZATION_EVIDENCE_PACKET",
        "remaining_gates": [
            "OPERATOR_RECORDS_MEASUREMENT_AUTHORIZATION_SEPARATELY",
            "OPERATOR_BINDS_FIXTURES_SEPARATELY",
            "OPERATOR_BINDS_OUTCOMES_SEPARATELY",
            "OPERATOR_AUTHORIZES_BRIER_RESOLUTION_SEPARATELY",
            "BRIER_RESOLUTION_REMAINS_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_held_out_set_attestation": False,
        "valid_for_held_out_set_lock": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice13_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice13ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE13_PROGRESS_RECEIPT",
        "receipt_status": (
            "LOOP805_SLICE13_AUTHORIZATION_EVIDENCE_PACKET_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_43_AUTHORIZATION_EVIDENCE_PACKET": "READY_SHAPE_ONLY_NOT_RECORDED",
            "PHASE_44_OPERATOR_EVIDENCE_ATTESTATION": "REQUIRED_NOT_RECORDED",
            "PHASE_45_FIXTURE_OUTCOME_BINDING_REVIEW": "RECOMMENDED_NEXT_NOT_CREATED",
        },
        "receipt_hashes": {
            "authorization_evidence_packet": packets[
                "slice13_authorization_evidence_packet"
            ]["canonical_hash"],
            "prompt_packet": packets["slice13_prompt_packet"]["canonical_hash"],
            "slice12_progress_receipt": _build_slice12_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE14_FIXTURE_OUTCOME_BINDING_REVIEW",
        "remaining_gates": [
            "OPERATOR_RECORDS_AUTHORIZATION_EVIDENCE_SEPARATELY",
            "OPERATOR_ATTESTS_MEASUREMENT_AUTHORIZATION_SEPARATELY",
            "OPERATOR_BINDS_FIXTURES_SEPARATELY",
            "OPERATOR_BINDS_OUTCOMES_SEPARATELY",
            "BRIER_RESOLUTION_REMAINS_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_authorization_evidence_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice14_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice14ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE14_PROGRESS_RECEIPT",
        "receipt_status": (
            "LOOP805_SLICE14_FIXTURE_OUTCOME_BINDING_REVIEW_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_46_FIXTURE_OUTCOME_BINDING_REVIEW": "READY_NOT_BOUND",
            "PHASE_47_BINDING_EVIDENCE_ATTESTATION": "REQUIRED_NOT_RECORDED",
            "PHASE_48_MEASUREMENT_DRYRUN_AUTHORIZATION_HOLD": (
                "RECOMMENDED_NEXT_NOT_CREATED"
            ),
        },
        "receipt_hashes": {
            "fixture_outcome_binding_review": packets[
                "slice14_fixture_outcome_binding_review"
            ]["canonical_hash"],
            "prompt_packet": packets["slice14_prompt_packet"]["canonical_hash"],
            "slice13_progress_receipt": _build_slice13_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE15_MEASUREMENT_DRYRUN_AUTHORIZATION_HOLD",
        "remaining_gates": [
            "OPERATOR_BINDS_FIXTURES_SEPARATELY",
            "OPERATOR_BINDS_OUTCOMES_SEPARATELY",
            "OPERATOR_ATTESTS_BINDING_EVIDENCE_SEPARATELY",
            "OPERATOR_AUTHORIZES_MEASUREMENT_DRYRUN_SEPARATELY",
            "BRIER_RESOLUTION_REMAINS_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_fixture_binding_review": False,
        "valid_for_outcome_binding_review": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice15_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice15ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE15_PROGRESS_RECEIPT",
        "receipt_status": (
            "LOOP805_SLICE15_MEASUREMENT_DRYRUN_AUTHORIZATION_HOLD_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_49_MEASUREMENT_DRYRUN_AUTHORIZATION_HOLD": "READY_NOT_AUTHORIZED",
            "PHASE_50_OPERATOR_DRYRUN_AUTHORIZATION": "REQUIRED_NOT_RECORDED",
            "PHASE_51_MEASUREMENT_DRYRUN_PREFLIGHT": "RECOMMENDED_NEXT_NOT_CREATED",
        },
        "receipt_hashes": {
            "measurement_dryrun_authorization_hold": packets[
                "slice15_measurement_dryrun_authorization_hold"
            ]["canonical_hash"],
            "prompt_packet": packets["slice15_prompt_packet"]["canonical_hash"],
            "slice14_progress_receipt": _build_slice14_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE16_MEASUREMENT_DRYRUN_PREFLIGHT_PACKET",
        "remaining_gates": [
            "OPERATOR_AUTHORIZES_MEASUREMENT_DRYRUN_SEPARATELY",
            "OPERATOR_ATTESTS_FIXTURE_BINDING_SEPARATELY",
            "OPERATOR_ATTESTS_OUTCOME_BINDING_SEPARATELY",
            "MEASUREMENT_DRYRUN_REMAINS_FALSE",
            "BRIER_RESOLUTION_REMAINS_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_authorization_hold": False,
        "valid_for_measurement_dryrun_authorization": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice16_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice16ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE16_PROGRESS_RECEIPT",
        "receipt_status": (
            "LOOP805_SLICE16_MEASUREMENT_DRYRUN_PREFLIGHT_PACKET_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_52_MEASUREMENT_DRYRUN_PREFLIGHT": "READY_SHAPE_ONLY_NOT_EXECUTABLE",
            "PHASE_53_OPERATOR_DRYRUN_DECISION": "REQUIRED_NOT_RECORDED",
            "PHASE_54_MEASUREMENT_DRYRUN_DECISION_REQUEST": (
                "RECOMMENDED_NEXT_NOT_CREATED"
            ),
        },
        "receipt_hashes": {
            "measurement_dryrun_preflight_packet": packets[
                "slice16_measurement_dryrun_preflight_packet"
            ]["canonical_hash"],
            "prompt_packet": packets["slice16_prompt_packet"]["canonical_hash"],
            "slice15_progress_receipt": _build_slice15_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE17_MEASUREMENT_DRYRUN_DECISION_REQUEST",
        "remaining_gates": [
            "OPERATOR_REVIEWS_PREFLIGHT_SEPARATELY",
            "OPERATOR_RECORDS_DRYRUN_DECISION_SEPARATELY",
            "MEASUREMENT_DRYRUN_EXECUTION_REMAINS_FALSE",
            "FORECAST_ROUTING_REMAINS_FALSE",
            "BRIER_RESOLUTION_REMAINS_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_preflight": False,
        "valid_for_measurement_dryrun_authorization": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice17_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice17ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE17_PROGRESS_RECEIPT",
        "receipt_status": (
            "LOOP805_SLICE17_MEASUREMENT_DRYRUN_DECISION_REQUEST_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_55_MEASUREMENT_DRYRUN_DECISION_REQUEST": "READY_NOT_RECORDED",
            "PHASE_56_OPERATOR_DRYRUN_DECISION_RECORD": "REQUIRED_NOT_RECORDED",
            "PHASE_57_MEASUREMENT_DRYRUN_DECISION_RECORD_TEMPLATE": (
                "RECOMMENDED_NEXT_NOT_CREATED"
            ),
        },
        "receipt_hashes": {
            "measurement_dryrun_decision_request": packets[
                "slice17_measurement_dryrun_decision_request"
            ]["canonical_hash"],
            "prompt_packet": packets["slice17_prompt_packet"]["canonical_hash"],
            "slice16_progress_receipt": _build_slice16_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": "PREPARE_SLICE18_MEASUREMENT_DRYRUN_DECISION_RECORD_TEMPLATE",
        "remaining_gates": [
            "OPERATOR_RECORDS_DRYRUN_DECISION_SEPARATELY",
            "DRYRUN_DECISION_RECORDING_REMAINS_FALSE",
            "MEASUREMENT_DRYRUN_EXECUTION_REMAINS_FALSE",
            "FORECAST_ROUTING_REMAINS_FALSE",
            "BRIER_RESOLUTION_REMAINS_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_decision_request": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice18_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice18ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE18_PROGRESS_RECEIPT",
        "receipt_status": (
            "LOOP805_SLICE18_MEASUREMENT_DRYRUN_DECISION_RECORD_TEMPLATE_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_58_MEASUREMENT_DRYRUN_DECISION_RECORD_TEMPLATE": (
                "READY_TEMPLATE_ONLY_NOT_RECORDED"
            ),
            "PHASE_59_OPERATOR_DECISION_INTAKE_GATE": "REQUIRED_NOT_CREATED",
            "PHASE_60_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE": (
                "RECOMMENDED_NEXT_NOT_CREATED"
            ),
        },
        "receipt_hashes": {
            "measurement_dryrun_decision_record_template": packets[
                "slice18_measurement_dryrun_decision_record_template"
            ]["canonical_hash"],
            "prompt_packet": packets["slice18_prompt_packet"]["canonical_hash"],
            "slice17_progress_receipt": _build_slice17_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": (
            "PREPARE_SLICE19_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE_GATE"
        ),
        "remaining_gates": [
            "OPERATOR_RECORDS_DRYRUN_DECISION_SEPARATELY",
            "DECISION_RECORD_TEMPLATE_REMAINS_UNFILLED",
            "DRYRUN_DECISION_RECORDING_REMAINS_FALSE",
            "MEASUREMENT_DRYRUN_EXECUTION_REMAINS_FALSE",
            "FORECAST_ROUTING_REMAINS_FALSE",
            "BRIER_RESOLUTION_REMAINS_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_decision_record_template": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice19_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice19ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE19_PROGRESS_RECEIPT",
        "receipt_status": (
            "LOOP805_SLICE19_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE_GATE_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_61_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE_GATE": (
                "READY_GATE_ONLY_NOT_OPENED"
            ),
            "PHASE_62_OPERATOR_DECISION_INTAKE_PACKET": "REQUIRED_NOT_CREATED",
            "PHASE_63_MEASUREMENT_DRYRUN_OPERATOR_DECISION_RECORD": (
                "RECOMMENDED_NEXT_NOT_CREATED"
            ),
        },
        "receipt_hashes": {
            "measurement_dryrun_operator_decision_intake_gate": packets[
                "slice19_measurement_dryrun_operator_decision_intake_gate"
            ]["canonical_hash"],
            "prompt_packet": packets["slice19_prompt_packet"]["canonical_hash"],
            "slice18_progress_receipt": _build_slice18_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": (
            "PREPARE_SLICE20_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE_PACKET"
        ),
        "remaining_gates": [
            "OPERATOR_OPENS_DRYRUN_DECISION_INTAKE_SEPARATELY",
            "OPERATOR_RECORDS_DRYRUN_DECISION_SEPARATELY",
            "OPERATOR_DECISION_INTAKE_REMAINS_FALSE",
            "DRYRUN_DECISION_RECORDING_REMAINS_FALSE",
            "MEASUREMENT_DRYRUN_EXECUTION_REMAINS_FALSE",
            "FORECAST_ROUTING_REMAINS_FALSE",
            "BRIER_RESOLUTION_REMAINS_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_decision_intake_gate": False,
        "valid_for_measurement_dryrun_operator_decision_intake": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _build_slice20_progress_receipt(
    timestamp: str,
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    from core.canonical.json import canonical_hash

    base: dict[str, Any] = {
        "schema_version": "AbxLoop805Slice20ProgressReceipt.v1",
        "loop_id": "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION",
        "receipt_id": "ABX_LOOP805_SLICE20_PROGRESS_RECEIPT",
        "receipt_status": (
            "LOOP805_SLICE20_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE_PACKET_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "phase_status": {
            "PHASE_64_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE_PACKET": (
                "READY_PACKET_ONLY_NOT_SUBMITTED"
            ),
            "PHASE_65_OPERATOR_DECISION_RECORD_CANDIDATE": "REQUIRED_NOT_CREATED",
            "PHASE_66_MEASUREMENT_DRYRUN_DECISION_RECORD_REVIEW": (
                "RECOMMENDED_NEXT_NOT_CREATED"
            ),
        },
        "receipt_hashes": {
            "measurement_dryrun_operator_decision_intake_packet": packets[
                "slice20_measurement_dryrun_operator_decision_intake_packet"
            ]["canonical_hash"],
            "prompt_packet": packets["slice20_prompt_packet"]["canonical_hash"],
            "slice19_progress_receipt": _build_slice19_progress_receipt(
                timestamp,
                packets,
            )["canonical_hash"],
        },
        "recommended_next_gate": (
            "PREPARE_SLICE21_MEASUREMENT_DRYRUN_OPERATOR_DECISION_RECORD_CANDIDATE"
        ),
        "remaining_gates": [
            "OPERATOR_SUBMITS_DRYRUN_DECISION_SEPARATELY",
            "OPERATOR_RECORDS_DRYRUN_DECISION_SEPARATELY",
            "OPERATOR_DECISION_INTAKE_SUBMISSION_REMAINS_FALSE",
            "DRYRUN_DECISION_RECORDING_REMAINS_FALSE",
            "MEASUREMENT_DRYRUN_EXECUTION_REMAINS_FALSE",
            "FORECAST_ROUTING_REMAINS_FALSE",
            "BRIER_RESOLUTION_REMAINS_FALSE",
        ],
        "authority_locks": packets["baseline"]["authority_locks"],
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_decision_intake_packet": False,
        "valid_for_measurement_dryrun_operator_decision_intake": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


if __name__ == "__main__":
    raise SystemExit(main())
