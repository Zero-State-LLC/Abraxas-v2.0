from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from core.research_boundary_decay_analysis import (
    build_research_boundary_decay_analysis,
    write_research_boundary_decay_analysis,
)
from scripts import run_research_boundary_decay_analysis
from scripts.run_research_boundary_decay_analysis import (
    P103_DEFAULT_PATH,
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

_REPLAY_PASS_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P103_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchShadowReplayAudit.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P103_RESEARCH_SHADOW_REPLAY_AUDIT",
    "status": "SHADOW_REPLAY_AUDIT_EMITTED",
    "upstream_lane_id": "P102_RESEARCH_STABILIZATION_WINDOW_MONITOR",
    "upstream_stabilization_window_monitor_status": "STABILIZATION_WINDOW_MONITOR_EMITTED",
    "shadow_replay_audit_status": "EMITTED",
    "stabilized_candidates": list(_REPLAY_PASS_CANDIDATES),
    "held_candidates": ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"],
    "repair_candidates": ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"],
    "rejected_candidates": ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"],
    "audited_candidates": list(_REPLAY_PASS_CANDIDATES),
    "replay_pass_candidates": list(_REPLAY_PASS_CANDIDATES),
    "replay_fail_candidates": [],
    "replay_incomplete_candidates": [],
    "candidate_replay_statuses": [],
    "missing_replay_requirements": {},
    "authority_locks": dict(_AUTHORITY_LOCKS),
    "recommended_next_lane": "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS",
    "recommended_next_lane_reason": "Proceed to P104.",
    "not_computable_reasons": [],
    "provenance": {"source": "p102"},
}


def _stable_observations() -> dict[str, Any]:
    return {
        "candidate_boundary_observations": {
            candidate_id: {
                "boundary_definition_present": True,
                "overlap_with_other_candidates": [],
                "semantic_drift_score": 0.1,
                "authority_boundary_leakage_observed": False,
                "forecast_boundary_leakage_observed": False,
                "runtime_boundary_leakage_observed": False,
                "aal_viz_projection_only_observed": True,
                "operator_review_observed": True,
                "decay_window_cycles_observed": 3,
            }
            for candidate_id in _REPLAY_PASS_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_boundary_decay_analysis.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


def test_deterministic_output_across_repeated_runs() -> None:
    observations = _stable_observations()
    first = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
    )
    second = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_schema_validates_representative_stable_packet() -> None:
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=_stable_observations(),
    )
    validate(packet, _schema())


def test_schema_validates_representative_continue_packet() -> None:
    packet = build_research_boundary_decay_analysis(p103_packet=_VALID_P103_PACKET)
    validate(packet, _schema())


def test_schema_validates_representative_failure_packet() -> None:
    packet = build_research_boundary_decay_analysis(p103_packet=None)
    validate(packet, _schema())


