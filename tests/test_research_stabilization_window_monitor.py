from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from core.research_stabilization_window_monitor import (
    REQUIRED_PROOF_FLAGS,
    build_research_stabilization_window_monitor,
    write_research_stabilization_window_monitor,
)
from scripts import run_research_stabilization_window_monitor
from scripts.run_research_stabilization_window_monitor import (
    P101_DEFAULT_PATH,
    _load_json_packet,
    _parse_args,
)

_AUTHORITY_LOCKS = {
    "production_activation": False,
    "canon_promotion": False,
    "runtime_mutation": False,
    "forecast_influence": False,
    "forecast_weight_allowed": False,
    "shadow_to_forecast_leakage": False,
    "scheduler_mutation": False,
    "autonomous_execution": False,
    "operator_bypass": False,
    "hidden_intent_claim_authority": False,
}

_VALID_P101_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchShadowStabilizationReceipt.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P101_RESEARCH_SHADOW_STABILIZATION_RECEIPT",
    "status": "SHADOW_STABILIZATION_RECEIPT_EMITTED",
    "upstream_lane_id": "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD",
    "upstream_operator_decision_status": "OPERATOR_DECISION_RECORD_EMITTED",
    "stabilization_receipt_status": "EMITTED",
    "stabilized_candidates": [
        "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
        "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
    ],
    "held_candidates": ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"],
    "repair_candidates": ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"],
    "rejected_candidates": ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"],
    "stabilization_window_requirements": {
        "minimum_shadow_cycles_required": 12,
        "authority_lock_invariance_required": True,
        "deterministic_replay_required": True,
        "not_computable_failure_proof_required": True,
        "aal_viz_projection_only_required": True,
        "operator_review_required": True,
        "no_runtime_mutation": True,
        "no_canon_promotion": True,
        "no_forecast_weight_mutation": True,
    },
    "authority_locks": dict(_AUTHORITY_LOCKS),
    "recommended_next_lane": "P102_RESEARCH_STABILIZATION_WINDOW_MONITOR",
    "recommended_next_lane_reason": "Proceed to P102.",
    "not_computable_reasons": [],
    "provenance": {"source": "p100"},
}


def _all_true_proof_flags() -> dict[str, bool]:
    return {flag: True for flag in REQUIRED_PROOF_FLAGS}


def _complete_observations() -> dict[str, Any]:
    return {
        "candidate_observations": {
            candidate_id: {
                "current_shadow_cycles_observed": 12,
                "proof_flags": _all_true_proof_flags(),
            }
            for candidate_id in _VALID_P101_PACKET["stabilized_candidates"]
        }
    }


