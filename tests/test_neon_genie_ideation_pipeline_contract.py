"""Tests for the neon_genie_ideation full pipeline contract (Track B slice 1/8, #1125).

Covers the contracts/pipelines/neon_genie_ideation.v1_1.json + paired
contracts/yggdrasil/routes/neon_genie_ideation.route.v1.json pair that closes
the CONTRACT_V0 -> ALIGNED gap for the Neon Genie subsystem.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from core.pipelines.models import PipelineContractV11
from core.pipelines.registry import load_pipeline_contract
from core.pipelines.validator import validate_pipeline_contract
from core.runes.registry import load_rune_catalog
from core.yggdrasil.models import YggdrasilRouteGraph
from core.yggdrasil.validator import load_route_graph

CONTRACT_PATH = Path("contracts/pipelines/neon_genie_ideation.v1_1.json")
ROUTE_PATH = Path("contracts/yggdrasil/routes/neon_genie_ideation.route.v1.json")
RUNE_CATALOG_PATH = Path("contracts/runes/catalog.v1.json")


def test_contract_loads_and_matches_owner_subsystem():
    contract = load_pipeline_contract(CONTRACT_PATH)
    assert isinstance(contract, PipelineContractV11)
    assert contract.schema_version == "AbraxasPipelineAutomationContract.v1.1"
    assert contract.pipeline_id == "neon_genie_ideation"
    assert contract.owner_subsystem == "Neon Genie"
    assert contract.lane.value == "SHADOW"


def test_contract_authority_all_locked():
    contract = load_pipeline_contract(CONTRACT_PATH)
    contract.authority.assert_locked()  # should not raise
    assert all(value is False for value in contract.authority.model_dump().values())


def test_contract_rejects_malformed_authority():
    data = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    data["authority"]["canon_mutation_allowed"] = True
    with pytest.raises(ValidationError):
        PipelineContractV11.model_validate(data)


def test_contract_rejects_missing_required_field():
    data = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    del data["required_runes"]
    with pytest.raises(ValidationError):
        PipelineContractV11.model_validate(data)


def test_contract_rejects_empty_required_runes():
    data = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    data["required_runes"] = []
    with pytest.raises(ValidationError):
        PipelineContractV11.model_validate(data)


def test_route_graph_loads_and_pairs_with_contract():
    graph = load_route_graph(ROUTE_PATH)
    assert isinstance(graph, YggdrasilRouteGraph)
    assert graph.schema_version == "YggdrasilRouteGraph.v1"
    assert graph.pipeline_id == "neon_genie_ideation"

    contract = load_pipeline_contract(CONTRACT_PATH)
    node_ids = {node.node_id for node in graph.nodes}
    assert set(contract.yggdrasil_nodes) == node_ids


def test_route_graph_authority_all_locked():
    graph = load_route_graph(ROUTE_PATH)
    graph.authority.assert_locked()  # should not raise


def test_doctrine_validator_accepts_contract():
    contract = load_pipeline_contract(CONTRACT_PATH)
    rune_catalog = load_rune_catalog(RUNE_CATALOG_PATH)
    graph = load_route_graph(ROUTE_PATH)
    result = validate_pipeline_contract(contract, rune_catalog, graph.model_dump())
    assert result["pipeline_id"] == "neon_genie_ideation"
    assert result["status"] in {"doctrine_compliant", "legacy_contract_posture"}


def test_runner_writes_out_receipt_with_no_authority_granted(tmp_path, monkeypatch):
    output_path = (
        tmp_path / "out" / "neon_genie" / "neon_genie_ideation_receipt_001.latest.json"
    )
    monkeypatch.setattr(
        "sys.argv",
        ["run_abx_neon_genie.py", "--output", str(output_path)],
    )

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_abx_neon_genie_under_test",
        Path("scripts/codegen/run_abx_neon_genie.py"),
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.main() == 0
    assert output_path.exists()

    receipt = json.loads(output_path.read_text(encoding="utf-8"))
    assert receipt["schema_version"] == "NeonGenieRunReceipt.v0.1"
    assert receipt["authority"]["execution_authority"] is False
    assert receipt["authority"]["promotion_authorized"] is False
    assert receipt["authority"]["canon_mutation_allowed"] is False
    assert receipt["operator_packet"]["authority"]["execution_authority"] is False
    assert (
        receipt["operator_packet"]["authority"]["forecast_routing_authorized"] is False
    )
