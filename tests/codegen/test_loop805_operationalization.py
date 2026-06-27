from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash
from core.codegen.loop805_activation_proposal import (
    build_loop805_gate_selection_matrix,
    build_loop805_activation_proposal,
    build_loop805_slice3_prompt_packet,
    build_loop805_slice4_prompt_packet,
)
from core.codegen.loop805_brier_attestation import (
    build_loop805_authorization_evidence_packet,
    build_loop805_brier_attestation_packet,
    build_loop805_brier_scoring_shadow_run,
    build_loop805_brier_shadow_resolution_review,
    build_loop805_fixture_binding_dryrun,
    build_loop805_fixture_outcome_binding_review,
    build_loop805_held_out_set_binding_review,
    build_loop805_held_out_set_attestation_gate,
    build_loop805_held_out_set_lockfile_proposal,
    build_loop805_measurement_authorization_proposal,
    build_loop805_measurement_dryrun_authorization_hold,
    build_loop805_measurement_dryrun_decision_record_review,
    build_loop805_measurement_dryrun_decision_record_template,
    build_loop805_measurement_dryrun_decision_request,
    build_loop805_measurement_dryrun_operator_decision_record_candidate,
    build_loop805_measurement_dryrun_operator_decision_intake_packet,
    build_loop805_measurement_dryrun_operator_decision_intake_gate,
    build_loop805_measurement_dryrun_execution_proposal_stub,
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
    build_loop805_slice21_prompt_packet,
    build_loop805_slice22_prompt_packet,
    build_loop805_slice23_prompt_packet,
    build_loop805_slice24_prompt_packet,
    build_loop805_slice25_prompt_packet,
)
from core.codegen.loop805_controller import build_loop805_controller_plan
from core.codegen.loop805_mcp_stub import (
    build_loop805_mcp_exposure_stub,
    default_loop805_mcp_tool_contracts,
)
from core.codegen.loop805_observability import (
    TARGET_TOKENS_PER_TURN,
    build_held_out_brier_fixture,
    build_held_out_brier_telemetry,
    build_loop805_daily_dashboard,
    build_loop805_regression_pr_proposal,
    build_spine_route_decision,
)
from core.codegen.loop805_operationalization import build_loop805_baseline_receipt
from core.codegen.loop805_token_optimizer import build_loop805_token_optimizer_stub
from core.codegen.spine_mcp_projection import (
    build_spine_audit_projection,
    build_spine_forecast_projection,
    build_spine_query_projection,
)


TIMESTAMP = "2026-06-21T23:05:00Z"
MERGE_SHA = "8eeb7f4df62feae25651645b589698a503fb40e6"


def _assert_canonical_hash(packet: dict) -> None:  # type: ignore[type-arg]
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("canonical_hash")
    assert packet_hash == canonical_hash(packet_without_hash)


def _assert_authority_locks(packet: dict) -> None:  # type: ignore[type-arg]
    locks = packet["authority_locks"]
    assert locks["advisory_only"] is True
    for name, value in locks.items():
        if name != "advisory_only":
            assert value is False, name


def test_loop805_baseline_receipt_is_advisory_and_hash_stable() -> None:
    packet = build_loop805_baseline_receipt(
        timestamp=TIMESTAMP,
        main_merge_sha=MERGE_SHA,
        source_receipts=["out/audit/example.latest.json"],
        validation_summary={"pyright": {"status": "TARGETED_PASS"}},
    )

    assert packet["loop_id"] == "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION"
    assert packet["spine_status"] == "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_COMPUTABLE"
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_live_mcp_exposure"] is False
    assert packet["success_criteria"][0]["metric"] == "held_out_forecast_brier_uplift"
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_loop805_controller_is_plan_only() -> None:
    packet = build_loop805_controller_plan(
        timestamp=TIMESTAMP,
        task="Run 24h forecast accuracy stress test on 2026 midterms signal set",
        measurements=[{"metric": "tokens", "value": 596311}],
    )

    assert [step["step"] for step in packet["cycle"]] == [
        "PLAN",
        "EXECUTE",
        "MEASURE",
        "ADJUST",
    ]
    assert packet["auto_pr_generation"]["authorized"] is False
    assert packet["quality_gates"]["max_tokens_per_full_loop"] == 420_000
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_spine_mcp_projections_are_not_live_tools() -> None:
    packets = [
        build_spine_query_projection(timestamp=TIMESTAMP, query="status"),
        build_spine_forecast_projection(
            timestamp=TIMESTAMP,
            forecast_question="token reduction",
            probability=0.62,
        ),
        build_spine_audit_projection(timestamp=TIMESTAMP, surface="README.md"),
    ]

    assert [packet["tool_name"] for packet in packets] == [
        "/spine/query",
        "/spine/forecast",
        "/spine/audit",
    ]
    for packet in packets:
        assert packet["projection_status"] == "MCP_TOOL_PROJECTION_READY_NOT_EXPOSED"
        assert packet["valid_for_live_mcp_exposure"] is False
        assert packet["valid_for_execution"] is False
        _assert_authority_locks(packet)
        _assert_canonical_hash(packet)


def test_spine_route_decision_records_token_delta_without_invocation() -> None:
    packet = build_spine_route_decision(
        timestamp=TIMESTAMP,
        tool_name="/spine/query",
        intent="Inspect advisory spine status",
        evidence_paths=["README.md", "PLANS.md"],
        estimated_input_tokens=25_000,
        estimated_output_tokens=10_000,
    )

    assert packet["decision_status"] == "ROUTE_PROJECTED_NOT_INVOKED"
    assert packet["valid_for_live_mcp_exposure"] is False
    assert packet["token_telemetry"]["estimated_total_tokens"] == 35_000
    assert packet["token_telemetry"]["estimated_reduction_target_met"] is True
    assert TARGET_TOKENS_PER_TURN == 488_975
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_loop805_daily_dashboard_is_observable_but_not_executing() -> None:
    route = build_spine_route_decision(
        timestamp=TIMESTAMP,
        tool_name="/spine/forecast",
        intent="Forecast token reduction",
        evidence_paths=["out/audit/example.latest.json"],
        estimated_input_tokens=50_000,
        estimated_output_tokens=15_000,
    )
    dashboard = build_loop805_daily_dashboard(
        timestamp=TIMESTAMP,
        route_decisions=[route],
        pyright_errors=0,
        ruff_errors=0,
        held_out_forecast_brier_baseline=0.25,
        held_out_forecast_brier_observed=0.1,
    )

    assert dashboard["dashboard_status"] == "OBSERVABILITY_DASHBOARD_READY_ADVISORY_ONLY"
    assert dashboard["route_decision_count"] == 1
    assert dashboard["token_target_met"] is True
    assert dashboard["quality_gates"]["pyright_zero"] is True
    assert dashboard["quality_gates"]["ruff_zero"] is True
    assert dashboard["forecast_brier"]["uplift_target_met"] is True
    assert dashboard["valid_for_execution"] is False
    _assert_authority_locks(dashboard)
    _assert_canonical_hash(dashboard)


def test_loop805_regression_pr_proposal_denies_writeback() -> None:
    route = build_spine_route_decision(
        timestamp=TIMESTAMP,
        tool_name="/spine/audit",
        intent="Audit Loop 805 receipts",
        evidence_paths=["out/audit/example.latest.json"],
        estimated_input_tokens=10_000,
        estimated_output_tokens=5_000,
    )
    dashboard = build_loop805_daily_dashboard(
        timestamp=TIMESTAMP,
        route_decisions=[route],
        pyright_errors=1,
        ruff_errors=0,
        held_out_forecast_brier_baseline=None,
        held_out_forecast_brier_observed=None,
    )
    proposal = build_loop805_regression_pr_proposal(
        timestamp=TIMESTAMP,
        dashboard=dashboard,
        regression_summary="Pyright regression requires operator review.",
        recommended_branch="loop-805-regression-repair-proposal",
        diff_preview=["core/codegen/example.py"],
    )

    assert proposal["proposal_status"] == "PROPOSAL_ONLY_OPERATOR_GATE_REQUIRED"
    assert proposal["auto_pr_generation"]["authorized"] is False
    assert proposal["valid_for_github_writeback"] is False
    assert proposal["dashboard_hash"] == dashboard["canonical_hash"]
    assert proposal["diff_preview"] == ["core/codegen/example.py"]
    assert "I approve" in proposal["operator_approval_template"]
    _assert_authority_locks(proposal)
    _assert_canonical_hash(proposal)


