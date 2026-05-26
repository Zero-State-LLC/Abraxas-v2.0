from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.research_shadow_stabilization_receipt import (
    ALLOWED_DECISIONS,
    FORBIDDEN_DECISIONS,
    build_research_shadow_stabilization_receipt,
    write_research_shadow_stabilization_receipt,
)
from scripts import run_research_shadow_stabilization_receipt
from scripts.run_research_shadow_stabilization_receipt import _load_p100_packet

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

_VALID_P100_PACKET: dict[str, object] = {
    "artifact_type": "ResearchOperatorStabilizationDecisionRecord.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD",
    "status": "OPERATOR_DECISION_RECORD_EMITTED",
    "upstream_lane_id": "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN",
    "upstream_conflict_scan_status": "PASS_CLEAN",
    "operator_decision_record_status": "EMITTED",
    "candidate_decisions": {
        "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER": "hold",
        "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER": "advance_to_shadow_stabilization",
        "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER": "hold",
        "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER": "advance_to_shadow_stabilization",
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER": "hold",
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER": "advance_to_shadow_stabilization",
    },
    "stabilized_candidates": [],
    "held_candidates": [
        "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER",
        "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER",
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER",
    ],
    "repair_candidates": [],
    "rejected_candidates": [],
    "unresolved_conflicts": [],
    "authority_locks": dict(_AUTHORITY_LOCKS),
    "recommended_next_lane": "P101_RESEARCH_SHADOW_STABILIZATION_RECEIPT",
    "recommended_next_lane_reason": "At least one candidate advances.",
    "not_computable_reasons": [],
    "provenance": {
        "source": "p99_research_cross_drop_conflict_scan",
        "mapping_method": "deterministic_operator_decision_record",
    },
}


