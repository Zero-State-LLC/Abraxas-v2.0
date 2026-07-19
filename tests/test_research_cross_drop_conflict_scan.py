from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.research_cross_drop_conflict_scan import (
    build_research_cross_drop_conflict_scan,
    write_research_cross_drop_conflict_scan,
)
from scripts.research import run_research_cross_drop_conflict_scan
from scripts.research.run_research_cross_drop_conflict_scan import _load_p98_packet

_VALID_P98_PACKET: dict[str, object] = {
    "lane_id": "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN",
    "artifact_type": "ResearchShadowStabilizationProofPlan.v1",
    "stabilization_proof_plan_status": "PASS",
    "stabilization_proof_plan_ready": True,
    "stabilization_proof_records": [
        {
            "proof_id": "DROP006_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN",
            "source_surface_id": "canon_drop_006_research_folds",
            "research_fold_family": "DROP006",
        },
        {
            "proof_id": "DROP007_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN",
            "source_surface_id": "canon_drop_007_research_folds",
            "research_fold_family": "DROP007",
        },
    ],
}


def test_missing_p98_returns_not_computable() -> None:
    packet = build_research_cross_drop_conflict_scan(p98_packet=None)
    assert packet["conflict_scan_status"] == "NOT_COMPUTABLE"
    assert packet["conflict_scan_ready"] is False
    assert packet["recommended_next_lane"] == "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN_REGENERATION"
    assert "p98_artifact_missing" in packet["missing_or_invalid_inputs"]


def test_invalid_p98_returns_not_computable() -> None:
    packet = build_research_cross_drop_conflict_scan(
        p98_packet={**_VALID_P98_PACKET, "stabilization_proof_plan_status": "NOT_COMPUTABLE"}
    )
    assert packet["conflict_scan_status"] == "NOT_COMPUTABLE"
    assert packet["conflict_scan_ready"] is False
    assert packet["conflict_findings"] == []


def test_valid_p98_returns_pass_with_one_pairwise_finding() -> None:
    packet = build_research_cross_drop_conflict_scan(p98_packet=_VALID_P98_PACKET)
    assert packet["conflict_scan_status"] == "PASS"
    assert packet["conflict_scan_ready"] is True
    assert len(packet["conflict_findings"]) == 1
    assert packet["recommended_next_lane"] == "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD"


def test_conflict_summary_expected_values() -> None:
    packet = build_research_cross_drop_conflict_scan(p98_packet=_VALID_P98_PACKET)
    assert packet["conflict_summary"] == {
        "scanned_drop_count": 2,
        "conflict_count": 0,
        "blocking_conflict_detected": False,
    }


def test_finding_arrays_are_sorted_and_deterministic() -> None:
    packet = build_research_cross_drop_conflict_scan(p98_packet=_VALID_P98_PACKET)
    finding = packet["conflict_findings"][0]
    assert finding["compared_proof_ids"] == sorted(finding["compared_proof_ids"])
    assert finding["compared_source_surface_ids"] == sorted(finding["compared_source_surface_ids"])


def test_repeated_input_produces_identical_packet_hash() -> None:
    first = build_research_cross_drop_conflict_scan(p98_packet=_VALID_P98_PACKET)
    second = build_research_cross_drop_conflict_scan(p98_packet=_VALID_P98_PACKET)
    assert first["packet_hash"] == second["packet_hash"]
    assert first == second


def test_authority_locks_are_non_authoritative() -> None:
    packet = build_research_cross_drop_conflict_scan(p98_packet=_VALID_P98_PACKET)
    locks = packet["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["projection_only"] is True
    assert locks["planning_only"] is True
    assert locks["evidence_only"] is True
    assert locks["scan_only"] is True
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
    out_path = tmp_path / "out" / "research_cross_drop_conflict_scan" / "latest.json"
    run_research_cross_drop_conflict_scan.run(
        p98_packet=_VALID_P98_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    assert out_path.exists()


def test_schema_validates_generated_output() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/canon/research_cross_drop_conflict_scan.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    packet = build_research_cross_drop_conflict_scan(p98_packet=_VALID_P98_PACKET)
    jsonschema.validate(packet, schema)


def test_load_p98_packet_missing_returns_none(tmp_path: Path) -> None:
    assert _load_p98_packet(tmp_path / "missing.json") is None


def test_write_includes_final_newline(tmp_path: Path) -> None:
    packet = build_research_cross_drop_conflict_scan(p98_packet=_VALID_P98_PACKET)
    out_path = tmp_path / "packet.json"
    write_research_cross_drop_conflict_scan(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