def test_deterministic_output_across_repeated_runs() -> None:
    observations = _complete_observations()
    first = build_research_stabilization_window_monitor(
        p101_packet=_VALID_P101_PACKET,
        observations_packet=observations,
    )
    second = build_research_stabilization_window_monitor(
        p101_packet=_VALID_P101_PACKET,
        observations_packet=observations,
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_p101_missing_returns_not_computable() -> None:
    packet = build_research_stabilization_window_monitor(p101_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p101_packet_missing" in packet["not_computable_reasons"]


def test_malformed_p101_returns_not_computable() -> None:
    packet = build_research_stabilization_window_monitor(
        p101_packet="bad"  # type: ignore[arg-type]
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p101_packet_malformed" in r for r in packet["not_computable_reasons"])


def test_wrong_chain_p101_returns_not_computable() -> None:
    packet = build_research_stabilization_window_monitor(
        p101_packet={**_VALID_P101_PACKET, "recommended_next_lane": "P999_WRONG"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p101_recommendation_chain_mismatch" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_non_emitted_non_pass_p101_returns_not_computable() -> None:
    packet = build_research_stabilization_window_monitor(
        p101_packet={
            **_VALID_P101_PACKET,
            "status": "NOT_COMPUTABLE",
            "stabilization_receipt_status": "NOT_COMPUTABLE",
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p101_status_not_emitted_or_rejected_drift" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_no_stabilized_candidates_returns_not_computable() -> None:
    packet = build_research_stabilization_window_monitor(
        p101_packet={**_VALID_P101_PACKET, "stabilized_candidates": []}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["not_computable_reasons"] == ["p101_no_stabilized_candidates"]


def test_p101_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_stabilization_window_monitor(
        p101_packet={
            **_VALID_P101_PACKET,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "stabilization_receipt_status": "REJECTED_AUTHORITY_DRIFT",
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"
    assert packet["stabilization_window_monitor_status"] == "REJECTED_AUTHORITY_DRIFT"


def test_authority_lock_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_stabilization_window_monitor(
        p101_packet={
            **_VALID_P101_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS, "runtime_mutation": True},
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_default_observations_recommend_continue() -> None:
    packet = build_research_stabilization_window_monitor(p101_packet=_VALID_P101_PACKET)
    statuses = {item["stabilization_window_status"] for item in packet["candidate_window_statuses"]}
    assert statuses.issubset({"WINDOW_NOT_STARTED", "WINDOW_IN_PROGRESS"})
    assert packet["recommended_next_lane"] == "P102_RESEARCH_STABILIZATION_WINDOW_MONITOR_CONTINUE"


def test_complete_observations_recommend_p103() -> None:
    packet = build_research_stabilization_window_monitor(
        p101_packet=_VALID_P101_PACKET,
        observations_packet=_complete_observations(),
    )
    assert all(
        item["stabilization_window_status"] == "WINDOW_COMPLETE"
        for item in packet["candidate_window_statuses"]
    )
    assert packet["recommended_next_lane"] == "P103_RESEARCH_SHADOW_REPLAY_AUDIT"


def test_missing_proof_flags_block_p103_and_mark_blocked() -> None:
    observations = _complete_observations()
    candidate_id = _VALID_P101_PACKET["stabilized_candidates"][0]
    observations["candidate_observations"][candidate_id]["proof_flags"] = {
        **_all_true_proof_flags(),
        "operator_review_observed": False,
    }
    packet = build_research_stabilization_window_monitor(
        p101_packet=_VALID_P101_PACKET,
        observations_packet=observations,
    )
    blocked = [
        item
        for item in packet["candidate_window_statuses"]
        if item["candidate_id"] == candidate_id
    ][0]
    assert blocked["stabilization_window_status"] == "WINDOW_BLOCKED_MISSING_PROOFS"
    assert "operator_review_observed" in blocked["missing_proof_flags"]
    assert packet["recommended_next_lane"] == "P102_RESEARCH_STABILIZATION_WINDOW_MONITOR_CONTINUE"


def test_held_repair_rejected_candidates_preserved_separately() -> None:
    packet = build_research_stabilization_window_monitor(
        p101_packet=_VALID_P101_PACKET,
        observations_packet=_complete_observations(),
    )
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]
    assert packet["repair_candidates"] == ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"]
    assert packet["rejected_candidates"] == ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"]


def test_all_authority_locks_remain_false() -> None:
    emitted = build_research_stabilization_window_monitor(
        p101_packet=_VALID_P101_PACKET,
        observations_packet=_complete_observations(),
    )
    blocked = build_research_stabilization_window_monitor(p101_packet=None)
    rejected = build_research_stabilization_window_monitor(
        p101_packet={
            **_VALID_P101_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS, "canon_promotion": True},
        }
    )
    assert emitted["authority_locks"] == _AUTHORITY_LOCKS
    assert blocked["authority_locks"] == _AUTHORITY_LOCKS
    assert rejected["authority_locks"] == _AUTHORITY_LOCKS


def test_recommended_next_lane_is_p103_only_when_all_candidates_meet_gate() -> None:
    complete_packet = build_research_stabilization_window_monitor(
        p101_packet=_VALID_P101_PACKET,
        observations_packet=_complete_observations(),
    )
    assert complete_packet["recommended_next_lane"] == "P103_RESEARCH_SHADOW_REPLAY_AUDIT"

    incomplete_observations = _complete_observations()
    candidate_id = _VALID_P101_PACKET["stabilized_candidates"][1]
    incomplete_observations["candidate_observations"][candidate_id][
        "current_shadow_cycles_observed"
    ] = 11
    blocked_packet = build_research_stabilization_window_monitor(
        p101_packet=_VALID_P101_PACKET,
        observations_packet=incomplete_observations,
    )
    assert blocked_packet["recommended_next_lane"] != "P103_RESEARCH_SHADOW_REPLAY_AUDIT"


def test_schema_validates_emitted_packet() -> None:
    schema = json.loads(
        Path(
            "contracts/canon/research_stabilization_window_monitor.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    packet = build_research_stabilization_window_monitor(
        p101_packet=_VALID_P101_PACKET,
        observations_packet=_complete_observations(),
    )
    validate(packet, schema)


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_stabilization_window_monitor" / "latest.json"
    observations = _complete_observations()
    first = run_research_stabilization_window_monitor.run(
        p101_packet=_VALID_P101_PACKET,
        observations_packet=observations,
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_research_stabilization_window_monitor.run(
        p101_packet=_VALID_P101_PACKET,
        observations_packet=observations,
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_writer_final_newline(tmp_path: Path) -> None:
    packet = build_research_stabilization_window_monitor(
        p101_packet=_VALID_P101_PACKET,
        observations_packet=_complete_observations(),
    )
    out_path = tmp_path / "monitor.json"
    write_research_stabilization_window_monitor(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")


def test_load_json_packet_and_parse_args(tmp_path: Path) -> None:
    assert str(P101_DEFAULT_PATH) == "out/research_shadow_stabilization_receipt/latest.json"

    missing = _load_json_packet(tmp_path / "missing.json")
    assert missing is None

    bad_path = tmp_path / "bad.json"
    bad_path.write_text("{not json", encoding="utf-8")
    assert _load_json_packet(bad_path) is None

    payload_path = tmp_path / "packet.json"
    payload_path.write_text(json.dumps(_VALID_P101_PACKET), encoding="utf-8")
    loaded = _load_json_packet(payload_path)
    assert isinstance(loaded, dict)
    assert loaded["artifact_type"] == "ResearchShadowStabilizationReceipt.v1"

    default_args = _parse_args([])
    assert default_args.p101_path == "out/research_shadow_stabilization_receipt/latest.json"
    assert default_args.observations_path is None

    obs = str(tmp_path / "observations.json")
    custom_args = _parse_args(["--p101-path", str(payload_path), "--observations-path", obs])
    assert custom_args.p101_path == str(payload_path)
    assert custom_args.observations_path == obs