def test_deterministic_output_across_repeated_runs() -> None:
    first = build_research_shadow_stabilization_receipt(p100_packet=_VALID_P100_PACKET)
    second = build_research_shadow_stabilization_receipt(p100_packet=_VALID_P100_PACKET)
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_p100_missing_returns_not_computable() -> None:
    packet = build_research_shadow_stabilization_receipt(p100_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p100_packet_missing" in packet["not_computable_reasons"]


def test_p100_malformed_returns_not_computable() -> None:
    packet = build_research_shadow_stabilization_receipt(p100_packet="bad")  # type: ignore[arg-type]
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p100_packet_malformed" in reason for reason in packet["not_computable_reasons"])


def test_wrong_chain_p100_returns_not_computable() -> None:
    packet = build_research_shadow_stabilization_receipt(
        p100_packet={**_VALID_P100_PACKET, "recommended_next_lane": "P999_WRONG"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p100_recommendation_chain_mismatch" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_non_emitted_p100_returns_not_computable() -> None:
    packet = build_research_shadow_stabilization_receipt(
        p100_packet={
            **_VALID_P100_PACKET,
            "status": "NOT_COMPUTABLE",
            "operator_decision_record_status": "NOT_COMPUTABLE",
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p100_status_not_emitted_or_rejected" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_no_advanced_candidates_returns_not_computable() -> None:
    packet = build_research_shadow_stabilization_receipt(
        p100_packet={
            **_VALID_P100_PACKET,
            "candidate_decisions": {
                "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER": "hold",
                "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER": "repair",
                "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER": "hold",
                "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER": "hold",
                "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER": "hold",
                "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER": "reject",
            },
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["not_computable_reasons"] == ["p100_no_shadow_stabilization_candidates"]


def test_p100_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_shadow_stabilization_receipt(
        p100_packet={
            **_VALID_P100_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS, "runtime_mutation": True},
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"
    assert packet["stabilized_candidates"] == []


def test_forbidden_decisions_are_rejected() -> None:
    packet = build_research_shadow_stabilization_receipt(
        p100_packet={
            **_VALID_P100_PACKET,
            "candidate_decisions": {
                **_VALID_P100_PACKET["candidate_decisions"],  # type: ignore[index]
                "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER": "runtime_mutate",
            },
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p100_forbidden_candidate_decision:DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER:runtime_mutate"
        == reason
        for reason in packet["not_computable_reasons"]
    )


def test_advanced_candidates_become_stabilized_candidates() -> None:
    packet = build_research_shadow_stabilization_receipt(p100_packet=_VALID_P100_PACKET)
    assert packet["status"] == "SHADOW_STABILIZATION_RECEIPT_EMITTED"
    assert packet["stabilized_candidates"] == [
        "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
        "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER",
    ]


def test_held_repair_and_rejected_candidates_are_recorded_separately() -> None:
    packet = build_research_shadow_stabilization_receipt(
        p100_packet={
            **_VALID_P100_PACKET,
            "candidate_decisions": {
                "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER": "hold",
                "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER": "advance_to_shadow_stabilization",
                "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER": "hold",
                "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER": "advance_to_shadow_stabilization",
                "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER": "repair",
                "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER": "reject",
            },
        }
    )
    assert packet["held_candidates"] == [
        "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER",
        "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER",
    ]
    assert packet["repair_candidates"] == [
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"
    ]
    assert packet["rejected_candidates"] == [
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"
    ]


def test_all_authority_locks_remain_false() -> None:
    emitted_packet = build_research_shadow_stabilization_receipt(
        p100_packet=_VALID_P100_PACKET
    )
    blocked_packet = build_research_shadow_stabilization_receipt(p100_packet=None)
    rejected_packet = build_research_shadow_stabilization_receipt(
        p100_packet={
            **_VALID_P100_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS, "canon_promotion": True},
        }
    )
    assert emitted_packet["authority_locks"] == _AUTHORITY_LOCKS
    assert blocked_packet["authority_locks"] == _AUTHORITY_LOCKS
    assert rejected_packet["authority_locks"] == _AUTHORITY_LOCKS


def test_recommended_next_lane_is_p102_only_when_candidates_stabilize_without_drift() -> None:
    emitted_packet = build_research_shadow_stabilization_receipt(
        p100_packet=_VALID_P100_PACKET
    )
    assert emitted_packet["recommended_next_lane"] == "P102_RESEARCH_STABILIZATION_WINDOW_MONITOR"

    rejected_packet = build_research_shadow_stabilization_receipt(
        p100_packet={
            **_VALID_P100_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS, "operator_bypass": True},
        }
    )
    assert rejected_packet["recommended_next_lane"] == "NOT_COMPUTABLE"

    blocked_packet = build_research_shadow_stabilization_receipt(
        p100_packet={
            **_VALID_P100_PACKET,
            "candidate_decisions": {
                "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER": "hold",
                "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER": "hold",
                "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER": "hold",
                "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER": "repair",
                "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER": "hold",
                "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER": "reject",
            },
        }
    )
    assert blocked_packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_accepts_shadow_stabilization_compatibility_from_active_p100_shape() -> None:
    compat_packet = {
        "artifact_type": "ResearchOperatorStabilizationDecisionRecord.v1",
        "canonical_status": "ADVISORY_ONLY",
        "advisory_only": True,
        "projection_only": True,
        "lane_id": "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD",
        "status": "PASS",
        "stabilization_decision_status": "PASS",
        "recommended_next_lane": "P101_RESEARCH_CANARY_AUTHORIZATION_PACKET_DRAFT",
        "shadow_stabilization_compatibility": {
            "compatibility_status": "EMITTED",
            "target_lane_id": "P101_RESEARCH_SHADOW_STABILIZATION_RECEIPT",
            "operator_decision_record_status": "EMITTED",
            "candidate_decisions": {
                candidate_id: {
                    "candidate_id": candidate_id,
                    "decision": "advance_to_shadow_stabilization",
                    "decision_scope": "shadow_stabilization_compatibility_only",
                    "authority_class": "NON_OPERATIVE",
                    "status": "DECISION_EMITTED",
                }
                for candidate_id in _VALID_P100_PACKET["candidate_decisions"]  # type: ignore[index]
            },
            "not_computable_reasons": [],
        },
        "authority_locks": dict(_AUTHORITY_LOCKS),
    }
    compat_packet["authority_locks"] = {
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "forecast_influence": False,
        "execution_authority": False,
        "repair_execution_authority": False,
        "regeneration_execution_authority": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "activation_approved": False,
        "authorization_granted": False,
        "canonical_status": "ADVISORY_ONLY",
    }
    packet = build_research_shadow_stabilization_receipt(p100_packet=compat_packet)
    assert packet["status"] == "SHADOW_STABILIZATION_RECEIPT_EMITTED"
    assert packet["stabilization_receipt_status"] == "EMITTED"
    assert packet["recommended_next_lane"] == "P102_RESEARCH_STABILIZATION_WINDOW_MONITOR"


def test_compatibility_shape_rejects_true_forbidden_current_authority_key() -> None:
    compat_packet = {
        "artifact_type": "ResearchOperatorStabilizationDecisionRecord.v1",
        "lane_id": "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD",
        "status": "PASS",
        "shadow_stabilization_compatibility": {
            "compatibility_status": "EMITTED",
            "target_lane_id": "P101_RESEARCH_SHADOW_STABILIZATION_RECEIPT",
            "operator_decision_record_status": "EMITTED",
            "candidate_decisions": {
                candidate_id: {"decision": "advance_to_shadow_stabilization"}
                for candidate_id in _VALID_P100_PACKET["candidate_decisions"]  # type: ignore[index]
            },
            "not_computable_reasons": [],
        },
        "authority_locks": {
            "production_activation": False,
            "canon_promotion": False,
            "scheduler_mutation": False,
            "runtime_authority": True,
            "forecast_influence": False,
            "execution_authority": False,
            "repair_execution_authority": False,
            "regeneration_execution_authority": False,
            "token_minting_allowed": False,
            "valid_for_execution": False,
            "activation_approved": False,
            "authorization_granted": False,
            "canonical_status": "ADVISORY_ONLY",
        },
    }
    packet = build_research_shadow_stabilization_receipt(p100_packet=compat_packet)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p100_authority_lock_not_false:runtime_authority:True" == r for r in packet["not_computable_reasons"])


def test_compatibility_shape_rejects_non_emitted_compatibility_authority_implication() -> None:
    compat_packet = {
        "artifact_type": "ResearchOperatorStabilizationDecisionRecord.v1",
        "lane_id": "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD",
        "status": "PASS",
        "shadow_stabilization_compatibility": {
            "compatibility_status": "NOT_COMPUTABLE",
            "target_lane_id": "P101_RESEARCH_SHADOW_STABILIZATION_RECEIPT",
            "operator_decision_record_status": "EMITTED",
            "candidate_decisions": {},
            "not_computable_reasons": ["blocked"],
        },
        "authority_locks": dict(_AUTHORITY_LOCKS),
    }
    packet = build_research_shadow_stabilization_receipt(p100_packet=compat_packet)
    assert packet["status"] == "NOT_COMPUTABLE"


def test_schema_validates_emitted_packet() -> None:
    schema = json.loads(
        Path(
            "contracts/canon/research_shadow_stabilization_receipt.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    packet = build_research_shadow_stabilization_receipt(p100_packet=_VALID_P100_PACKET)
    validate(packet, schema)


def test_schema_locks_authority_fields_false() -> None:
    schema = json.loads(
        Path(
            "contracts/canon/research_shadow_stabilization_receipt.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    for field in _AUTHORITY_LOCKS:
        assert schema["properties"]["authority_locks"]["properties"][field]["const"] is False


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_shadow_stabilization_receipt" / "latest.json"
    first = run_research_shadow_stabilization_receipt.run(
        p100_packet=_VALID_P100_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")

    second = run_research_shadow_stabilization_receipt.run(
        p100_packet=_VALID_P100_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")

    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_writer_final_newline(tmp_path: Path) -> None:
    packet = build_research_shadow_stabilization_receipt(p100_packet=_VALID_P100_PACKET)
    out_path = tmp_path / "research_shadow_stabilization_receipt_test.json"
    write_research_shadow_stabilization_receipt(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")


def test_load_p100_packet_missing_returns_none(tmp_path: Path) -> None:
    assert _load_p100_packet(tmp_path / "missing.json") is None


def test_load_p100_packet_malformed_returns_none(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert _load_p100_packet(bad) is None


def test_load_p100_packet_non_dict_returns_none(tmp_path: Path) -> None:
    arr = tmp_path / "arr.json"
    arr.write_text("[1, 2]", encoding="utf-8")
    assert _load_p100_packet(arr) is None


def test_load_p100_packet_valid_returns_dict(tmp_path: Path) -> None:
    packet_path = tmp_path / "p100.json"
    packet_path.write_text(json.dumps(_VALID_P100_PACKET), encoding="utf-8")
    loaded = _load_p100_packet(packet_path)
    assert isinstance(loaded, dict)
    assert loaded["artifact_type"] == "ResearchOperatorStabilizationDecisionRecord.v1"


def test_p100_default_path_constant() -> None:
    from scripts.run_research_shadow_stabilization_receipt import P100_DEFAULT_PATH

    assert (
        str(P100_DEFAULT_PATH)
        == "out/research_operator_stabilization_decision_record/latest.json"
    )


def test_parse_args_default_and_custom_p100_path(tmp_path: Path) -> None:
    from scripts.run_research_shadow_stabilization_receipt import _parse_args

    default_args = _parse_args([])
    assert default_args.p100_path == "out/research_operator_stabilization_decision_record/latest.json"

    custom = str(tmp_path / "custom_p100.json")
    custom_args = _parse_args(["--p100-path", custom])
    assert custom_args.p100_path == custom


def test_required_output_fields_are_present() -> None:
    packet = build_research_shadow_stabilization_receipt(p100_packet=_VALID_P100_PACKET)
    required_fields = {
        "artifact_type",
        "canonical_status",
        "advisory_only",
        "projection_only",
        "lane_id",
        "status",
        "upstream_lane_id",
        "upstream_operator_decision_status",
        "stabilization_receipt_status",
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "stabilization_window_requirements",
        "authority_locks",
        "recommended_next_lane",
        "recommended_next_lane_reason",
        "not_computable_reasons",
        "provenance",
        "packet_hash",
    }
    assert required_fields.issubset(packet.keys())


def test_allowed_and_forbidden_decisions_are_partitioned() -> None:
    assert ALLOWED_DECISIONS == {
        "hold",
        "repair",
        "reject",
        "advance_to_shadow_stabilization",
    }
    assert FORBIDDEN_DECISIONS.isdisjoint(ALLOWED_DECISIONS)
