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
        graph_data = route_graphs[contract.pipeline_id].model_dump() if contract.pipeline_id in route_graphs else None
        result = validate_pipeline_contract(contract, rune_catalog, graph_data)
        results.append(result)
    return results


def test_doctrine_validator_deterministic() -> None:
    assert _get_validation_results() == _get_validation_results()


def test_all_tier1_pipelines_validated() -> None:
    assert len(_get_validation_results()) == 7


def test_status_not_ambiguous_blanket_repair() -> None:
    results = _get_validation_results()
    assert not all(r["status"] == "repair_required" for r in results)


def test_legacy_contract_posture_is_explicit() -> None:
    results = _get_validation_results()
    for r in results:
        assert "contract_posture" in r
        assert r["contract_posture"] in {"current", "legacy_accepted", "legacy_needs_upgrade", "invalid", "not_computable"}


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
        assert {"pipeline_id", "status", "gate_results", "failed_gates", "legacy_gates", "not_applicable_gates", "required_upgrade_actions"}.issubset(r.keys())
        for g in r["gate_results"]:
            assert {"gate_id", "applies_to", "required_for_versions", "required_for_pipeline_types", "status", "reason"}.issubset(g.keys())


def test_sandbox_gates_not_globally_required_for_non_sandbox() -> None:
    results = _get_validation_results()
    for r in results:
        if "sandbox" not in r["pipeline_id"]:
            na = [g for g in r["not_applicable_gates"] if g["gate_id"].startswith("sandbox_")]
            assert na
