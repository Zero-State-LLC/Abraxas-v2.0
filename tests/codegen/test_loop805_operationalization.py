from __future__ import annotations

from core.canonical.json import canonical_hash
from core.codegen.loop805_activation_proposal import (
    build_loop805_gate_selection_matrix,
    build_loop805_activation_proposal,
    build_loop805_slice3_prompt_packet,
    build_loop805_slice4_prompt_packet,
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
