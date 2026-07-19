from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.research_derived_subsystem_candidate_ledger import (
    build_research_derived_subsystem_candidate_ledger,
    write_research_derived_subsystem_candidate_ledger,
)
from scripts.research import run_research_derived_subsystem_candidate_ledger
from scripts.research.run_research_derived_subsystem_candidate_ledger import _load_p96_packet

_VALID_P96_PACKET: dict[str, object] = {
    "lane_id": "P96_RESEARCH_FOLD_VALIDATION_PLAN",
    "artifact_type": "ResearchFoldValidationPlan.v1",
    "validation_plan_status": "PASS",
    "validation_plan_ready": True,
    "validation_records": [
        {
            "validation_id": "DROP006_RESEARCH_FOLD_VALIDATION_PLAN",
            "spec_id": "DROP006_RESEARCH_FOLD_SPEC",
            "source_surface_id": "canon_drop_006_research_folds",
            "research_fold_family": "DROP006",
        },
        {
            "validation_id": "DROP007_RESEARCH_FOLD_VALIDATION_PLAN",
            "spec_id": "DROP007_RESEARCH_FOLD_SPEC",
            "source_surface_id": "canon_drop_007_research_folds",
            "research_fold_family": "DROP007",
        },
    ],
}


def test_missing_p96_returns_not_computable() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=None)
    assert packet["candidate_ledger_status"] == "NOT_COMPUTABLE"
    assert packet["candidates_ready"] is False
    assert packet["recommended_next_lane"] == "P96_RESEARCH_FOLD_VALIDATION_PLAN_REGENERATION"
    assert "p96_artifact_missing" in packet["missing_or_invalid_inputs"]


def test_invalid_p96_returns_not_computable() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(
        p96_packet={**_VALID_P96_PACKET, "validation_plan_status": "NOT_COMPUTABLE"}
    )
    assert packet["candidate_ledger_status"] == "NOT_COMPUTABLE"
    assert packet["candidates_ready"] is False
    assert packet["derived_candidates"] == []


def test_valid_p96_returns_pass_with_exactly_two_candidates() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    assert packet["candidate_ledger_status"] == "PASS"
    assert packet["candidates_ready"] is True
    assert len(packet["derived_candidates"]) == 2
    assert packet["recommended_next_lane"] == "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN"


def test_candidate_records_sorted_and_deterministic() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    ids = [record["candidate_id"] for record in packet["derived_candidates"]]
    assert ids == sorted(ids)
    assert ids == [
        "DROP006_INTENT_GRAPH_BEHAVIORAL_LOGIC_CANDIDATE",
        "DROP007_SITUATION_RUNTIME_PROACTIVE_COORDINATION_CANDIDATE",
    ]


def test_repeated_input_produces_identical_packet_hash() -> None:
    first = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    second = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    assert first["packet_hash"] == second["packet_hash"]
    assert first == second


def test_authority_locks_are_non_authoritative() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    locks = packet["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["projection_only"] is True
    assert locks["planning_only"] is True
    assert locks["evidence_only"] is True
    assert locks["candidate_only"] is True
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
    out_path = tmp_path / "out" / "research_derived_subsystem_candidate_ledger" / "latest.json"
    run_research_derived_subsystem_candidate_ledger.run(
        p96_packet=_VALID_P96_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    assert out_path.exists()


def test_schema_validates_generated_output() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path(
            "contracts/canon/research_derived_subsystem_candidate_ledger.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    jsonschema.validate(packet, schema)


def test_load_p96_packet_missing_returns_none(tmp_path: Path) -> None:
    assert _load_p96_packet(tmp_path / "missing.json") is None


def test_write_includes_final_newline(tmp_path: Path) -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    out_path = tmp_path / "packet.json"
    write_research_derived_subsystem_candidate_ledger(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
