from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.research_canary_advisory_shadow_activation_record import (
    build_research_canary_advisory_shadow_activation_record,
    write_research_canary_advisory_shadow_activation_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _schema() -> dict:
    return json.loads(
        Path(
            "contracts/canon/research_canary_advisory_shadow_activation_record.v1.schema.json"
        ).read_text()
    )


def test_p132_emitted_with_drop006a_pilot() -> None:
    packet = build_research_canary_advisory_shadow_activation_record(REPO_ROOT)
    assert packet["status"] == "RESEARCH_CANARY_ADVISORY_SHADOW_ACTIVATION_RECORD_EMITTED"
    assert packet["lane_status"] == "ADVISORY_SHADOW_ACTIVATION_RECORD_EMITTED"
    assert packet["operator_id"] == "daniel_meyer"
    assert len(packet["candidate_activation_records"]) == 6
    drop006a = next(
        rec
        for rec in packet["candidate_activation_records"]
        if rec["candidate_id"] == "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"
    )
    assert drop006a["advisory_shadow_activation_approved"] is True
    assert drop006a["wiring_mode"] == "SHADOW_ADVISORY_ONLY"
    drop006b = next(
        rec
        for rec in packet["candidate_activation_records"]
        if rec["candidate_id"] == "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER"
    )
    assert drop006b["advisory_shadow_activation_approved"] is True
    drop006c = next(
        rec
        for rec in packet["candidate_activation_records"]
        if rec["candidate_id"] == "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER"
    )
    assert drop006c["advisory_shadow_activation_approved"] is True
    drop007a = next(
        rec
        for rec in packet["candidate_activation_records"]
        if rec["candidate_id"] == "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER"
    )
    assert drop007a["advisory_shadow_activation_approved"] is True
    validate(packet, _schema())


def test_p132_all_records_shadow_only_wiring_mode() -> None:
    packet = build_research_canary_advisory_shadow_activation_record(REPO_ROOT)
    for record in packet["candidate_activation_records"]:
        assert record["wiring_mode"] == "SHADOW_ADVISORY_ONLY"
        assert record["execution_authority"] is False
        assert record["production_activation"] is False


def test_p132_authority_locks_all_false() -> None:
    packet = build_research_canary_advisory_shadow_activation_record(REPO_ROOT)
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_p132_provenance_hashes_present() -> None:
    packet = build_research_canary_advisory_shadow_activation_record(REPO_ROOT)
    assert packet["upstream_packet_hash"] != "NOT_COMPUTABLE"
    assert packet["operator_attestation_hash"].startswith("sha256:")


def test_p132_deterministic() -> None:
    first = build_research_canary_advisory_shadow_activation_record(REPO_ROOT)
    second = build_research_canary_advisory_shadow_activation_record(REPO_ROOT)
    assert first == second


def test_p132_blocked_without_p131(tmp_path: Path) -> None:
    packet = build_research_canary_advisory_shadow_activation_record(tmp_path)
    assert packet["status"] == "NOT_COMPUTABLE"


def test_p132_writer(tmp_path: Path) -> None:
    out = tmp_path / "latest.json"
    packet = write_research_canary_advisory_shadow_activation_record(REPO_ROOT, out_path=out)
    assert out.exists()
    assert json.loads(out.read_text()) == packet
