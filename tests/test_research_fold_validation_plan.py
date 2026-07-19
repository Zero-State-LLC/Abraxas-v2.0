from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.research_fold_validation_plan import (
    build_research_fold_validation_plan,
    write_research_fold_validation_plan,
)
from scripts.research import run_research_fold_validation_plan
from scripts.research.run_research_fold_validation_plan import _load_p95_packet

_VALID_P95_PACKET: dict[str, object] = {
    "lane_id": "P95_RESEARCH_FOLD_DROP_SPEC_BUILDER",
    "artifact_type": "ResearchFoldDropSpecBuilder.v1",
    "spec_builder_status": "PASS",
    "specs_ready": True,
    "built_specs": [
        {"spec_id": "DROP006_RESEARCH_FOLD_SPEC"},
        {"spec_id": "DROP007_RESEARCH_FOLD_SPEC"},
    ],
}


def test_missing_p95_returns_not_computable() -> None:
    packet = build_research_fold_validation_plan(p95_packet=None)
    assert packet["validation_plan_status"] == "NOT_COMPUTABLE"
    assert packet["validation_plan_ready"] is False
    assert packet["recommended_next_lane"] == "P95_RESEARCH_FOLD_DROP_SPEC_BUILDER_REGENERATION"
    assert "p95_artifact_missing" in packet["missing_or_invalid_inputs"]


def test_invalid_p95_returns_not_computable() -> None:
    packet = build_research_fold_validation_plan(
        p95_packet={**_VALID_P95_PACKET, "spec_builder_status": "NOT_COMPUTABLE"}
    )
    assert packet["validation_plan_status"] == "NOT_COMPUTABLE"
    assert packet["validation_plan_ready"] is False
    assert packet["validation_records"] == []


def test_valid_p95_returns_pass_with_exactly_two_records() -> None:
    packet = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    assert packet["validation_plan_status"] == "PASS"
    assert packet["validation_plan_ready"] is True
    assert len(packet["validation_records"]) == 2
    assert packet["recommended_next_lane"] == "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER"


def test_validation_records_sorted_and_deterministic() -> None:
    packet = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    ids = [record["validation_id"] for record in packet["validation_records"]]
    assert ids == sorted(ids)
    assert ids == [
        "DROP006_RESEARCH_FOLD_VALIDATION_PLAN",
        "DROP007_RESEARCH_FOLD_VALIDATION_PLAN",
    ]


def test_repeated_input_produces_identical_packet_hash() -> None:
    first = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    second = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    assert first["packet_hash"] == second["packet_hash"]
    assert first == second


def test_authority_locks_are_non_authoritative() -> None:
    packet = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    locks = packet["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["projection_only"] is True
    assert locks["planning_only"] is True
    assert locks["evidence_only"] is True
    assert locks["validation_only"] is True
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
    out_path = tmp_path / "out" / "research_fold_validation_plan" / "latest.json"
    run_research_fold_validation_plan.run(
        p95_packet=_VALID_P95_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    assert out_path.exists()


def test_schema_validates_generated_output() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/canon/research_fold_validation_plan.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    packet = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    jsonschema.validate(packet, schema)


def test_load_p95_packet_missing_returns_none(tmp_path: Path) -> None:
    assert _load_p95_packet(tmp_path / "missing.json") is None


def test_write_includes_final_newline(tmp_path: Path) -> None:
    packet = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    out_path = tmp_path / "packet.json"
    write_research_fold_validation_plan(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
