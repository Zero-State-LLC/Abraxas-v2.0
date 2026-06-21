from __future__ import annotations

from core.canonical.json import canonical_hash
from core.codegen.loop805_controller import build_loop805_controller_plan
from core.codegen.loop805_observability import (
    TARGET_TOKENS_PER_TURN,
    build_loop805_daily_dashboard,
    build_loop805_regression_pr_proposal,
    build_spine_route_decision,
)
from core.codegen.loop805_operationalization import build_loop805_baseline_receipt
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
    )

    assert proposal["proposal_status"] == "PROPOSAL_ONLY_OPERATOR_GATE_REQUIRED"
    assert proposal["auto_pr_generation"]["authorized"] is False
    assert proposal["valid_for_github_writeback"] is False
    assert proposal["dashboard_hash"] == dashboard["canonical_hash"]
    _assert_authority_locks(proposal)
    _assert_canonical_hash(proposal)
