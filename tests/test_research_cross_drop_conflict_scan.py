from __future__ import annotations

import json
from pathlib import Path

from core.research_cross_drop_conflict_scan import (
    BOUNDARY_RESOLUTION_NOTES,
    build_research_cross_drop_conflict_scan,
    write_research_cross_drop_conflict_scan,
)
from scripts import run_research_cross_drop_conflict_scan
from scripts.run_research_cross_drop_conflict_scan import _load_p98_packet

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


def _valid_p98_packet() -> dict[str, object]:
    return {
        "artifact_type": "ResearchShadowStabilizationProofPlan.v1",
        "lane_id": "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN",
        "status": "PASS",
        "recommended_next_lane": "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN",
        "authority_locks": dict(_AUTHORITY_LOCKS),
        "drop_candidates": [
            {
                "drop_id": "DROP006",
                "candidate_id": "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_SPEC",
                "schema_name": "BehavioralIntentGraph.v1",
                "rune_id": "RUNE_INTENT_GRAPH",
                "metric_id": "METRIC_DEPENDENCY_STABILITY",
                "target_subsystem": "intent-graph",
            },
            {
                "drop_id": "DROP007",
                "candidate_id": "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_SPEC",
                "schema_name": "SituationContinuityFrame.v1",
                "rune_id": "RUNE_SITUATION_RUNTIME",
                "metric_id": "METRIC_PROACTIVE_TRACE_COVERAGE",
                "target_subsystem": "situation-runtime",
            },
        ],
    }


