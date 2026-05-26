from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.research_operator_stabilization_decision_record import (
    build_research_operator_stabilization_decision_record,
    write_research_operator_stabilization_decision_record,
)
from scripts import run_research_operator_stabilization_decision_record
from scripts.run_research_operator_stabilization_decision_record import _load_p99_packet

_VALID_P99_PACKET: dict[str, object] = {
    "lane_id": "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN",
    "artifact_type": "ResearchCrossDropConflictScan.v1",
    "conflict_scan_status": "PASS",
    "conflict_scan_ready": True,
    "conflict_findings": [{"finding_id": "DROP006_DROP007_CROSS_DROP_CONFLICT_SCAN"}],
    "conflict_summary": {
        "scanned_drop_count": 2,
        "conflict_count": 0,
        "blocking_conflict_detected": False,
    },
}


def test_missing_p99_artifact_returns_not_computable() -> None:
    packet = build_research_operator_stabilization_decision_record(p99_packet=None)
    assert packet["stabilization_decision_status"] == "NOT_COMPUTABLE"
    assert packet["decision_record_ready"] is False


def test_invalid_p99_artifact_returns_not_computable() -> None:
    packet = build_research_operator_stabilization_decision_record(
        p99_packet={**_VALID_P99_PACKET, "conflict_scan_status": "NOT_COMPUTABLE"}
    )
    assert packet["stabilization_decision_status"] == "NOT_COMPUTABLE"


def test_blocking_conflict_detected_returns_not_computable() -> None:
    p99 = dict(_VALID_P99_PACKET)
    p99["conflict_summary"] = {
        "scanned_drop_count": 2,
        "conflict_count": 1,
        "blocking_conflict_detected": True,
    }
    packet = build_research_operator_stabilization_decision_record(p99_packet=p99)
    assert packet["stabilization_decision_status"] == "NOT_COMPUTABLE"


def test_valid_p99_returns_pass() -> None:
    packet = build_research_operator_stabilization_decision_record(p99_packet=_VALID_P99_PACKET)
    assert packet["stabilization_decision_status"] == "PASS"
    assert packet["decision_record_ready"] is True


def test_operator_decision_hold_for_review() -> None:
    packet = build_research_operator_stabilization_decision_record(p99_packet=_VALID_P99_PACKET)
    assert packet["decision_record"]["operator_decision"] == "HOLD_FOR_OPERATOR_REVIEW"


def test_stabilization_recommendation_non_activation() -> None:
    packet = build_research_operator_stabilization_decision_record(p99_packet=_VALID_P99_PACKET)
    assert (
        packet["decision_record"]["stabilization_recommendation"]
        == "READY_FOR_OPERATOR_REVIEW_NOT_ACTIVATION"
    )


def test_determinism_packet_hash() -> None:
    first = build_research_operator_stabilization_decision_record(p99_packet=_VALID_P99_PACKET)
    second = build_research_operator_stabilization_decision_record(p99_packet=_VALID_P99_PACKET)
    assert first["packet_hash"] == second["packet_hash"]


def test_authority_locks_forbidden_flags_false() -> None:
    packet = build_research_operator_stabilization_decision_record(p99_packet=_VALID_P99_PACKET)
    locks = packet["authority_locks"]
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
    assert locks["activation_approved"] is False
    assert locks["authorization_granted"] is False


def test_runner_writes_output(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_operator_stabilization_decision_record" / "latest.json"
    run_research_operator_stabilization_decision_record.run(
        p99_packet=_VALID_P99_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    assert out_path.exists()


def test_schema_validates_output() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/canon/research_operator_stabilization_decision_record.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    packet = build_research_operator_stabilization_decision_record(p99_packet=_VALID_P99_PACKET)
    jsonschema.validate(packet, schema)


def test_load_p99_packet_missing_returns_none(tmp_path: Path) -> None:
    assert _load_p99_packet(tmp_path / "missing.json") is None


def test_write_newline(tmp_path: Path) -> None:
    packet = build_research_operator_stabilization_decision_record(p99_packet=_VALID_P99_PACKET)
    out_path = tmp_path / "packet.json"
    write_research_operator_stabilization_decision_record(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
