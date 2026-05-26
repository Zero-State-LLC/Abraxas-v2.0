from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.research_shadow_stabilization_proof_plan import (
    build_research_shadow_stabilization_proof_plan,
    write_research_shadow_stabilization_proof_plan,
)
from scripts import run_research_shadow_stabilization_proof_plan
from scripts.run_research_shadow_stabilization_proof_plan import _load_p97_packet

_VALID_P97_PACKET: dict[str, object] = {
    "lane_id": "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER",
    "artifact_type": "ResearchDerivedSubsystemCandidateLedger.v1",
    "candidate_ledger_status": "PASS",
    "candidates_ready": True,
    "derived_candidates": [
        {
            "candidate_id": "DROP006_INTENT_GRAPH_BEHAVIORAL_LOGIC_CANDIDATE",
            "source_surface_id": "canon_drop_006_research_folds",
            "research_fold_family": "DROP006",
        },
        {
            "candidate_id": "DROP007_SITUATION_RUNTIME_PROACTIVE_COORDINATION_CANDIDATE",
            "source_surface_id": "canon_drop_007_research_folds",
            "research_fold_family": "DROP007",
        },
    ],
}


def test_missing_p97_returns_not_computable() -> None:
    packet = build_research_shadow_stabilization_proof_plan(p97_packet=None)
    assert packet["stabilization_proof_plan_status"] == "NOT_COMPUTABLE"
    assert packet["stabilization_proof_plan_ready"] is False
    assert packet["recommended_next_lane"] == "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER_REGENERATION"
    assert "p97_artifact_missing" in packet["missing_or_invalid_inputs"]


def test_invalid_p97_returns_not_computable() -> None:
    packet = build_research_shadow_stabilization_proof_plan(
        p97_packet={**_VALID_P97_PACKET, "candidate_ledger_status": "NOT_COMPUTABLE"}
    )
    assert packet["stabilization_proof_plan_status"] == "NOT_COMPUTABLE"
    assert packet["stabilization_proof_plan_ready"] is False
    assert packet["stabilization_proof_records"] == []


def test_valid_p97_returns_pass_with_exactly_two_records() -> None:
    packet = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    assert packet["stabilization_proof_plan_status"] == "PASS"
    assert packet["stabilization_proof_plan_ready"] is True
    assert len(packet["stabilization_proof_records"]) == 2
    assert packet["recommended_next_lane"] == "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN"


def test_stabilization_records_sorted_and_deterministic() -> None:
    packet = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    ids = [record["proof_id"] for record in packet["stabilization_proof_records"]]
    assert ids == sorted(ids)
    assert ids == [
        "DROP006_INTENT_GRAPH_BEHAVIORAL_LOGIC_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN",
        "DROP007_SITUATION_RUNTIME_PROACTIVE_COORDINATION_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN",
    ]


def test_repeated_input_produces_identical_packet_hash() -> None:
    first = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    second = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    assert first["packet_hash"] == second["packet_hash"]
    assert first == second


def test_authority_locks_are_non_authoritative() -> None:
    packet = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    locks = packet["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["projection_only"] is True
    assert locks["planning_only"] is True
    assert locks["evidence_only"] is True
    assert locks["proof_only"] is True
    assert locks["shadow_only"] is True
    assert locks["production_activation"] is False
    assert locks["canon_promotion"] is False
    assert locks["scheduler_mutation"] is False
    assert locks["runtime_authority"] is False
    assert locks["forecast_influence"] is False
    assert locks["execution_authority"] is False
    assert locks["repair_execution_authority"] is False
    assert locks["regeneration_execution_authority"] is False
    assert locks["token_minting_allowed"] is False
    assert locks["valid_for_execution"] is False
    assert locks["canonical_status"] == "ADVISORY_ONLY"


def test_runner_writes_latest_json(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_shadow_stabilization_proof_plan" / "latest.json"
    run_research_shadow_stabilization_proof_plan.run(
        p97_packet=_VALID_P97_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    assert out_path.exists()


def test_schema_validates_generated_output() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/canon/research_shadow_stabilization_proof_plan.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    packet = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    jsonschema.validate(packet, schema)


def test_load_p97_packet_missing_returns_none(tmp_path: Path) -> None:
    assert _load_p97_packet(tmp_path / "missing.json") is None


def test_write_includes_final_newline(tmp_path: Path) -> None:
    packet = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    out_path = tmp_path / "packet.json"
    write_research_shadow_stabilization_proof_plan(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