def test_p103_missing_returns_not_computable() -> None:
    packet = build_research_boundary_decay_analysis(p103_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p103_packet_missing" in packet["not_computable_reasons"]


def test_malformed_p103_returns_not_computable() -> None:
    packet = build_research_boundary_decay_analysis(
        p103_packet="bad"  # type: ignore[arg-type]
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p103_packet_malformed" in reason for reason in packet["not_computable_reasons"])


def test_wrong_chain_p103_returns_not_computable() -> None:
    packet = build_research_boundary_decay_analysis(
        p103_packet={**_VALID_P103_PACKET, "recommended_next_lane": "P999_WRONG"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p103_recommendation_chain_mismatch" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_non_emitted_non_pass_p103_returns_not_computable() -> None:
    packet = build_research_boundary_decay_analysis(
        p103_packet={
            **_VALID_P103_PACKET,
            "status": "NOT_COMPUTABLE",
            "shadow_replay_audit_status": "NOT_COMPUTABLE",
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p103_status_not_emitted_or_rejected_drift" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_p103_without_p104_recommendation_never_recommends_p105() -> None:
    packet = build_research_boundary_decay_analysis(
        p103_packet={
            **_VALID_P103_PACKET,
            "recommended_next_lane": "P103_RESEARCH_SHADOW_REPLAY_AUDIT_CONTINUE",
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] != "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER"


def test_no_replay_pass_candidates_returns_not_computable() -> None:
    packet = build_research_boundary_decay_analysis(
        p103_packet={**_VALID_P103_PACKET, "replay_pass_candidates": []}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["not_computable_reasons"] == ["p103_no_replay_pass_candidates"]


def test_p103_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_boundary_decay_analysis(
        p103_packet={
            **_VALID_P103_PACKET,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "shadow_replay_audit_status": "REJECTED_AUTHORITY_DRIFT",
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"
    assert packet["boundary_decay_analysis_status"] == "REJECTED_AUTHORITY_DRIFT"


def test_boundary_observation_authority_leakage_returns_rejected_authority_drift() -> None:
    observations = _stable_observations()
    observations["candidate_boundary_observations"][_REPLAY_PASS_CANDIDATES[0]][
        "authority_boundary_leakage_observed"
    ] = True
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_boundary_observation_forecast_leakage_returns_rejected_authority_drift() -> None:
    observations = _stable_observations()
    observations["candidate_boundary_observations"][_REPLAY_PASS_CANDIDATES[0]][
        "forecast_boundary_leakage_observed"
    ] = True
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_boundary_observation_runtime_leakage_returns_rejected_authority_drift() -> None:
    observations = _stable_observations()
    observations["candidate_boundary_observations"][_REPLAY_PASS_CANDIDATES[0]][
        "runtime_boundary_leakage_observed"
    ] = True
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_default_missing_boundary_observations_recommend_continue() -> None:
    packet = build_research_boundary_decay_analysis(p103_packet=_VALID_P103_PACKET)
    assert packet["recommended_next_lane"] == "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS_CONTINUE"
    for candidate_status in packet["candidate_boundary_statuses"]:
        assert candidate_status["boundary_decay_status"] == "BOUNDARY_DECAY_NOT_OBSERVED"


def test_stable_observations_for_every_analyzed_candidate_recommend_p105() -> None:
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=_stable_observations(),
    )
    assert packet["recommended_next_lane"] == "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER"
    assert packet["boundary_decay_analysis_status"] == "BOUNDARY_STABLE"


def test_semantic_drift_score_above_threshold_produces_decay_detected_and_blocks_p105() -> None:
    observations = _stable_observations()
    observations["candidate_boundary_observations"][_REPLAY_PASS_CANDIDATES[0]][
        "semantic_drift_score"
    ] = 0.151
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] != "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER"
    blocked = next(
        status
        for status in packet["candidate_boundary_statuses"]
        if status["candidate_id"] == _REPLAY_PASS_CANDIDATES[0]
    )
    assert blocked["boundary_decay_status"] == "BOUNDARY_DECAY_DETECTED"


def test_missing_boundary_definition_present_blocks_p105() -> None:
    observations = _stable_observations()
    observations["candidate_boundary_observations"][_REPLAY_PASS_CANDIDATES[0]].pop(
        "boundary_definition_present"
    )
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] == "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS_CONTINUE"


def test_missing_aal_viz_projection_only_observed_blocks_p105() -> None:
    observations = _stable_observations()
    observations["candidate_boundary_observations"][_REPLAY_PASS_CANDIDATES[0]].pop(
        "aal_viz_projection_only_observed"
    )
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] == "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS_CONTINUE"


def test_missing_operator_review_observed_blocks_p105() -> None:
    observations = _stable_observations()
    observations["candidate_boundary_observations"][_REPLAY_PASS_CANDIDATES[0]].pop(
        "operator_review_observed"
    )
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] == "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS_CONTINUE"


def test_decay_window_cycles_below_threshold_blocks_p105() -> None:
    observations = _stable_observations()
    observations["candidate_boundary_observations"][_REPLAY_PASS_CANDIDATES[0]][
        "decay_window_cycles_observed"
    ] = 2
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] == "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS_CONTINUE"


def test_conflicting_overlap_blocks_p105() -> None:
    observations = _stable_observations()
    observations["candidate_boundary_observations"][_REPLAY_PASS_CANDIDATES[0]][
        "overlap_with_other_candidates"
    ] = ["conflicting_overlap"]
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] == "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS_CONTINUE"


def test_advisory_non_conflicting_overlap_does_not_block_p105() -> None:
    observations = _stable_observations()
    observations["candidate_boundary_observations"][_REPLAY_PASS_CANDIDATES[0]][
        "overlap_with_other_candidates"
    ] = ["advisory_non_conflicting"]
    observations["candidate_boundary_observations"][_REPLAY_PASS_CANDIDATES[1]][
        "overlap_with_other_candidates"
    ] = [{"classification": "advisory_non_conflicting"}]
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] == "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER"


def test_held_repair_rejected_candidates_are_preserved_separately() -> None:
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=_stable_observations(),
    )
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]
    assert packet["repair_candidates"] == [
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"
    ]
    assert packet["rejected_candidates"] == [
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"
    ]


