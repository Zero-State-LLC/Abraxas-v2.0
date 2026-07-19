"""Tests for doctrine validator."""

from __future__ import annotations

from pathlib import Path

from core.pipelines.registry import load_contracts
from core.pipelines.validator import validate_pipeline_contract
from core.runtime.graph_runner import run_execution_graph
from core.runtime.topology_replay import replay_execution_graph
from core.runes.registry import load_rune_catalog
from core.yggdrasil.validator import load_route_graphs

CONTRACTS_DIR = Path("contracts/pipelines")
RUNE_CATALOG_PATH = Path("contracts/runes/catalog.v1.json")
ROUTES_DIR = Path("contracts/yggdrasil/routes")
RUNTIME_EVIDENCE_PATHS = (
    Path("out/yggdrasil/runtime.latest.json"),
    Path("out/graph_replay/latest.json"),
    Path("out/route_cache/latest.json"),
)


def _ensure_runtime_evidence(route_graphs: dict) -> None:
    if all(path.exists() for path in RUNTIME_EVIDENCE_PATHS):
        return
    route_graph = route_graphs.get("research_intake") or route_graphs[sorted(route_graphs)[0]]
    runtime_run = run_execution_graph(route_graph)
    replay_execution_graph(runtime_run)


def _get_validation_results() -> list[dict]:
    rune_catalog = load_rune_catalog(RUNE_CATALOG_PATH)
    route_graphs = load_route_graphs(ROUTES_DIR)
    _ensure_runtime_evidence(route_graphs)
    contracts = load_contracts(CONTRACTS_DIR)
    results = []
    for contract in contracts:
        graph_data = (
            route_graphs[contract.pipeline_id].model_dump()
            if contract.pipeline_id in route_graphs
            else None
        )
        result = validate_pipeline_contract(contract, rune_catalog, graph_data)
        results.append(result)
    return results


def test_doctrine_validator_deterministic() -> None:
    assert _get_validation_results() == _get_validation_results()


def test_all_observed_pipeline_contracts_validated() -> None:
    assert len(_get_validation_results()) == 11


def test_status_not_ambiguous_blanket_repair() -> None:
    results = _get_validation_results()
    assert not all(r["status"] == "repair_required" for r in results)


def test_legacy_contract_posture_is_explicit() -> None:
    results = _get_validation_results()
    for r in results:
        assert "contract_posture" in r
        assert r["contract_posture"] in {
            "current",
            "legacy_accepted",
            "legacy_needs_upgrade",
            "invalid",
            "not_computable",
        }


def test_missing_route_graph_yields_not_computable() -> None:
    rune_catalog = load_rune_catalog(RUNE_CATALOG_PATH)
    contracts = load_contracts(CONTRACTS_DIR)
    result = validate_pipeline_contract(contracts[0], rune_catalog, None)
    assert result["status"] == "not_computable"


def test_unknown_rune_yields_not_computable() -> None:
    from core.pipelines.models import Authority, PipelineContractV11, PipelineLane

    contract = PipelineContractV11(
        pipeline_id="test_unknown_rune",
        trigger="test trigger",
        owner_subsystem="test",
        lane=PipelineLane.SHADOW,
        typed_ir_schema="TestIR.v1",
        required_runes=["RUNE.NONEXISTENT.RUNE"],
        yggdrasil_nodes=["test.node"],
        required_artifacts=["test.artifact"],
        final_state_policy=["hold"],
        authority=Authority(),
    )
    rune_catalog = load_rune_catalog(RUNE_CATALOG_PATH)
    route_graph = {"nodes": [{"node_id": "test.node"}], "edges": []}
    result = validate_pipeline_contract(contract, rune_catalog, route_graph)
    assert result["status"] == "not_computable"


def test_gate_results_structure() -> None:
    for r in _get_validation_results():
        assert {
            "pipeline_id",
            "status",
            "gate_results",
            "failed_gates",
            "legacy_gates",
            "not_applicable_gates",
            "required_upgrade_actions",
        }.issubset(r.keys())
        for g in r["gate_results"]:
            assert {
                "gate_id",
                "applies_to",
                "required_for_versions",
                "required_for_pipeline_types",
                "status",
                "reason",
            }.issubset(g.keys())


def test_sandbox_gates_not_globally_required_for_non_sandbox() -> None:
    results = _get_validation_results()
    for r in results:
        if "sandbox" not in r["pipeline_id"]:
            na = [
                g
                for g in r["not_applicable_gates"]
                if g["gate_id"].startswith("sandbox_")
            ]
            assert na


def test_doctrine_summary_uses_derived_milestone() -> None:
    from scripts.governance.run_doctrine_validator import _build_summary
    from core.spine.milestone_validator import MilestoneValidationPacket

    mv = MilestoneValidationPacket(
        validation_id="x",
        reported_active_milestone="v2.0.5-governed-adaptive-sandbox",
        derived_active_milestone="v2.0.9-governed-weight-drift-simulation",
        derived_evidence_status="code_verified",
        stale_metadata_detected=False,
        registry_status="passed",
        partial_milestones=[],
        missing_milestones=[],
        lineage_valid=True,
        status="passed",
    )
    summary = _build_summary(
        [], "v2.0.9-governed-weight-drift-simulation", mv, "passed"
    )
    assert summary["active_milestone"] == "v2.0.9-governed-weight-drift-simulation"


def test_aal_viz_milestone_summary_projection_only() -> None:
    from core.projections.aal_viz import build_projection_packet

    packet = build_projection_packet(
        {"pipeline_count": 0},
        [],
        {"queue_item_count": 0},
        milestone_summary={
            "active_milestone": "v2.0.9-governed-weight-drift-simulation",
            "stabilized_milestones": ["v2.0.9-governed-weight-drift-simulation"],
            "latest_stable_hash": "h",
            "lineage_depth": 1,
            "derived_evidence_status": "code_verified",
            "artifact_verified_milestones": [],
            "code_verified_milestones": ["v2.0.9-governed-weight-drift-simulation"],
            "partial_milestones": [],
            "missing_milestones": [],
            "stale_metadata_detected": False,
            "milestone_validator_status": "passed",
        },
    )
    assert "milestone_summary" in packet
    assert packet["projection_only"] is True
    assert packet["inference_authority"] is False


def test_doctrine_summary_includes_overlay_firewall_gates() -> None:
    from scripts.governance.run_doctrine_validator import _build_summary

    summary = _build_summary(
        [],
        overlay_governance_status={
            "overlay_firewall_readiness_gate": "passed",
            "overlay_firewall_governance_gate": "passed",
            "overlay_firewall_containment_gate": "passed",
            "overlay_firewall_rollback_gate": "passed",
            "overlay_firewall_continuity_gate": "passed",
            "overlay_firewall_eligibility_gate": "passed",
            "overlay_firewall_replay_gate": "passed",
            "overlay_firewall_operator_review_gate": "passed",
        },
    )
    assert summary["overlay_firewall_readiness_gate"] == "passed"
    assert summary["overlay_firewall_operator_review_gate"] == "passed"