def test_deterministic_output_across_repeated_runs() -> None:
    first = build_research_cross_drop_conflict_scan(p98_packet=_valid_p98_packet())
    second = build_research_cross_drop_conflict_scan(p98_packet=_valid_p98_packet())
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_p98_missing_returns_not_computable() -> None:
    packet = build_research_cross_drop_conflict_scan(p98_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p98_packet_missing" in packet["not_computable_reasons"]


def test_p98_malformed_returns_not_computable() -> None:
    packet = build_research_cross_drop_conflict_scan(p98_packet="invalid")  # type: ignore[arg-type]
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p98_packet_malformed" in reason for reason in packet["not_computable_reasons"])


def test_p98_list_payload_returns_not_computable() -> None:
    packet = build_research_cross_drop_conflict_scan(p98_packet=[1, 2, 3])  # type: ignore[arg-type]
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p98_packet_malformed" in reason for reason in packet["not_computable_reasons"])


def test_p98_non_pass_returns_not_computable() -> None:
    p98 = _valid_p98_packet()
    p98["status"] = "FAIL"
    packet = build_research_cross_drop_conflict_scan(p98_packet=p98)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p98_status_not_pass" in reason for reason in packet["not_computable_reasons"])


def test_wrong_recommendation_chain_returns_not_computable() -> None:
    p98 = _valid_p98_packet()
    p98["recommended_next_lane"] = "P101_SOMETHING_ELSE"
    packet = build_research_cross_drop_conflict_scan(p98_packet=p98)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p98_recommendation_chain_mismatch" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_missing_required_drop_candidates_returns_not_computable() -> None:
    p98 = _valid_p98_packet()
    p98["drop_candidates"] = [p98["drop_candidates"][0]]  # type: ignore[index]
    packet = build_research_cross_drop_conflict_scan(p98_packet=p98)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "missing_required_drop_candidates:DROP007" in packet["not_computable_reasons"]


def test_authority_drifted_p98_is_rejected() -> None:
    p98 = _valid_p98_packet()
    p98["authority_locks"] = {**_AUTHORITY_LOCKS, "operator_bypass": True}
    packet = build_research_cross_drop_conflict_scan(p98_packet=p98)
    assert packet["status"] in {"REJECTED_AUTHORITY_DRIFT", "NOT_COMPUTABLE"}
    assert packet["authority_drift_findings"]


def test_duplicate_candidate_ids_detected() -> None:
    p98 = _valid_p98_packet()
    p98["drop_candidates"] = [
        p98["drop_candidates"][0],
        {**p98["drop_candidates"][1], "candidate_id": "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_SPEC"},  # type: ignore[index]
    ]
    packet = build_research_cross_drop_conflict_scan(p98_packet=p98)
    assert "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_SPEC" in packet["duplicate_id_conflicts"]


def test_duplicate_schema_names_detected() -> None:
    p98 = _valid_p98_packet()
    p98["drop_candidates"] = [
        p98["drop_candidates"][0],
        {**p98["drop_candidates"][1], "schema_name": "BehavioralIntentGraph.v1"},  # type: ignore[index]
    ]
    packet = build_research_cross_drop_conflict_scan(p98_packet=p98)
    assert "BehavioralIntentGraph.v1" in packet["schema_conflicts"]


def test_advisory_semantic_overlaps_allowed_only_with_boundary_notes() -> None:
    p98 = _valid_p98_packet()
    p98["drop_candidates"] = [
        {
            **p98["drop_candidates"][0],
            "target_subsystem": "overlap-subsystem",
            "semantic_overlap_notes": ["drop006-drop007-overlap"],
        },
        {
            **p98["drop_candidates"][1],
            "target_subsystem": "overlap-subsystem",
            "semantic_overlap_notes": ["drop006-drop007-overlap"],
        },
    ]
    packet = build_research_cross_drop_conflict_scan(p98_packet=p98)
    assert packet["status"] == "PASS_WITH_ADVISORY_CONFLICTS"
    assert packet["subsystem_overlap_notes"]
    assert packet["semantic_redundancy_notes"]
    assert packet["boundary_resolution_notes"]


def test_drop006_drop007_boundary_notes_present() -> None:
    packet = build_research_cross_drop_conflict_scan(p98_packet=_valid_p98_packet())
    boundary_ids = {entry["boundary_id"] for entry in packet["boundary_resolution_notes"]}
    assert len(packet["boundary_resolution_notes"]) >= 7
    assert {
        "drop006_drop007_hidden_intent_endpoint_constraint",
        "drop006_drop007_proactive_vs_inductive_planning_trace",
        "drop006_drop007_situation_continuity_vs_behavioral_graph",
        "drop006_drop007_interleaved_intent_vs_behavioral_graph",
        "drop006_drop007_intervention_window_vs_pruning_signal",
        "drop006_drop007_coordination_threshold_vs_topology_concepts",
        "drop006_drop007_calibration_projection_vs_pse_calibration",
    }.issubset(boundary_ids)


def test_all_authority_locks_remain_false() -> None:
    packet = build_research_cross_drop_conflict_scan(p98_packet=_valid_p98_packet())
    assert packet["authority_locks"] == _AUTHORITY_LOCKS


def test_recommended_next_lane_only_on_pass_states() -> None:
    clean = build_research_cross_drop_conflict_scan(p98_packet=_valid_p98_packet())
    assert clean["status"] == "PASS_CLEAN"
    assert (
        clean["recommended_next_lane"]
        == "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD"
    )

    advisory_p98 = _valid_p98_packet()
    advisory_p98["drop_candidates"] = [
        {
            **advisory_p98["drop_candidates"][0],
            "target_subsystem": "overlap-subsystem",
            "semantic_overlap_notes": ["drop006-drop007-overlap"],
        },
        {
            **advisory_p98["drop_candidates"][1],
            "target_subsystem": "overlap-subsystem",
            "semantic_overlap_notes": ["drop006-drop007-overlap"],
        },
    ]
    advisory = build_research_cross_drop_conflict_scan(p98_packet=advisory_p98)
    assert advisory["status"] == "PASS_WITH_ADVISORY_CONFLICTS"
    assert (
        advisory["recommended_next_lane"]
        == "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD"
    )

    blocked = build_research_cross_drop_conflict_scan(p98_packet=None)
    assert blocked["recommended_next_lane"] != "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD"


def test_schema_locks_authority_fields_false() -> None:
    schema = json.loads(
        Path("contracts/canon/research_cross_drop_conflict_scan.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    for field in _AUTHORITY_LOCKS:
        assert schema["properties"]["authority_locks"]["properties"][field]["const"] is False


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_cross_drop_conflict_scan" / "latest.json"
    first = run_research_cross_drop_conflict_scan.run(
        p98_packet=_valid_p98_packet(),
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")

    second = run_research_cross_drop_conflict_scan.run(
        p98_packet=_valid_p98_packet(),
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")

    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_writer_final_newline(tmp_path: Path) -> None:
    packet = build_research_cross_drop_conflict_scan(p98_packet=_valid_p98_packet())
    out_path = tmp_path / "research_cross_drop_conflict_scan_test.json"
    write_research_cross_drop_conflict_scan(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")


def test_load_p98_packet_missing_returns_none(tmp_path: Path) -> None:
    assert _load_p98_packet(tmp_path / "missing.json") is None


def test_load_p98_packet_malformed_returns_none(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert _load_p98_packet(bad) is None


def test_load_p98_packet_non_dict_returns_none(tmp_path: Path) -> None:
    arr = tmp_path / "arr.json"
    arr.write_text("[1, 2]", encoding="utf-8")
    assert _load_p98_packet(arr) is None


def test_load_p98_packet_valid_returns_dict(tmp_path: Path) -> None:
    p = tmp_path / "p98.json"
    p.write_text(json.dumps(_valid_p98_packet()), encoding="utf-8")
    loaded = _load_p98_packet(p)
    assert isinstance(loaded, dict)
    assert loaded["artifact_type"] == "ResearchShadowStabilizationProofPlan.v1"


def test_p98_default_path_constant() -> None:
    from scripts.run_research_cross_drop_conflict_scan import P98_DEFAULT_PATH

    assert str(P98_DEFAULT_PATH) == "out/research_shadow_stabilization_proof_plan/latest.json"


def test_parse_args_default_and_custom_p98_path(tmp_path: Path) -> None:
    from scripts.run_research_cross_drop_conflict_scan import _parse_args

    default_args = _parse_args([])
    assert default_args.p98_path == "out/research_shadow_stabilization_proof_plan/latest.json"

    custom = str(tmp_path / "my_p98.json")
    custom_args = _parse_args(["--p98-path", custom])
    assert custom_args.p98_path == custom


def test_boundary_notes_constant_kept_complete() -> None:
    assert len(BOUNDARY_RESOLUTION_NOTES) == 7