def test_only_replay_pass_candidates_are_analyzed() -> None:
    packet = build_research_boundary_decay_analysis(
        p103_packet={
            **_VALID_P103_PACKET,
            "replay_pass_candidates": [_REPLAY_PASS_CANDIDATES[0]],
        },
        boundary_observations_packet=_stable_observations(),
    )
    analyzed_ids = {status["candidate_id"] for status in packet["candidate_boundary_statuses"]}
    assert analyzed_ids == {_REPLAY_PASS_CANDIDATES[0]}
    assert "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER" not in analyzed_ids


def test_all_authority_locks_remain_false() -> None:
    emitted = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=_stable_observations(),
    )
    blocked = build_research_boundary_decay_analysis(p103_packet=None)
    rejected = build_research_boundary_decay_analysis(
        p103_packet={
            **_VALID_P103_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS, "runtime_mutation": True},
        }
    )
    assert emitted["authority_locks"] == _AUTHORITY_LOCKS
    assert blocked["authority_locks"] == _AUTHORITY_LOCKS
    assert rejected["authority_locks"] == _AUTHORITY_LOCKS


def test_packet_hash_is_deterministic_and_excludes_itself() -> None:
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=_stable_observations(),
    )
    payload_without_hash = {k: v for k, v in packet.items() if k != "packet_hash"}
    canonical = json.dumps(
        payload_without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert packet["packet_hash"] == expected_hash


def test_output_writer_emits_canonical_json_with_trailing_newline(tmp_path: Path) -> None:
    packet = build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=_stable_observations(),
    )
    out_path = tmp_path / "analysis.json"
    write_research_boundary_decay_analysis(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    loaded = json.loads(text)
    assert loaded["packet_hash"] == packet["packet_hash"]


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_boundary_decay_analysis" / "latest.json"
    observations = _stable_observations()
    first = run_research_boundary_decay_analysis.run(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_research_boundary_decay_analysis.run(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=observations,
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_runner_supports_p103_path_and_boundary_observations_path(tmp_path: Path) -> None:
    assert str(P103_DEFAULT_PATH) == "out/research_shadow_replay_audit/latest.json"

    missing = _load_json_packet(tmp_path / "missing.json")
    assert missing is None

    bad_path = tmp_path / "bad.json"
    bad_path.write_text("{not json", encoding="utf-8")
    assert _load_json_packet(bad_path) is None

    payload_path = tmp_path / "p103.json"
    payload_path.write_text(json.dumps(_VALID_P103_PACKET), encoding="utf-8")
    loaded = _load_json_packet(payload_path)
    assert isinstance(loaded, dict)
    assert loaded["artifact_type"] == "ResearchShadowReplayAudit.v1"

    default_args = _parse_args([])
    assert default_args.p103_path == "out/research_shadow_replay_audit/latest.json"
    assert default_args.boundary_observations_path is None

    observations_path = str(tmp_path / "observations.json")
    custom_args = _parse_args(
        [
            "--p103-path",
            str(payload_path),
            "--boundary-observations-path",
            observations_path,
        ]
    )
    assert custom_args.p103_path == str(payload_path)
    assert custom_args.boundary_observations_path == observations_path


def test_generated_out_artifacts_remain_untouched() -> None:
    validation_path = Path("out/validation/latest.json")
    aal_viz_path = Path("out/projections/aal_viz.latest.json")

    validation_before = validation_path.read_bytes() if validation_path.exists() else None
    aal_viz_before = aal_viz_path.read_bytes() if aal_viz_path.exists() else None

    build_research_boundary_decay_analysis(
        p103_packet=_VALID_P103_PACKET,
        boundary_observations_packet=_stable_observations(),
    )

    if validation_before is not None:
        assert validation_path.read_bytes() == validation_before
    if aal_viz_before is not None:
        assert aal_viz_path.read_bytes() == aal_viz_before
