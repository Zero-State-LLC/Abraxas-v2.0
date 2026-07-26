"""Follow-up binding tests: Alembic YGGDRASIL route + Oracle intake bridge."""

from __future__ import annotations

from pathlib import Path

from core.alembic.oracle_bridge import (
    architecture_aware_intake_from_oracle_candidate,
    architecture_aware_intakes_from_oracle_receipt,
    task_envelope_from_oracle_candidate,
)
from core.pipelines.registry import load_pipeline_contract
from core.yggdrasil.rune_route_binding_matrix import build_coupling_map
from core.yggdrasil.validator import load_route_graph

REPO = Path(__file__).resolve().parents[1]


def test_alembic_pipeline_and_route_load_with_locked_authority() -> None:
    contract = load_pipeline_contract(REPO / "contracts/pipelines/alembic_spine.v1_1.json")
    route = load_route_graph(REPO / "contracts/yggdrasil/routes/alembic_spine.route.v1.json")
    assert contract.pipeline_id == "alembic_spine"
    assert route.pipeline_id == "alembic_spine"
    contract.authority.assert_locked()
    route.authority.assert_locked()
    assert "RUNE.PIPELINE.ROUTE" in contract.required_runes
    exposed = {
        node.rune_id
        for node in route.nodes
        if getattr(node, "rune_id", None)
    }
    assert set(contract.required_runes).issubset(exposed)


def test_alembic_route_bound_in_coupling_map_without_unbound_runes() -> None:
    coupling = build_coupling_map(repo_root=REPO)
    assert coupling["pipeline_to_route"]["alembic_spine"].endswith(
        "alembic_spine.route.v1.json"
    )
    assert coupling["unbound_runes"] == []
    assert "alembic_spine" in coupling["rune_to_pipelines"]["RUNE.PIPELINE.ROUTE"]


def test_oracle_bridge_does_not_claim_second_pipeline_or_mutation() -> None:
    candidate = {
        "signal_id": "sig-1",
        "signal_hash": "hash-1",
        "signal_status": "CANDIDATE_SHADOW_ONLY",
        "adapter_id": "json_adapter",
        "domain": "research",
        "source_ref": {"source_uri": "notes.json"},
    }
    intake = architecture_aware_intake_from_oracle_candidate(candidate)
    assert intake["second_ingest_pipeline"] is False
    assert intake["mutates_oracle_receipt"] is False
    assert intake["oracle_signal_id"] == "sig-1"
    task = task_envelope_from_oracle_candidate(candidate, run_id="run-1")
    assert task.run_id == "run-1"
    assert "symbolic_expert" in task.allowed_architecture_families


def test_oracle_receipt_projection_is_read_only() -> None:
    receipt = {
        "candidate_signals": [
            {
                "signal_id": "a",
                "signal_hash": "h",
                "signal_status": "CANDIDATE_SHADOW_ONLY",
                "adapter_id": "filesystem_adapter",
                "domain": "local",
                "source_ref": {"source_uri": "a.txt"},
            }
        ]
    }
    rows = architecture_aware_intakes_from_oracle_receipt(receipt)
    assert len(rows) == 1
    assert rows[0]["mutates_oracle_receipt"] is False
