"""Tests for doctrine validator."""

from __future__ import annotations

from pathlib import Path

from core.pipelines.registry import load_contracts
from core.pipelines.validator import validate_pipeline_contract
from core.runes.registry import load_rune_catalog
from core.yggdrasil.validator import load_route_graphs

CONTRACTS_DIR = Path("contracts/pipelines")
RUNE_CATALOG_PATH = Path("contracts/runes/catalog.v1.json")
ROUTES_DIR = Path("contracts/yggdrasil/routes")


def _get_validation_results() -> list[dict]:
    rune_catalog = load_rune_catalog(RUNE_CATALOG_PATH)
    route_graphs = load_route_graphs(ROUTES_DIR)
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


def test_doctrine_validator_deterministic():
    """Two identical runs produce identical results."""
    results1 = _get_validation_results()
    results2 = _get_validation_results()
    assert results1 == results2


def test_all_tier1_pipelines_validated():
    results = _get_validation_results()
    assert len(results) == 7


def test_all_tier1_pipelines_doctrine_compliant():
    results = _get_validation_results()
    for r in results:
        assert r["status"] == "doctrine_compliant", (
            f"Pipeline {r['pipeline_id']} is {r['status']}: "
            f"{[g for g in r['gate_results'] if not g['passed']]}"
        )


def test_missing_route_graph_yields_not_computable():
    rune_catalog = load_rune_catalog(RUNE_CATALOG_PATH)
    contracts = load_contracts(CONTRACTS_DIR)
    result = validate_pipeline_contract(contracts[0], rune_catalog, None)
    assert result["status"] == "not_computable"


def test_unknown_rune_yields_not_computable():
    """A contract referencing a non-existent rune gets not_computable."""
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


def test_gate_results_structure():
    results = _get_validation_results()
    for r in results:
        assert "pipeline_id" in r
        assert "status" in r
        assert "gate_results" in r
        for g in r["gate_results"]:
            assert "gate" in g
            assert "passed" in g