def test_loop805_mcp_exposure_stub_is_read_only_and_not_live() -> None:
    packet = build_loop805_mcp_exposure_stub(
        timestamp=TIMESTAMP,
        tool_contracts=default_loop805_mcp_tool_contracts(),
    )

    assert packet["stub_status"] == "MCP_EXPOSURE_STUB_READY_READ_ONLY_NOT_LIVE"
    assert len(packet["tool_contracts"]) == 3
    assert packet["valid_for_live_mcp_exposure"] is False
    for contract in packet["tool_contracts"]:
        assert contract["mode"] == "READ_ONLY_STUB"
        assert contract["live_exposure"] is False
        assert contract["valid_for_execution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_held_out_brier_fixture_and_telemetry_are_static_only() -> None:
    baseline = build_held_out_brier_fixture(
        timestamp=TIMESTAMP,
        fixture_id="baseline",
        forecast_rows=[
            {"forecast_id": "a", "probability": 0.5, "outcome": 1},
            {"forecast_id": "b", "probability": 0.5, "outcome": 0},
        ],
    )
    observed = build_held_out_brier_fixture(
        timestamp=TIMESTAMP,
        fixture_id="observed",
        forecast_rows=[
            {"forecast_id": "a", "probability": 0.8, "outcome": 1},
            {"forecast_id": "b", "probability": 0.2, "outcome": 0},
        ],
    )
    telemetry = build_held_out_brier_telemetry(
        timestamp=TIMESTAMP,
        baseline_fixture=baseline,
        observed_fixture=observed,
    )

    assert baseline["mean_brier_score"] == 0.25
    assert observed["mean_brier_score"] == 0.04
    assert telemetry["target_met"] is True
    assert telemetry["valid_for_brier_resolution"] is False
    assert telemetry["valid_for_forecast_routing"] is False
    _assert_authority_locks(baseline)
    _assert_authority_locks(observed)
    _assert_authority_locks(telemetry)
    _assert_canonical_hash(baseline)
    _assert_canonical_hash(observed)
    _assert_canonical_hash(telemetry)


def test_token_optimizer_stub_is_advisory_math_only() -> None:
    route = build_spine_route_decision(
        timestamp=TIMESTAMP,
        tool_name="/spine/query",
        intent="Inspect advisory spine status",
        evidence_paths=["README.md"],
        estimated_input_tokens=20_000,
        estimated_output_tokens=10_000,
    )
    packet = build_loop805_token_optimizer_stub(
        timestamp=TIMESTAMP,
        route_decisions=[route],
        optimizer_names=["token-optimizer", "ccusage", "caveman", "squeez"],
    )

    assert packet["stub_status"] == "TOKEN_OPTIMIZER_STUB_READY_NOT_ENFORCED"
    assert packet["target_met"] is True
    assert packet["enforcement"]["enabled"] is False
    assert packet["valid_for_ci_enforcement"] is False
    assert packet["valid_for_token_rewrite"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice3_activation_proposal_keeps_all_gates_locked() -> None:
    packet = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={
            "mcp_exposure_stub": "hash-a",
            "held_out_brier_telemetry": "hash-b",
            "token_optimizer_stub": "hash-c",
        },
    )

    assert (
        packet["proposal_status"]
        == "SLICE3_FULL_ACTIVATION_PROPOSAL_READY_OPERATOR_GATE_REQUIRED"
    )
    assert len(packet["activation_gates"]) == 4
    assert packet["operator_gate"]["exact_confirmation"] == "yes"
    assert packet["valid_for_live_mcp_exposure"] is False
    assert packet["valid_for_brier_resolution"] is False
    assert packet["valid_for_ci_enforcement"] is False
    assert packet["valid_for_github_writeback"] is False
    for gate in packet["activation_gates"]:
        assert gate["activation_authorized"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice3_prompt_packet_is_ready_to_paste_but_not_executable() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    packet = build_loop805_slice3_prompt_packet(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )

    assert packet["packet_status"] == "SLICE3_PROMPT_READY_ADVISORY_ONLY"
    assert "BOUNDARY" in packet["prompt"]
    assert "TASK" in packet["prompt"]
    assert packet["activation_proposal_hash"] == proposal["canonical_hash"]
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_live_mcp_exposure"] is False
    assert packet["valid_for_github_writeback"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice4_gate_selection_matrix_ranks_brier_first_without_authorizing() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )

    assert matrix["matrix_status"] == "SLICE4_GATE_SELECTION_READY_ADVISORY_ONLY"
    assert matrix["activation_proposal_hash"] == proposal["canonical_hash"]
    assert matrix["selected_gate"] is None
    assert matrix["selection_authorized"] is False
    assert matrix["ranked_gates"][0]["gate_id"] == (
        "GATE_2_HELD_OUT_BRIER_BOUNDING_REVIEW"
    )
    assert matrix["ranked_gates"][-1]["gate_id"] == "GATE_4_SELF_PR_WRITEBACK_REVIEW"
    for gate in matrix["ranked_gates"]:
        assert gate["activation_authorized"] is False
    _assert_authority_locks(matrix)
    _assert_canonical_hash(matrix)


def test_slice4_prompt_packet_selects_nothing_and_executes_nothing() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    packet = build_loop805_slice4_prompt_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )

    assert packet["packet_status"] == "SLICE4_GATE_SELECTION_PROMPT_READY_ADVISORY_ONLY"
    assert "Selecting a gate does not activate that gate" in packet["prompt"]
    assert packet["gate_selection_matrix_hash"] == matrix["canonical_hash"]
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_runtime_activation"] is False
    assert packet["valid_for_live_mcp_exposure"] is False
    assert packet["valid_for_github_writeback"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice5_brier_attestation_packet_does_not_resolve_brier() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    packet = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )

    assert (
        packet["packet_status"]
        == "SLICE5_HELD_OUT_BRIER_ATTESTATION_READY_ADVISORY_ONLY"
    )
    assert packet["target_gate"] == "GATE_2_HELD_OUT_BRIER_BOUNDING_REVIEW"
    assert packet["operator_attestation"]["attestation_recorded"] is False
    assert packet["scoring_authority"]["fixture_binding_allowed"] is False
    assert packet["scoring_authority"]["outcome_binding_allowed"] is False
    assert packet["scoring_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_brier_resolution"] is False
    for requirement in packet["held_out_set_requirements"]:
        assert requirement["satisfied"] is False
        assert requirement["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice5_prompt_packet_is_attestation_only() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    packet = build_loop805_slice5_prompt_packet(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
    )

    assert packet["packet_status"] == "SLICE5_PROMPT_READY_ADVISORY_ONLY"
    assert "does not bind outcomes or resolve Brier scores" in packet["prompt"]
    assert packet["brier_attestation_packet_hash"] == attestation["canonical_hash"]
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    assert packet["valid_for_github_writeback"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice6_fixture_binding_dryrun_validates_shape_without_binding() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    packet = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will dry-run shape stay advisory?",
                "probability": 0.61,
                "provenance": "test",
            }
        ],
    )

    assert (
        packet["dryrun_status"]
        == "SLICE6_FIXTURE_BINDING_DRYRUN_READY_ADVISORY_ONLY"
    )
    assert packet["fixture_row_count"] == 1
    assert packet["fixture_rows"][0]["outcome"] is None
    assert packet["binding_authority"]["fixture_binding_allowed"] is False
    assert packet["binding_authority"]["outcome_binding_allowed"] is False
    assert packet["binding_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_fixture_binding"] is False
    assert packet["valid_for_outcome_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice6_prompt_packet_is_dryrun_only() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will dry-run shape stay advisory?",
                "probability": 0.61,
                "provenance": "test",
            }
        ],
    )
    packet = build_loop805_slice6_prompt_packet(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
    )

    assert packet["packet_status"] == "SLICE6_PROMPT_READY_ADVISORY_ONLY"
    assert "does not bind fixtures" in packet["prompt"]
    assert packet["fixture_binding_dryrun_hash"] == dryrun["canonical_hash"]
    assert packet["valid_for_fixture_binding"] is False
    assert packet["valid_for_outcome_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice7_brier_scoring_shadow_run_rehearses_without_resolution() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will shadow scoring stay advisory?",
                "probability": 0.75,
                "provenance": "test",
            },
            {
                "forecast_id": "shape-2",
                "question": "Will Brier resolution remain denied?",
                "probability": 0.25,
                "provenance": "test",
            },
        ],
    )
    packet = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1, "shape-2": 0},
    )

    assert (
        packet["shadow_run_status"]
        == "SLICE7_BRIER_SCORING_SHADOW_RUN_READY_ADVISORY_ONLY"
    )
    assert packet["shadow_row_count"] == 2
    assert packet["mean_shadow_brier_score"] == 0.0625
    assert packet["shadow_rows"][0]["shadow_brier_component"] == 0.0625
    assert packet["shadow_scoring_authority"]["fixture_binding_allowed"] is False
    assert packet["shadow_scoring_authority"]["outcome_binding_allowed"] is False
    assert packet["shadow_scoring_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_fixture_binding"] is False
    assert packet["valid_for_outcome_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice7_prompt_packet_is_shadow_rehearsal_only() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will shadow scoring stay advisory?",
                "probability": 0.75,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    packet = build_loop805_slice7_prompt_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
    )

    assert packet["packet_status"] == "SLICE7_PROMPT_READY_ADVISORY_ONLY"
    assert "does not resolve Brier" in packet["prompt"]
    assert packet["brier_scoring_shadow_run_hash"] == shadow_run["canonical_hash"]
    assert packet["valid_for_outcome_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice8_outcome_policy_review_does_not_bind_policy_or_outcomes() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will outcome policy remain advisory?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    packet = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )

    assert packet["packet_status"] == "SLICE8_OUTCOME_POLICY_REVIEW_READY_ADVISORY_ONLY"
    assert packet["policy_requirement_count"] == 1
    assert packet["policy_requirements"][0]["satisfied"] is False
    assert packet["policy_authority"]["outcome_policy_binding_allowed"] is False
    assert packet["policy_authority"]["outcome_binding_allowed"] is False
    assert packet["policy_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_outcome_policy_binding"] is False
    assert packet["valid_for_outcome_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice8_prompt_packet_is_policy_review_only() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will outcome policy remain advisory?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    packet = build_loop805_slice8_prompt_packet(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
    )

    assert packet["packet_status"] == "SLICE8_PROMPT_READY_ADVISORY_ONLY"
    assert "it binds nothing" in packet["prompt"]
    assert packet["outcome_policy_review_hash"] == review["canonical_hash"]
    assert packet["valid_for_outcome_policy_binding"] is False
    assert packet["valid_for_outcome_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice9_held_out_set_lockfile_proposal_does_not_lock_or_bind() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will lockfile remain proposal-only?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    packet = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )

    assert (
        packet["proposal_status"]
        == "SLICE9_HELD_OUT_SET_LOCKFILE_PROPOSAL_READY_ADVISORY_ONLY"
    )
    assert packet["held_out_set_id"] == "set-1"
    assert packet["forecast_count"] == 1
    assert packet["lockfile_authority"]["held_out_set_lock_allowed"] is False
    assert packet["lockfile_authority"]["fixture_binding_allowed"] is False
    assert packet["lockfile_authority"]["outcome_binding_allowed"] is False
    assert packet["lockfile_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_held_out_set_lock"] is False
    assert packet["valid_for_fixture_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice9_prompt_packet_is_lockfile_review_only() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will lockfile remain proposal-only?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    lockfile = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )
    packet = build_loop805_slice9_prompt_packet(
        timestamp=TIMESTAMP,
        held_out_set_lockfile_proposal=lockfile,
    )

    assert packet["packet_status"] == "SLICE9_PROMPT_READY_ADVISORY_ONLY"
    assert "it does not lock the set" in packet["prompt"]
    assert packet["held_out_set_lockfile_proposal_hash"] == lockfile["canonical_hash"]
    assert packet["valid_for_held_out_set_lock"] is False
    assert packet["valid_for_fixture_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice10_held_out_set_attestation_gate_does_not_attest_or_lock() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will attestation stay review-only?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    lockfile = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )
    packet = build_loop805_held_out_set_attestation_gate(
        timestamp=TIMESTAMP,
        held_out_set_lockfile_proposal=lockfile,
        attestation_requirements=[
            {
                "requirement_id": "LOCKFILE_REVIEW",
                "description": "Operator reviews proposed lockfile.",
            }
        ],
    )

    assert (
        packet["gate_status"]
        == "SLICE10_HELD_OUT_SET_ATTESTATION_GATE_READY_ADVISORY_ONLY"
    )
    assert packet["attestation_requirement_count"] == 1
    assert packet["attestation_requirements"][0]["satisfied"] is False
    assert packet["operator_gate"]["attestation_recorded"] is False
    assert packet["gate_authority"]["held_out_set_attestation_allowed"] is False
    assert packet["gate_authority"]["held_out_set_lock_allowed"] is False
    assert packet["gate_authority"]["fixture_binding_allowed"] is False
    assert packet["gate_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_held_out_set_attestation"] is False
    assert packet["valid_for_held_out_set_lock"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice10_prompt_packet_is_attestation_review_only() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will attestation stay review-only?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    lockfile = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )
    gate = build_loop805_held_out_set_attestation_gate(
        timestamp=TIMESTAMP,
        held_out_set_lockfile_proposal=lockfile,
        attestation_requirements=[
            {
                "requirement_id": "LOCKFILE_REVIEW",
                "description": "Operator reviews proposed lockfile.",
            }
        ],
    )
    packet = build_loop805_slice10_prompt_packet(
        timestamp=TIMESTAMP,
        held_out_set_attestation_gate=gate,
    )

    assert packet["packet_status"] == "SLICE10_PROMPT_READY_ADVISORY_ONLY"
    assert "it does not attest" in packet["prompt"]
    assert packet["held_out_set_attestation_gate_hash"] == gate["canonical_hash"]
    assert packet["valid_for_held_out_set_attestation"] is False
    assert packet["valid_for_held_out_set_lock"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice11_measurement_readiness_review_does_not_measure_or_resolve() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will measurement remain review-only?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    lockfile = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )
    gate = build_loop805_held_out_set_attestation_gate(
        timestamp=TIMESTAMP,
        held_out_set_lockfile_proposal=lockfile,
        attestation_requirements=[
            {
                "requirement_id": "LOCKFILE_REVIEW",
                "description": "Operator reviews proposed lockfile.",
            }
        ],
    )
    packet = build_loop805_measurement_readiness_review(
        timestamp=TIMESTAMP,
        held_out_set_attestation_gate=gate,
        readiness_checks=[
            {
                "check_id": "BRIER_RESOLUTION_AUTHORIZED",
                "description": "Operator separately authorizes resolution.",
            }
        ],
    )

    assert (
        packet["review_status"]
        == "SLICE11_MEASUREMENT_READINESS_REVIEW_READY_ADVISORY_ONLY"
    )
    assert packet["readiness_check_count"] == 1
    assert packet["readiness_checks"][0]["satisfied"] is False
    assert packet["measurement_authority"]["measurement_allowed"] is False
    assert packet["measurement_authority"]["outcome_binding_allowed"] is False
    assert packet["measurement_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_measurement"] is False
    assert packet["valid_for_outcome_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice11_prompt_packet_is_measurement_review_only() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will measurement remain review-only?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    lockfile = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )
    gate = build_loop805_held_out_set_attestation_gate(
        timestamp=TIMESTAMP,
        held_out_set_lockfile_proposal=lockfile,
        attestation_requirements=[
            {
                "requirement_id": "LOCKFILE_REVIEW",
                "description": "Operator reviews proposed lockfile.",
            }
        ],
    )
    readiness = build_loop805_measurement_readiness_review(
        timestamp=TIMESTAMP,
        held_out_set_attestation_gate=gate,
        readiness_checks=[
            {
                "check_id": "BRIER_RESOLUTION_AUTHORIZED",
                "description": "Operator separately authorizes resolution.",
            }
        ],
    )
    packet = build_loop805_slice11_prompt_packet(
        timestamp=TIMESTAMP,
        measurement_readiness_review=readiness,
    )

    assert packet["packet_status"] == "SLICE11_PROMPT_READY_ADVISORY_ONLY"
    assert "it does not measure or resolve Brier" in packet["prompt"]
    assert packet["measurement_readiness_review_hash"] == readiness["canonical_hash"]
    assert packet["valid_for_measurement"] is False
    assert packet["valid_for_outcome_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice12_measurement_authorization_proposal_does_not_authorize() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will authorization remain proposal-only?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    lockfile = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )
    gate = build_loop805_held_out_set_attestation_gate(
        timestamp=TIMESTAMP,
        held_out_set_lockfile_proposal=lockfile,
        attestation_requirements=[
            {
                "requirement_id": "LOCKFILE_REVIEW",
                "description": "Operator reviews proposed lockfile.",
            }
        ],
    )
    readiness = build_loop805_measurement_readiness_review(
        timestamp=TIMESTAMP,
        held_out_set_attestation_gate=gate,
        readiness_checks=[
            {
                "check_id": "MEASUREMENT_AUTHORIZATION_RECORDED",
                "description": "Operator separately authorizes measurement.",
            }
        ],
    )
    packet = build_loop805_measurement_authorization_proposal(
        timestamp=TIMESTAMP,
        measurement_readiness_review=readiness,
        authorization_items=[
            {
                "authorization_id": "MEASUREMENT_AUTHORIZATION_NOTE",
                "description": "Operator records authorization outside receipts.",
            }
        ],
    )

    assert (
        packet["proposal_status"]
        == "SLICE12_MEASUREMENT_AUTHORIZATION_PROPOSAL_READY_ADVISORY_ONLY"
    )
    assert packet["authorization_item_count"] == 1
    assert packet["authorization_items"][0]["requested"] is True
    assert packet["authorization_items"][0]["authorized"] is False
    assert packet["authorization_authority"]["measurement_authorization_allowed"] is False
    assert packet["authorization_authority"]["measurement_allowed"] is False
    assert packet["authorization_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_measurement_authorization"] is False
    assert packet["valid_for_measurement"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice12_prompt_packet_is_authorization_proposal_only() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will authorization remain proposal-only?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    lockfile = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )
    gate = build_loop805_held_out_set_attestation_gate(
        timestamp=TIMESTAMP,
        held_out_set_lockfile_proposal=lockfile,
        attestation_requirements=[
            {
                "requirement_id": "LOCKFILE_REVIEW",
                "description": "Operator reviews proposed lockfile.",
            }
        ],
    )
    readiness = build_loop805_measurement_readiness_review(
        timestamp=TIMESTAMP,
        held_out_set_attestation_gate=gate,
        readiness_checks=[
            {
                "check_id": "MEASUREMENT_AUTHORIZATION_RECORDED",
                "description": "Operator separately authorizes measurement.",
            }
        ],
    )
    authorization = build_loop805_measurement_authorization_proposal(
        timestamp=TIMESTAMP,
        measurement_readiness_review=readiness,
        authorization_items=[
            {
                "authorization_id": "MEASUREMENT_AUTHORIZATION_NOTE",
                "description": "Operator records authorization outside receipts.",
            }
        ],
    )
    packet = build_loop805_slice12_prompt_packet(
        timestamp=TIMESTAMP,
        measurement_authorization_proposal=authorization,
    )

    assert packet["packet_status"] == "SLICE12_PROMPT_READY_ADVISORY_ONLY"
    assert "it does not authorize measurement" in packet["prompt"]
    assert (
        packet["measurement_authorization_proposal_hash"]
        == authorization["canonical_hash"]
    )
    assert packet["valid_for_measurement_authorization"] is False
    assert packet["valid_for_measurement"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice13_authorization_evidence_packet_records_no_evidence() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will evidence remain unrecorded?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    lockfile = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )
    gate = build_loop805_held_out_set_attestation_gate(
        timestamp=TIMESTAMP,
        held_out_set_lockfile_proposal=lockfile,
        attestation_requirements=[
            {
                "requirement_id": "LOCKFILE_REVIEW",
                "description": "Operator reviews proposed lockfile.",
            }
        ],
    )
    readiness = build_loop805_measurement_readiness_review(
        timestamp=TIMESTAMP,
        held_out_set_attestation_gate=gate,
        readiness_checks=[
            {
                "check_id": "MEASUREMENT_AUTHORIZATION_RECORDED",
                "description": "Operator separately authorizes measurement.",
            }
        ],
    )
    authorization = build_loop805_measurement_authorization_proposal(
        timestamp=TIMESTAMP,
        measurement_readiness_review=readiness,
        authorization_items=[
            {
                "authorization_id": "MEASUREMENT_AUTHORIZATION_NOTE",
                "description": "Operator records authorization outside receipts.",
            }
        ],
    )
    packet = build_loop805_authorization_evidence_packet(
        timestamp=TIMESTAMP,
        measurement_authorization_proposal=authorization,
        evidence_items=[
            {
                "evidence_id": "MEASUREMENT_AUTHORIZATION_ATTESTATION_NOTE",
                "description": "External note authorizes measurement review.",
            }
        ],
    )

    assert (
        packet["packet_status"]
        == "SLICE13_AUTHORIZATION_EVIDENCE_PACKET_READY_ADVISORY_ONLY"
    )
    assert packet["evidence_item_count"] == 1
    assert packet["evidence_items"][0]["recorded"] is False
    assert packet["evidence_items"][0]["attested"] is False
    assert (
        packet["evidence_authority"]["authorization_evidence_recording_allowed"]
        is False
    )
    assert (
        packet["evidence_authority"]["operator_attestation_recording_allowed"]
        is False
    )
    assert packet["evidence_authority"]["measurement_allowed"] is False
    assert packet["valid_for_authorization_evidence_recording"] is False
    assert packet["valid_for_measurement_authorization"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice13_prompt_packet_is_evidence_shape_only() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will evidence remain unrecorded?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    lockfile = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )
    gate = build_loop805_held_out_set_attestation_gate(
        timestamp=TIMESTAMP,
        held_out_set_lockfile_proposal=lockfile,
        attestation_requirements=[
            {
                "requirement_id": "LOCKFILE_REVIEW",
                "description": "Operator reviews proposed lockfile.",
            }
        ],
    )
    readiness = build_loop805_measurement_readiness_review(
        timestamp=TIMESTAMP,
        held_out_set_attestation_gate=gate,
        readiness_checks=[
            {
                "check_id": "MEASUREMENT_AUTHORIZATION_RECORDED",
                "description": "Operator separately authorizes measurement.",
            }
        ],
    )
    authorization = build_loop805_measurement_authorization_proposal(
        timestamp=TIMESTAMP,
        measurement_readiness_review=readiness,
        authorization_items=[
            {
                "authorization_id": "MEASUREMENT_AUTHORIZATION_NOTE",
                "description": "Operator records authorization outside receipts.",
            }
        ],
    )
    evidence = build_loop805_authorization_evidence_packet(
        timestamp=TIMESTAMP,
        measurement_authorization_proposal=authorization,
        evidence_items=[
            {
                "evidence_id": "MEASUREMENT_AUTHORIZATION_ATTESTATION_NOTE",
                "description": "External note authorizes measurement review.",
            }
        ],
    )
    packet = build_loop805_slice13_prompt_packet(
        timestamp=TIMESTAMP,
        authorization_evidence_packet=evidence,
    )

    assert packet["packet_status"] == "SLICE13_PROMPT_READY_ADVISORY_ONLY"
    assert "it does not record evidence" in packet["prompt"]
    assert packet["authorization_evidence_packet_hash"] == evidence["canonical_hash"]
    assert packet["valid_for_authorization_evidence_recording"] is False
    assert packet["valid_for_measurement_authorization"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice14_fixture_outcome_binding_review_binds_nothing() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will binding remain review-only?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    lockfile = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )
    gate = build_loop805_held_out_set_attestation_gate(
        timestamp=TIMESTAMP,
        held_out_set_lockfile_proposal=lockfile,
        attestation_requirements=[
            {
                "requirement_id": "LOCKFILE_REVIEW",
                "description": "Operator reviews proposed lockfile.",
            }
        ],
    )
    readiness = build_loop805_measurement_readiness_review(
        timestamp=TIMESTAMP,
        held_out_set_attestation_gate=gate,
        readiness_checks=[
            {
                "check_id": "MEASUREMENT_AUTHORIZATION_RECORDED",
                "description": "Operator separately authorizes measurement.",
            }
        ],
    )
    authorization = build_loop805_measurement_authorization_proposal(
        timestamp=TIMESTAMP,
        measurement_readiness_review=readiness,
        authorization_items=[
            {
                "authorization_id": "MEASUREMENT_AUTHORIZATION_NOTE",
                "description": "Operator records authorization outside receipts.",
            }
        ],
    )
    evidence = build_loop805_authorization_evidence_packet(
        timestamp=TIMESTAMP,
        measurement_authorization_proposal=authorization,
        evidence_items=[
            {
                "evidence_id": "MEASUREMENT_AUTHORIZATION_ATTESTATION_NOTE",
                "description": "External note authorizes measurement review.",
            }
        ],
    )
    packet = build_loop805_fixture_outcome_binding_review(
        timestamp=TIMESTAMP,
        authorization_evidence_packet=evidence,
        binding_checks=[
            {
                "check_id": "FIXTURE_BINDING_RECORD_PRESENT",
                "description": "Operator provides fixture binding record.",
            }
        ],
    )

    assert (
        packet["review_status"]
        == "SLICE14_FIXTURE_OUTCOME_BINDING_REVIEW_READY_ADVISORY_ONLY"
    )
    assert packet["binding_check_count"] == 1
    assert packet["binding_checks"][0]["satisfied"] is False
    assert packet["binding_checks"][0]["fixture_bound"] is False
    assert packet["binding_checks"][0]["outcome_bound"] is False
    assert packet["binding_authority"]["fixture_binding_allowed"] is False
    assert packet["binding_authority"]["outcome_binding_allowed"] is False
    assert packet["binding_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_fixture_binding"] is False
    assert packet["valid_for_outcome_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice14_prompt_packet_is_binding_review_only() -> None:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will binding remain review-only?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    lockfile = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )
    gate = build_loop805_held_out_set_attestation_gate(
        timestamp=TIMESTAMP,
        held_out_set_lockfile_proposal=lockfile,
        attestation_requirements=[
            {
                "requirement_id": "LOCKFILE_REVIEW",
                "description": "Operator reviews proposed lockfile.",
            }
        ],
    )
    readiness = build_loop805_measurement_readiness_review(
        timestamp=TIMESTAMP,
        held_out_set_attestation_gate=gate,
        readiness_checks=[
            {
                "check_id": "MEASUREMENT_AUTHORIZATION_RECORDED",
                "description": "Operator separately authorizes measurement.",
            }
        ],
    )
    authorization = build_loop805_measurement_authorization_proposal(
        timestamp=TIMESTAMP,
        measurement_readiness_review=readiness,
        authorization_items=[
            {
                "authorization_id": "MEASUREMENT_AUTHORIZATION_NOTE",
                "description": "Operator records authorization outside receipts.",
            }
        ],
    )
    evidence = build_loop805_authorization_evidence_packet(
        timestamp=TIMESTAMP,
        measurement_authorization_proposal=authorization,
        evidence_items=[
            {
                "evidence_id": "MEASUREMENT_AUTHORIZATION_ATTESTATION_NOTE",
                "description": "External note authorizes measurement review.",
            }
        ],
    )
    binding_review = build_loop805_fixture_outcome_binding_review(
        timestamp=TIMESTAMP,
        authorization_evidence_packet=evidence,
        binding_checks=[
            {
                "check_id": "FIXTURE_BINDING_RECORD_PRESENT",
                "description": "Operator provides fixture binding record.",
            }
        ],
    )
    packet = build_loop805_slice14_prompt_packet(
        timestamp=TIMESTAMP,
        fixture_outcome_binding_review=binding_review,
    )

    assert packet["packet_status"] == "SLICE14_PROMPT_READY_ADVISORY_ONLY"
    assert "it binds nothing" in packet["prompt"]
    assert (
        packet["fixture_outcome_binding_review_hash"]
        == binding_review["canonical_hash"]
    )
    assert packet["valid_for_fixture_binding"] is False
    assert packet["valid_for_outcome_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def _build_slice14_binding_review_for_slice15_tests() -> dict[str, Any]:
    proposal = build_loop805_activation_proposal(
        timestamp=TIMESTAMP,
        slice2_receipt_hashes={"slice2_progress_receipt": "hash-d"},
    )
    matrix = build_loop805_gate_selection_matrix(
        timestamp=TIMESTAMP,
        activation_proposal=proposal,
    )
    attestation = build_loop805_brier_attestation_packet(
        timestamp=TIMESTAMP,
        gate_selection_matrix=matrix,
    )
    dryrun = build_loop805_fixture_binding_dryrun(
        timestamp=TIMESTAMP,
        brier_attestation_packet=attestation,
        fixture_rows=[
            {
                "forecast_id": "shape-1",
                "question": "Will dry-run authorization remain held?",
                "probability": 0.7,
                "provenance": "test",
            },
        ],
    )
    shadow_run = build_loop805_brier_scoring_shadow_run(
        timestamp=TIMESTAMP,
        fixture_binding_dryrun=dryrun,
        shadow_outcomes={"shape-1": 1},
    )
    review = build_loop805_outcome_policy_review_packet(
        timestamp=TIMESTAMP,
        brier_scoring_shadow_run=shadow_run,
        policy_requirements=[
            {
                "requirement_id": "OUTCOME_SOURCE_OF_TRUTH",
                "description": "Operator identifies source.",
            }
        ],
    )
    lockfile = build_loop805_held_out_set_lockfile_proposal(
        timestamp=TIMESTAMP,
        outcome_policy_review_packet=review,
        held_out_set_id="set-1",
        forecast_ids=["shape-1"],
    )
    gate = build_loop805_held_out_set_attestation_gate(
        timestamp=TIMESTAMP,
        held_out_set_lockfile_proposal=lockfile,
        attestation_requirements=[
            {
                "requirement_id": "LOCKFILE_REVIEW",
                "description": "Operator reviews proposed lockfile.",
            }
        ],
    )
    readiness = build_loop805_measurement_readiness_review(
        timestamp=TIMESTAMP,
        held_out_set_attestation_gate=gate,
        readiness_checks=[
            {
                "check_id": "MEASUREMENT_AUTHORIZATION_RECORDED",
                "description": "Operator separately authorizes measurement.",
            }
        ],
    )
    authorization = build_loop805_measurement_authorization_proposal(
        timestamp=TIMESTAMP,
        measurement_readiness_review=readiness,
        authorization_items=[
            {
                "authorization_id": "MEASUREMENT_AUTHORIZATION_NOTE",
                "description": "Operator records authorization outside receipts.",
            }
        ],
    )
    evidence = build_loop805_authorization_evidence_packet(
        timestamp=TIMESTAMP,
        measurement_authorization_proposal=authorization,
        evidence_items=[
            {
                "evidence_id": "MEASUREMENT_AUTHORIZATION_ATTESTATION_NOTE",
                "description": "External note authorizes measurement review.",
            }
        ],
    )
    return build_loop805_fixture_outcome_binding_review(
        timestamp=TIMESTAMP,
        authorization_evidence_packet=evidence,
        binding_checks=[
            {
                "check_id": "FIXTURE_BINDING_RECORD_PRESENT",
                "description": "Operator provides fixture binding record.",
            },
            {
                "check_id": "OUTCOME_BINDING_RECORD_PRESENT",
                "description": "Operator provides outcome binding record.",
            },
        ],
    )


def test_slice15_measurement_dryrun_authorization_hold_authorizes_nothing() -> None:
    binding_review = _build_slice14_binding_review_for_slice15_tests()
    packet = build_loop805_measurement_dryrun_authorization_hold(
        timestamp=TIMESTAMP,
        fixture_outcome_binding_review=binding_review,
        hold_checks=[
            {
                "check_id": "MEASUREMENT_DRYRUN_AUTHORIZATION_RECORDED",
                "description": "Operator records dry-run authorization separately.",
            }
        ],
    )

    assert (
        packet["hold_status"]
        == "SLICE15_MEASUREMENT_DRYRUN_AUTHORIZATION_HOLD_READY_ADVISORY_ONLY"
    )
    assert packet["hold_check_count"] == 1
    assert packet["hold_checks"][0]["satisfied"] is False
    assert packet["hold_checks"][0]["externally_attested"] is False
    assert packet["authorization_authority"]["measurement_allowed"] is False
    assert (
        packet["authorization_authority"][
            "measurement_dryrun_authorization_allowed"
        ]
        is False
    )
    assert packet["authorization_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_measurement_dryrun_authorization"] is False
    assert packet["valid_for_measurement"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice15_prompt_packet_is_authorization_hold_only() -> None:
    binding_review = _build_slice14_binding_review_for_slice15_tests()
    hold = build_loop805_measurement_dryrun_authorization_hold(
        timestamp=TIMESTAMP,
        fixture_outcome_binding_review=binding_review,
        hold_checks=[
            {
                "check_id": "MEASUREMENT_DRYRUN_AUTHORIZATION_RECORDED",
                "description": "Operator records dry-run authorization separately.",
            }
        ],
    )
    packet = build_loop805_slice15_prompt_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_authorization_hold=hold,
    )

    assert packet["packet_status"] == "SLICE15_PROMPT_READY_ADVISORY_ONLY"
    assert "it authorizes no dry-run measurement" in packet["prompt"]
    assert packet["measurement_dryrun_authorization_hold_hash"] == hold[
        "canonical_hash"
    ]
    assert packet["valid_for_measurement_dryrun_authorization"] is False
    assert packet["valid_for_measurement"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def _build_slice15_authorization_hold_for_slice16_tests() -> dict[str, Any]:
    binding_review = _build_slice14_binding_review_for_slice15_tests()
    return build_loop805_measurement_dryrun_authorization_hold(
        timestamp=TIMESTAMP,
        fixture_outcome_binding_review=binding_review,
        hold_checks=[
            {
                "check_id": "MEASUREMENT_DRYRUN_AUTHORIZATION_RECORDED",
                "description": "Operator records dry-run authorization separately.",
            },
            {
                "check_id": "FIXTURE_AND_OUTCOME_BINDINGS_ATTESTED",
                "description": "Operator attests fixture and outcome bindings separately.",
            },
        ],
    )


def test_slice16_measurement_dryrun_preflight_packet_executes_nothing() -> None:
    hold = _build_slice15_authorization_hold_for_slice16_tests()
    packet = build_loop805_measurement_dryrun_preflight_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_authorization_hold=hold,
        preflight_checks=[
            {
                "check_id": "SHADOW_RUN_OUTPUTS_QUARANTINED",
                "description": "Dry-run outputs cannot route forecasts.",
            }
        ],
    )

    assert (
        packet["preflight_status"]
        == "SLICE16_MEASUREMENT_DRYRUN_PREFLIGHT_PACKET_READY_ADVISORY_ONLY"
    )
    assert packet["preflight_check_count"] == 1
    assert packet["preflight_checks"][0]["satisfied"] is False
    assert packet["preflight_checks"][0]["executable"] is False
    assert packet["preflight_authority"]["measurement_execution_allowed"] is False
    assert packet["preflight_authority"]["forecast_routing_allowed"] is False
    assert packet["preflight_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_measurement_dryrun_preflight"] is False
    assert packet["valid_for_measurement"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice16_prompt_packet_is_preflight_shape_only() -> None:
    hold = _build_slice15_authorization_hold_for_slice16_tests()
    preflight = build_loop805_measurement_dryrun_preflight_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_authorization_hold=hold,
        preflight_checks=[
            {
                "check_id": "SHADOW_RUN_OUTPUTS_QUARANTINED",
                "description": "Dry-run outputs cannot route forecasts.",
            }
        ],
    )
    packet = build_loop805_slice16_prompt_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_preflight_packet=preflight,
    )

    assert packet["packet_status"] == "SLICE16_PROMPT_READY_ADVISORY_ONLY"
    assert "it cannot run measurement" in packet["prompt"]
    assert packet["measurement_dryrun_preflight_packet_hash"] == preflight[
        "canonical_hash"
    ]
    assert packet["valid_for_measurement_dryrun_preflight"] is False
    assert packet["valid_for_measurement"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def _build_slice16_preflight_for_slice17_tests() -> dict[str, Any]:
    hold = _build_slice15_authorization_hold_for_slice16_tests()
    return build_loop805_measurement_dryrun_preflight_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_authorization_hold=hold,
        preflight_checks=[
            {
                "check_id": "SHADOW_RUN_OUTPUTS_QUARANTINED",
                "description": "Dry-run outputs cannot route forecasts.",
            },
            {
                "check_id": "REVERSION_PATH_DOCUMENTED",
                "description": "Rollback path is documented outside this receipt.",
            },
        ],
    )


def test_slice17_measurement_dryrun_decision_request_records_no_decision() -> None:
    preflight = _build_slice16_preflight_for_slice17_tests()
    packet = build_loop805_measurement_dryrun_decision_request(
        timestamp=TIMESTAMP,
        measurement_dryrun_preflight_packet=preflight,
        decision_items=[
            {
                "decision_id": "DRYRUN_GO_NO_GO_DECISION",
                "description": "Operator records dry-run go/no-go separately.",
            }
        ],
    )

    assert (
        packet["request_status"]
        == "SLICE17_MEASUREMENT_DRYRUN_DECISION_REQUEST_READY_ADVISORY_ONLY"
    )
    assert packet["decision_item_count"] == 1
    assert packet["decision_items"][0]["requested"] is True
    assert packet["decision_items"][0]["decision_recorded"] is False
    assert packet["decision_items"][0]["operator_attested"] is False
    assert packet["decision_authority"]["measurement_dryrun_execution_allowed"] is False
    assert packet["decision_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_measurement_dryrun_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice17_prompt_packet_requests_decision_only() -> None:
    preflight = _build_slice16_preflight_for_slice17_tests()
    decision_request = build_loop805_measurement_dryrun_decision_request(
        timestamp=TIMESTAMP,
        measurement_dryrun_preflight_packet=preflight,
        decision_items=[
            {
                "decision_id": "DRYRUN_GO_NO_GO_DECISION",
                "description": "Operator records dry-run go/no-go separately.",
            }
        ],
    )
    packet = build_loop805_slice17_prompt_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_decision_request=decision_request,
    )

    assert packet["packet_status"] == "SLICE17_PROMPT_READY_ADVISORY_ONLY"
    assert "records no decision and executes nothing" in packet["prompt"]
    assert packet["measurement_dryrun_decision_request_hash"] == decision_request[
        "canonical_hash"
    ]
    assert packet["valid_for_measurement_dryrun_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def _build_slice17_decision_request_for_slice18_tests() -> dict[str, Any]:
    preflight = _build_slice16_preflight_for_slice17_tests()
    return build_loop805_measurement_dryrun_decision_request(
        timestamp=TIMESTAMP,
        measurement_dryrun_preflight_packet=preflight,
        decision_items=[
            {
                "decision_id": "DRYRUN_GO_NO_GO_DECISION",
                "description": "Operator dry-run go/no-go decision remains external.",
            }
        ],
    )


def test_slice18_measurement_dryrun_decision_record_template_records_no_decision() -> None:
    decision_request = _build_slice17_decision_request_for_slice18_tests()
    packet = build_loop805_measurement_dryrun_decision_record_template(
        timestamp=TIMESTAMP,
        measurement_dryrun_decision_request=decision_request,
        template_items=[
            {
                "field_id": "OPERATOR_DRYRUN_GO_NO_GO_DECISION",
                "description": "Unfilled operator go/no-go decision field.",
            }
        ],
    )

    assert (
        packet["template_status"]
        == "SLICE18_MEASUREMENT_DRYRUN_DECISION_RECORD_TEMPLATE_READY_ADVISORY_ONLY"
    )
    assert packet["template_item_count"] == 1
    assert packet["template_items"][0]["required"] is True
    assert packet["template_items"][0]["filled"] is False
    assert packet["template_items"][0]["decision_recorded"] is False
    assert packet["template_items"][0]["operator_attested"] is False
    assert packet["decision_record_state"]["decision_recorded"] is False
    assert packet["decision_record_state"]["measurement_dryrun_executable"] is False
    assert packet["valid_for_measurement_dryrun_decision_record_template"] is False
    assert packet["valid_for_measurement_dryrun_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice18_prompt_packet_is_template_only() -> None:
    decision_request = _build_slice17_decision_request_for_slice18_tests()
    template = build_loop805_measurement_dryrun_decision_record_template(
        timestamp=TIMESTAMP,
        measurement_dryrun_decision_request=decision_request,
        template_items=[
            {
                "field_id": "OPERATOR_DRYRUN_GO_NO_GO_DECISION",
                "description": "Unfilled operator go/no-go decision field.",
            }
        ],
    )
    packet = build_loop805_slice18_prompt_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_decision_record_template=template,
    )

    assert packet["packet_status"] == "SLICE18_PROMPT_READY_ADVISORY_ONLY"
    assert "records no decision and executes nothing" in packet["prompt"]
    assert "template is not an operator decision record" in packet["prompt"]
    assert (
        packet["measurement_dryrun_decision_record_template_hash"]
        == template["canonical_hash"]
    )
    assert packet["valid_for_measurement_dryrun_decision_record_template"] is False
    assert packet["valid_for_measurement_dryrun_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def _build_slice18_template_for_slice19_tests() -> dict[str, Any]:
    decision_request = _build_slice17_decision_request_for_slice18_tests()
    return build_loop805_measurement_dryrun_decision_record_template(
        timestamp=TIMESTAMP,
        measurement_dryrun_decision_request=decision_request,
        template_items=[
            {
                "field_id": "OPERATOR_DRYRUN_GO_NO_GO_DECISION",
                "description": "Unfilled operator go/no-go decision field.",
            }
        ],
    )


def test_slice19_operator_decision_intake_gate_opens_no_intake() -> None:
    template = _build_slice18_template_for_slice19_tests()
    packet = build_loop805_measurement_dryrun_operator_decision_intake_gate(
        timestamp=TIMESTAMP,
        measurement_dryrun_decision_record_template=template,
        intake_requirements=[
            {
                "requirement_id": "OPERATOR_INTAKE_CHANNEL_SELECTED",
                "description": "Operator intake channel remains external.",
            }
        ],
    )

    assert (
        packet["gate_status"]
        == "SLICE19_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE_GATE_READY_ADVISORY_ONLY"
    )
    assert packet["intake_requirement_count"] == 1
    assert packet["intake_requirements"][0]["required"] is True
    assert packet["intake_requirements"][0]["satisfied"] is False
    assert packet["intake_requirements"][0]["intake_opened"] is False
    assert packet["intake_requirements"][0]["decision_received"] is False
    assert packet["intake_requirements"][0]["decision_recorded"] is False
    assert packet["intake_state"]["operator_decision_intake_opened"] is False
    assert packet["intake_state"]["operator_decision_recorded"] is False
    assert packet["intake_state"]["measurement_dryrun_executable"] is False
    assert packet["valid_for_measurement_dryrun_operator_decision_intake_gate"] is False
    assert packet["valid_for_measurement_dryrun_operator_decision_intake"] is False
    assert packet["valid_for_measurement_dryrun_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice19_prompt_packet_is_intake_gate_only() -> None:
    template = _build_slice18_template_for_slice19_tests()
    intake_gate = build_loop805_measurement_dryrun_operator_decision_intake_gate(
        timestamp=TIMESTAMP,
        measurement_dryrun_decision_record_template=template,
        intake_requirements=[
            {
                "requirement_id": "OPERATOR_INTAKE_CHANNEL_SELECTED",
                "description": "Operator intake channel remains external.",
            }
        ],
    )
    packet = build_loop805_slice19_prompt_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_operator_decision_intake_gate=intake_gate,
    )

    assert packet["packet_status"] == "SLICE19_PROMPT_READY_ADVISORY_ONLY"
    assert "opens no intake, records no decision, and executes nothing" in packet[
        "prompt"
    ]
    assert "not a submitted decision" in packet["prompt"]
    assert (
        packet["measurement_dryrun_operator_decision_intake_gate_hash"]
        == intake_gate["canonical_hash"]
    )
    assert packet["valid_for_measurement_dryrun_operator_decision_intake_gate"] is False
    assert packet["valid_for_measurement_dryrun_operator_decision_intake"] is False
    assert packet["valid_for_measurement_dryrun_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def _build_slice19_intake_gate_for_slice20_tests() -> dict[str, Any]:
    template = _build_slice18_template_for_slice19_tests()
    return build_loop805_measurement_dryrun_operator_decision_intake_gate(
        timestamp=TIMESTAMP,
        measurement_dryrun_decision_record_template=template,
        intake_requirements=[
            {
                "requirement_id": "OPERATOR_INTAKE_CHANNEL_SELECTED",
                "description": "Operator intake channel remains external.",
            }
        ],
    )


def test_slice20_operator_decision_intake_packet_submits_no_decision() -> None:
    intake_gate = _build_slice19_intake_gate_for_slice20_tests()
    packet = build_loop805_measurement_dryrun_operator_decision_intake_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_operator_decision_intake_gate=intake_gate,
        intake_items=[
            {
                "item_id": "OPERATOR_GO_NO_GO_PLACEHOLDER",
                "description": "Unsubmitted future operator decision placeholder.",
            }
        ],
    )

    assert (
        packet["intake_packet_status"]
        == "SLICE20_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE_PACKET_READY_ADVISORY_ONLY"
    )
    assert packet["intake_item_count"] == 1
    assert packet["intake_items"][0]["required"] is True
    assert packet["intake_items"][0]["submitted"] is False
    assert packet["intake_items"][0]["decision_received"] is False
    assert packet["intake_items"][0]["decision_recorded"] is False
    assert packet["intake_packet_state"]["intake_submitted"] is False
    assert packet["intake_packet_state"]["decision_recorded"] is False
    assert packet["intake_packet_state"]["measurement_dryrun_executable"] is False
    assert packet["valid_for_measurement_dryrun_operator_decision_intake_packet"] is False
    assert packet["valid_for_measurement_dryrun_operator_decision_intake"] is False
    assert packet["valid_for_measurement_dryrun_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice20_prompt_packet_is_unsubmitted_intake_only() -> None:
    intake_gate = _build_slice19_intake_gate_for_slice20_tests()
    intake_packet = build_loop805_measurement_dryrun_operator_decision_intake_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_operator_decision_intake_gate=intake_gate,
        intake_items=[
            {
                "item_id": "OPERATOR_GO_NO_GO_PLACEHOLDER",
                "description": "Unsubmitted future operator decision placeholder.",
            }
        ],
    )
    packet = build_loop805_slice20_prompt_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_operator_decision_intake_packet=intake_packet,
    )

    assert packet["packet_status"] == "SLICE20_PROMPT_READY_ADVISORY_ONLY"
    assert "records no decision and executes nothing" in packet["prompt"]
    assert "not submitted, attested, recorded, or executable" in packet["prompt"]
    assert (
        packet["measurement_dryrun_operator_decision_intake_packet_hash"]
        == intake_packet["canonical_hash"]
    )
    assert packet["valid_for_measurement_dryrun_operator_decision_intake_packet"] is False
    assert packet["valid_for_measurement_dryrun_operator_decision_intake"] is False
    assert packet["valid_for_measurement_dryrun_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def _build_slice20_intake_packet_for_slice21_tests() -> dict[str, Any]:
    intake_gate = _build_slice19_intake_gate_for_slice20_tests()
    return build_loop805_measurement_dryrun_operator_decision_intake_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_operator_decision_intake_gate=intake_gate,
        intake_items=[
            {
                "item_id": "OPERATOR_GO_NO_GO_PLACEHOLDER",
                "description": "Unsubmitted future operator decision placeholder.",
            }
        ],
    )


def test_slice21_operator_decision_record_candidate_records_no_decision() -> None:
    intake_packet = _build_slice20_intake_packet_for_slice21_tests()
    packet = build_loop805_measurement_dryrun_operator_decision_record_candidate(
        timestamp=TIMESTAMP,
        measurement_dryrun_operator_decision_intake_packet=intake_packet,
        candidate_fields=[
            {
                "field_id": "CANDIDATE_GO_NO_GO_VALUE",
                "description": "Candidate-only go/no-go field.",
            }
        ],
    )

    assert (
        packet["candidate_status"]
        == "SLICE21_MEASUREMENT_DRYRUN_OPERATOR_DECISION_RECORD_CANDIDATE_READY_ADVISORY_ONLY"
    )
    assert packet["candidate_field_count"] == 1
    assert packet["candidate_fields"][0]["candidate_only"] is True
    assert packet["candidate_fields"][0]["filled"] is False
    assert packet["candidate_fields"][0]["decision_received"] is False
    assert packet["candidate_fields"][0]["decision_recorded"] is False
    assert packet["candidate_fields"][0]["operator_attested"] is False
    assert packet["candidate_state"]["decision_recorded"] is False
    assert packet["candidate_state"]["operator_attested"] is False
    assert packet["candidate_state"]["measurement_dryrun_executable"] is False
    assert (
        packet["valid_for_measurement_dryrun_operator_decision_record_candidate"]
        is False
    )
    assert packet["valid_for_measurement_dryrun_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice21_prompt_packet_is_candidate_only() -> None:
    intake_packet = _build_slice20_intake_packet_for_slice21_tests()
    candidate = build_loop805_measurement_dryrun_operator_decision_record_candidate(
        timestamp=TIMESTAMP,
        measurement_dryrun_operator_decision_intake_packet=intake_packet,
        candidate_fields=[
            {
                "field_id": "CANDIDATE_GO_NO_GO_VALUE",
                "description": "Candidate-only go/no-go field.",
            }
        ],
    )
    packet = build_loop805_slice21_prompt_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_operator_decision_record_candidate=candidate,
    )

    assert packet["packet_status"] == "SLICE21_PROMPT_READY_ADVISORY_ONLY"
    assert "records no decision and executes nothing" in packet["prompt"]
    assert "not a submitted decision" in packet["prompt"]
    assert (
        packet["measurement_dryrun_operator_decision_record_candidate_hash"]
        == candidate["canonical_hash"]
    )
    assert (
        packet["valid_for_measurement_dryrun_operator_decision_record_candidate"]
        is False
    )
    assert packet["valid_for_measurement_dryrun_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def _build_slice21_candidate_for_slice22_tests() -> dict[str, Any]:
    intake_packet = _build_slice20_intake_packet_for_slice21_tests()
    return build_loop805_measurement_dryrun_operator_decision_record_candidate(
        timestamp=TIMESTAMP,
        measurement_dryrun_operator_decision_intake_packet=intake_packet,
        candidate_fields=[
            {
                "field_id": "CANDIDATE_GO_NO_GO_VALUE",
                "description": "Candidate-only go/no-go field.",
            }
        ],
    )


def test_slice22_decision_record_review_records_no_decision() -> None:
    candidate = _build_slice21_candidate_for_slice22_tests()
    packet = build_loop805_measurement_dryrun_decision_record_review(
        timestamp=TIMESTAMP,
        measurement_dryrun_operator_decision_record_candidate=candidate,
        review_items=[
            {
                "review_id": "CANDIDATE_DIFF_PREVIEW_REVIEW",
                "description": "Review diff-preview stub without recording.",
            }
        ],
    )

    assert (
        packet["review_status"]
        == "SLICE22_MEASUREMENT_DRYRUN_DECISION_RECORD_REVIEW_READY_ADVISORY_ONLY"
    )
    assert packet["review_item_count"] == 1
    assert packet["review_items"][0]["required"] is True
    assert packet["review_items"][0]["satisfied"] is False
    assert packet["review_items"][0]["reviewed"] is False
    assert packet["review_items"][0]["decision_recorded"] is False
    assert packet["review_items"][0]["operator_attested"] is False
    assert packet["review_state"]["review_surface_prepared"] is True
    assert packet["review_state"]["candidate_reviewed"] is False
    assert packet["review_state"]["decision_recorded"] is False
    assert packet["review_state"]["operator_attested"] is False
    assert packet["review_state"]["measurement_dryrun_executable"] is False
    assert packet["diff_preview_stub"]["enabled"] is False
    assert packet["diff_preview_stub"]["preview_generated"] is False
    assert packet["diff_preview_stub"]["valid_for_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_decision_record_review"] is False
    assert packet["valid_for_measurement_dryrun_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_fixture_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice22_prompt_packet_is_review_only() -> None:
    candidate = _build_slice21_candidate_for_slice22_tests()
    review = build_loop805_measurement_dryrun_decision_record_review(
        timestamp=TIMESTAMP,
        measurement_dryrun_operator_decision_record_candidate=candidate,
        review_items=[
            {
                "review_id": "CANDIDATE_DIFF_PREVIEW_REVIEW",
                "description": "Review diff-preview stub without recording.",
            }
        ],
    )
    packet = build_loop805_slice22_prompt_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_decision_record_review=review,
    )

    assert packet["packet_status"] == "SLICE22_PROMPT_READY_ADVISORY_ONLY"
    assert "records no decision and executes nothing" in packet["prompt"]
    assert "held-out binding" in packet["prompt"]
    assert (
        packet["measurement_dryrun_decision_record_review_hash"]
        == review["canonical_hash"]
    )
    assert packet["valid_for_measurement_dryrun_decision_record_review"] is False
    assert packet["valid_for_measurement_dryrun_decision_recording"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def _build_slice22_review_for_slice23_tests() -> dict[str, Any]:
    candidate = _build_slice21_candidate_for_slice22_tests()
    return build_loop805_measurement_dryrun_decision_record_review(
        timestamp=TIMESTAMP,
        measurement_dryrun_operator_decision_record_candidate=candidate,
        review_items=[
            {
                "review_id": "CANDIDATE_DIFF_PREVIEW_REVIEW",
                "description": "Review diff-preview stub without recording.",
            }
        ],
    )


def test_slice23_held_out_set_binding_review_binds_nothing() -> None:
    review = _build_slice22_review_for_slice23_tests()
    observability = build_loop805_daily_dashboard(
        timestamp=TIMESTAMP,
        route_decisions=[],
        pyright_errors=0,
        ruff_errors=0,
        held_out_forecast_brier_baseline=None,
        held_out_forecast_brier_observed=None,
    )
    packet = build_loop805_held_out_set_binding_review(
        timestamp=TIMESTAMP,
        measurement_dryrun_decision_record_review=review,
        observability_dashboard=observability,
        binding_checks=[
            {
                "check_id": "FIXTURE_BINDING_SHAPE_REVIEW",
                "description": "Review fixture shape without binding fixtures.",
            }
        ],
    )

    assert (
        packet["review_status"]
        == "SLICE23_HELD_OUT_SET_BINDING_REVIEW_READY_ADVISORY_ONLY"
    )
    assert packet["binding_check_count"] == 1
    assert packet["binding_checks"][0]["required"] is True
    assert packet["binding_checks"][0]["satisfied"] is False
    assert packet["binding_checks"][0]["reviewed"] is False
    assert packet["binding_checks"][0]["binding_hook_prepared"] is True
    assert packet["binding_checks"][0]["held_out_set_bound"] is False
    assert packet["binding_checks"][0]["fixture_bound"] is False
    assert packet["binding_checks"][0]["outcome_bound"] is False
    assert packet["observability_dashboard_hash"] == observability["canonical_hash"]
    assert packet["observability_integration"]["telemetry_reviewed"] is False
    assert packet["observability_integration"]["binding_validation_hooks_prepared"] is True
    assert packet["observability_integration"]["fixtures_bound"] is False
    assert packet["observability_integration"]["outcomes_bound"] is False
    assert packet["observability_integration"]["brier_resolution_prepared"] is False
    assert packet["binding_authority"]["held_out_set_binding_allowed"] is False
    assert packet["binding_authority"]["fixture_binding_allowed"] is False
    assert packet["binding_authority"]["outcome_binding_allowed"] is False
    assert packet["binding_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_held_out_set_binding_review"] is False
    assert packet["valid_for_held_out_set_binding"] is False
    assert packet["valid_for_fixture_binding"] is False
    assert packet["valid_for_outcome_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice23_prompt_packet_is_binding_review_only() -> None:
    review = _build_slice22_review_for_slice23_tests()
    observability = build_loop805_daily_dashboard(
        timestamp=TIMESTAMP,
        route_decisions=[],
        pyright_errors=0,
        ruff_errors=0,
        held_out_forecast_brier_baseline=None,
        held_out_forecast_brier_observed=None,
    )
    binding_review = build_loop805_held_out_set_binding_review(
        timestamp=TIMESTAMP,
        measurement_dryrun_decision_record_review=review,
        observability_dashboard=observability,
        binding_checks=[
            {
                "check_id": "FIXTURE_BINDING_SHAPE_REVIEW",
                "description": "Review fixture shape without binding fixtures.",
            }
        ],
    )
    packet = build_loop805_slice23_prompt_packet(
        timestamp=TIMESTAMP,
        held_out_set_binding_review=binding_review,
    )

    assert packet["packet_status"] == "SLICE23_PROMPT_READY_ADVISORY_ONLY"
    assert "binds no held-out sets" in packet["prompt"]
    assert "Brier shadow resolution" in packet["prompt"]
    assert (
        packet["held_out_set_binding_review_hash"]
        == binding_review["canonical_hash"]
    )
    assert packet["valid_for_held_out_set_binding_review"] is False
    assert packet["valid_for_held_out_set_binding"] is False
    assert packet["valid_for_fixture_binding"] is False
    assert packet["valid_for_outcome_binding"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def _build_slice23_binding_review_for_slice24_tests() -> dict[str, Any]:
    review = _build_slice22_review_for_slice23_tests()
    observability = build_loop805_daily_dashboard(
        timestamp=TIMESTAMP,
        route_decisions=[],
        pyright_errors=0,
        ruff_errors=0,
        held_out_forecast_brier_baseline=None,
        held_out_forecast_brier_observed=None,
    )
    return build_loop805_held_out_set_binding_review(
        timestamp=TIMESTAMP,
        measurement_dryrun_decision_record_review=review,
        observability_dashboard=observability,
        binding_checks=[
            {
                "check_id": "FIXTURE_BINDING_SHAPE_REVIEW",
                "description": "Review fixture shape without binding fixtures.",
            }
        ],
    )


def test_slice24_brier_shadow_resolution_review_resolves_nothing() -> None:
    binding_review = _build_slice23_binding_review_for_slice24_tests()
    packet = build_loop805_brier_shadow_resolution_review(
        timestamp=TIMESTAMP,
        held_out_set_binding_review=binding_review,
        resolution_checks=[
            {
                "check_id": "SHADOW_RESOLUTION_INPUT_REVIEW",
                "description": "Review inputs without resolving Brier.",
            }
        ],
    )

    assert (
        packet["review_status"]
        == "SLICE24_BRIER_SHADOW_RESOLUTION_REVIEW_READY_ADVISORY_ONLY"
    )
    assert packet["resolution_check_count"] == 1
    assert packet["resolution_checks"][0]["required"] is True
    assert packet["resolution_checks"][0]["satisfied"] is False
    assert packet["resolution_checks"][0]["reviewed"] is False
    assert packet["resolution_checks"][0]["shadow_resolution_computed"] is False
    assert packet["resolution_checks"][0]["live_resolution_computed"] is False
    assert packet["shadow_resolution_state"]["review_surface_prepared"] is True
    assert packet["shadow_resolution_state"]["held_out_set_bound"] is False
    assert packet["shadow_resolution_state"]["fixtures_bound"] is False
    assert packet["shadow_resolution_state"]["outcomes_bound"] is False
    assert packet["shadow_resolution_state"]["shadow_resolution_computed"] is False
    assert packet["resolution_authority"]["brier_shadow_resolution_allowed"] is False
    assert packet["resolution_authority"]["brier_resolution_allowed"] is False
    assert packet["valid_for_brier_shadow_resolution_review"] is False
    assert packet["valid_for_brier_shadow_resolution"] is False
    assert packet["valid_for_brier_resolution"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_fixture_binding"] is False
    assert packet["valid_for_outcome_binding"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice24_prompt_packet_is_resolution_review_only() -> None:
    binding_review = _build_slice23_binding_review_for_slice24_tests()
    review = build_loop805_brier_shadow_resolution_review(
        timestamp=TIMESTAMP,
        held_out_set_binding_review=binding_review,
        resolution_checks=[
            {
                "check_id": "SHADOW_RESOLUTION_INPUT_REVIEW",
                "description": "Review inputs without resolving Brier.",
            }
        ],
    )
    packet = build_loop805_slice24_prompt_packet(
        timestamp=TIMESTAMP,
        brier_shadow_resolution_review=review,
    )

    assert packet["packet_status"] == "SLICE24_PROMPT_READY_ADVISORY_ONLY"
    assert "resolves no Brier scores" in packet["prompt"]
    assert "Slice 25 measurement dry-run execution proposal" in packet["prompt"]
    assert packet["brier_shadow_resolution_review_hash"] == review["canonical_hash"]
    assert packet["valid_for_brier_shadow_resolution_review"] is False
    assert packet["valid_for_brier_shadow_resolution"] is False
    assert packet["valid_for_brier_resolution"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def _build_slice24_resolution_review_for_slice25_tests() -> dict[str, Any]:
    binding_review = _build_slice23_binding_review_for_slice24_tests()
    return build_loop805_brier_shadow_resolution_review(
        timestamp=TIMESTAMP,
        held_out_set_binding_review=binding_review,
        resolution_checks=[
            {
                "check_id": "SHADOW_RESOLUTION_INPUT_REVIEW",
                "description": "Review inputs without resolving Brier.",
            }
        ],
    )


def test_slice25_measurement_dryrun_execution_proposal_stub_executes_nothing() -> None:
    review = _build_slice24_resolution_review_for_slice25_tests()
    packet = build_loop805_measurement_dryrun_execution_proposal_stub(
        timestamp=TIMESTAMP,
        brier_shadow_resolution_review=review,
        proposal_items=[
            {
                "item_id": "OPERATOR_EXECUTION_GATE_REQUIREMENT",
                "description": "Require separate operator execution gate before any dry run.",
            }
        ],
    )

    assert (
        packet["proposal_status"]
        == "SLICE25_MEASUREMENT_DRYRUN_EXECUTION_PROPOSAL_STUB_READY_ADVISORY_ONLY"
    )
    assert packet["proposal_item_count"] == 1
    item = packet["proposal_items"][0]
    assert item["required"] is True
    assert item["satisfied"] is False
    assert item["reviewed"] is False
    assert item["operator_gate_recorded"] is False
    assert item["operator_attested"] is False
    assert item["measurement_dryrun_executable"] is False
    assert item["measurement_dryrun_executed"] is False
    assert packet["execution_proposal_state"]["proposal_surface_prepared"] is True
    assert packet["execution_proposal_state"]["measurement_dryrun_executable"] is False
    assert packet["execution_proposal_state"]["measurement_dryrun_executed"] is False
    assert packet["execution_authority"]["measurement_dryrun_execution_allowed"] is False
    assert packet["valid_for_measurement_dryrun_execution_proposal"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_brier_resolution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)


def test_slice25_prompt_packet_is_execution_proposal_only() -> None:
    review = _build_slice24_resolution_review_for_slice25_tests()
    proposal = build_loop805_measurement_dryrun_execution_proposal_stub(
        timestamp=TIMESTAMP,
        brier_shadow_resolution_review=review,
        proposal_items=[
            {
                "item_id": "OPERATOR_EXECUTION_GATE_REQUIREMENT",
                "description": "Require separate operator execution gate before any dry run.",
            }
        ],
    )
    packet = build_loop805_slice25_prompt_packet(
        timestamp=TIMESTAMP,
        measurement_dryrun_execution_proposal_stub=proposal,
    )

    assert packet["packet_status"] == "SLICE25_PROMPT_READY_ADVISORY_ONLY"
    assert "executes no measurement dry run" in packet["prompt"]
    assert "Slice 26 operator measurement execution gate review" in packet["prompt"]
    assert (
        packet["measurement_dryrun_execution_proposal_stub_hash"]
        == proposal["canonical_hash"]
    )
    assert packet["valid_for_measurement_dryrun_execution_proposal"] is False
    assert packet["valid_for_measurement_dryrun_execution"] is False
    assert packet["valid_for_execution"] is False
    _assert_authority_locks(packet)
    _assert_canonical_hash(packet)
