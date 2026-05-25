from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P108 is advisory-only and projection-only.
# It does NOT activate canary mode.
# It does NOT grant canary authority.
# It does NOT promote any candidate to canon.
# It does NOT grant runtime authority.
# It does NOT execute runtime behavior.
# It does NOT create proactive or autonomous behavior.
# It does NOT mutate runtime, scheduler, baseline, canon, or forecast weights.
# It does NOT grant AAL-Viz inference authority.
# It does NOT promote any candidate beyond decision-record readiness.

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from jsonschema import validate

from core.research_canary_decision_record import (
    build_research_canary_decision_record,
    write_research_canary_decision_record,
)
from scripts import run_research_canary_decision_record
from scripts.run_research_canary_decision_record import (
    P107_DEFAULT_PATH,
    _load_json_packet,
    _parse_args,
)

_AUTHORITY_LOCKS_P107 = {
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
    "canary_activation": False,
    "canary_authority": False,
}

_REVIEW_PACKET_COMPLETE_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P107_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchCanaryReviewPacket.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P107_RESEARCH_CANARY_REVIEW_PACKET",
    "status": "CANARY_REVIEW_PACKET_EMITTED",
    "upstream_lane_id": "P106_RESEARCH_CANARY_ELIGIBILITY_DOSSIER",
    "upstream_canary_eligibility_dossier_status": "CANARY_ELIGIBILITY_DOSSIER_EMITTED",
    "canary_review_packet_status": "EMITTED",
    "stabilized_candidates": list(_REVIEW_PACKET_COMPLETE_CANDIDATES),
    "held_candidates": ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"],
    "repair_candidates": ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"],
    "rejected_candidates": ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"],
    "analyzed_candidates": list(_REVIEW_PACKET_COMPLETE_CANDIDATES),
    "review_packet_complete_candidates": list(_REVIEW_PACKET_COMPLETE_CANDIDATES),
    "review_packet_incomplete_candidates": [],
    "candidate_review_statuses": [],
    "required_review_observations": [],
    "missing_review_requirements": {},
    "authority_locks": dict(_AUTHORITY_LOCKS_P107),
    "recommended_next_lane": "P108_RESEARCH_CANARY_DECISION_RECORD",
    "recommended_next_lane_reason": "Proceed to P108.",
    "not_computable_reasons": [],
    "provenance": {"source": "p106"},
    "packet_hash": "a" * 64,
}


def _decision_observations(decision: str = "approve_for_future_canary_plan") -> dict[str, Any]:
    return {
        "candidate_decision_observations": {
            candidate_id: {
                "candidate_id": candidate_id,
                "decision": decision,
                "operator_decision_observed": True,
                "decision_rationale_attached": True,
                "provenance_bundle_attached": True,
                "review_packet_complete_observed": True,
                "authority_drift_observed": False,
                "notes": "decision evidence confirmed",
            }
            for candidate_id in _REVIEW_PACKET_COMPLETE_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_canary_decision_record.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_output_across_repeated_runs() -> None:
    observations = _decision_observations()
    first = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=observations,
    )
    second = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=observations,
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def test_schema_validates_representative_approved_packet() -> None:
    packet = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=_decision_observations(),
    )
    validate(packet, _schema())


def test_schema_validates_representative_continue_packet() -> None:
    packet = build_research_canary_decision_record(p107_packet=_VALID_P107_PACKET)
    validate(packet, _schema())


def test_schema_validates_representative_failure_packet() -> None:
    packet = build_research_canary_decision_record(p107_packet=None)
    validate(packet, _schema())


# ---------------------------------------------------------------------------
# NOT_COMPUTABLE cases
# ---------------------------------------------------------------------------


def test_p107_missing_returns_not_computable() -> None:
    packet = build_research_canary_decision_record(p107_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p107_packet_missing" in packet["not_computable_reasons"]


def test_malformed_p107_returns_not_computable() -> None:
    packet = build_research_canary_decision_record(
        p107_packet="bad"  # type: ignore[arg-type]
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["not_computable_reasons"] == ["p107_packet_malformed:not_a_dict"]


def test_wrong_chain_p107_returns_not_computable() -> None:
    packet = build_research_canary_decision_record(
        p107_packet={**_VALID_P107_PACKET, "recommended_next_lane": "P999_WRONG"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p107_recommendation_chain_mismatch" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_non_emitted_non_pass_p107_returns_not_computable() -> None:
    packet = build_research_canary_decision_record(
        p107_packet={
            **_VALID_P107_PACKET,
            "status": "NOT_COMPUTABLE",
            "canary_review_packet_status": "NOT_COMPUTABLE",
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p107_status_not_emitted" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_p107_without_p108_recommendation_never_recommends_p109() -> None:
    packet = build_research_canary_decision_record(
        p107_packet={
            **_VALID_P107_PACKET,
            "recommended_next_lane": "P107_RESEARCH_CANARY_REVIEW_PACKET_CONTINUE",
        },
        decision_observations_packet=_decision_observations(),
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] != "P109_RESEARCH_CANARY_PLAN_DRAFT"


def test_no_review_packet_complete_candidates_returns_not_computable() -> None:
    packet = build_research_canary_decision_record(
        p107_packet={**_VALID_P107_PACKET, "review_packet_complete_candidates": []}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p107_no_review_packet_complete_candidates" in packet["not_computable_reasons"]


# ---------------------------------------------------------------------------
# REJECTED_AUTHORITY_DRIFT cases
# ---------------------------------------------------------------------------


def test_p107_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_decision_record(
        p107_packet={
            **_VALID_P107_PACKET,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "canary_review_packet_status": "REJECTED_AUTHORITY_DRIFT",
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_decision_observation_authority_drift_returns_rejected_authority_drift() -> None:
    observations = _decision_observations()
    first_candidate = _REVIEW_PACKET_COMPLETE_CANDIDATES[0]
    observations["candidate_decision_observations"][first_candidate][
        "authority_drift_observed"
    ] = True
    packet = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=observations,
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_forbidden_decision_returns_rejected_authority_drift() -> None:
    observations = _decision_observations(decision="activate_canary")
    packet = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=observations,
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


# ---------------------------------------------------------------------------
# Recommendation routing
# ---------------------------------------------------------------------------


def test_default_missing_decision_observations_recommend_p108_continue_and_hold() -> None:
    packet = build_research_canary_decision_record(p107_packet=_VALID_P107_PACKET)
    assert packet["status"] == "CANARY_DECISION_RECORD_EMITTED"
    assert packet["recommended_next_lane"] == "P108_RESEARCH_CANARY_DECISION_RECORD_CONTINUE"
    assert set(packet["held_for_review_candidates"]) == set(_REVIEW_PACKET_COMPLETE_CANDIDATES)
    for cs in packet["candidate_decision_statuses"]:
        assert cs["decision"] == "hold"
        assert cs["canary_decision_status"] == "CANARY_DECISION_HELD_PENDING_REVIEW"


def test_all_approved_with_required_evidence_recommend_p109() -> None:
    packet = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=_decision_observations(),
    )
    assert packet["status"] == "CANARY_DECISION_RECORD_EMITTED"
    assert packet["recommended_next_lane"] == "P109_RESEARCH_CANARY_PLAN_DRAFT"
    assert set(packet["approved_for_future_canary_plan_candidates"]) == set(
        _REVIEW_PACKET_COMPLETE_CANDIDATES
    )


def test_hold_blocks_p109() -> None:
    packet = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=_decision_observations(decision="hold"),
    )
    assert packet["recommended_next_lane"] != "P109_RESEARCH_CANARY_PLAN_DRAFT"


def test_request_repair_blocks_p109_and_records_repair_requested_candidates() -> None:
    packet = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=_decision_observations(decision="request_repair"),
    )
    assert packet["recommended_next_lane"] != "P109_RESEARCH_CANARY_PLAN_DRAFT"
    assert set(packet["repair_requested_candidates"]) == set(
        _REVIEW_PACKET_COMPLETE_CANDIDATES
    )


def test_reject_blocks_p109_and_records_rejected_by_decision_candidates() -> None:
    packet = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=_decision_observations(decision="reject"),
    )
    assert packet["recommended_next_lane"] != "P109_RESEARCH_CANARY_PLAN_DRAFT"
    assert set(packet["rejected_by_decision_candidates"]) == set(
        _REVIEW_PACKET_COMPLETE_CANDIDATES
    )


@pytest.mark.parametrize(
    "missing_field",
    [
        "operator_decision_observed",
        "decision_rationale_attached",
        "provenance_bundle_attached",
        "review_packet_complete_observed",
    ],
)
def test_missing_required_decision_evidence_blocks_p109(missing_field: str) -> None:
    observations = _decision_observations()
    for candidate_id in _REVIEW_PACKET_COMPLETE_CANDIDATES:
        observations["candidate_decision_observations"][candidate_id][missing_field] = False
    packet = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] != "P109_RESEARCH_CANARY_PLAN_DRAFT"
    for cs in packet["candidate_decision_statuses"]:
        assert any(
            missing_field in requirement
            for requirement in cs["missing_decision_requirements"]
        )


# ---------------------------------------------------------------------------
# Candidate list preservation
# ---------------------------------------------------------------------------


def test_held_repair_rejected_candidates_from_upstream_are_preserved_separately() -> None:
    packet = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=_decision_observations(),
    )
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]
    assert packet["repair_candidates"] == [
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"
    ]
    assert packet["rejected_candidates"] == [
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"
    ]


def test_only_review_packet_complete_candidates_are_analyzed() -> None:
    p107_packet = {
        **_VALID_P107_PACKET,
        "review_packet_complete_candidates": [_REVIEW_PACKET_COMPLETE_CANDIDATES[0]],
    }
    packet = build_research_canary_decision_record(
        p107_packet=p107_packet,
        decision_observations_packet=_decision_observations(),
    )
    assert packet["analyzed_candidates"] == [_REVIEW_PACKET_COMPLETE_CANDIDATES[0]]
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------


def test_all_authority_locks_remain_false_including_canary_activation_and_authority() -> None:
    packet = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=_decision_observations(),
    )
    locks = packet["authority_locks"]
    assert isinstance(locks, dict)
    expected_keys = {
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "forecast_influence",
        "forecast_weight_allowed",
        "shadow_to_forecast_leakage",
        "scheduler_mutation",
        "autonomous_execution",
        "operator_bypass",
        "hidden_intent_claim_authority",
        "canary_activation",
        "canary_authority",
    }
    assert set(locks.keys()) == expected_keys
    for key, value in locks.items():
        assert value is False, f"authority_lock {key!r} must be False, got {value!r}"


# ---------------------------------------------------------------------------
# Packet hash
# ---------------------------------------------------------------------------


def test_packet_hash_is_deterministic_and_excludes_itself() -> None:
    packet = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=_decision_observations(),
    )
    packet_hash = packet["packet_hash"]
    assert isinstance(packet_hash, str)
    assert len(packet_hash) == 64
    assert all(c in "0123456789abcdef" for c in packet_hash)

    base_without_hash = {k: v for k, v in packet.items() if k != "packet_hash"}
    serialized = json.dumps(
        base_without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    expected_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    assert packet_hash == expected_hash


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------


def test_output_writer_emits_canonical_json_with_trailing_newline() -> None:
    packet = build_research_canary_decision_record(
        p107_packet=_VALID_P107_PACKET,
        decision_observations_packet=_decision_observations(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        write_research_canary_decision_record(out_path, packet)
        content = out_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    parsed = json.loads(content)
    assert parsed == packet


# ---------------------------------------------------------------------------
# Runner CLI
# ---------------------------------------------------------------------------


def test_runner_default_p107_path() -> None:
    args = _parse_args([])
    assert args.p107_path == str(P107_DEFAULT_PATH)
    assert args.decision_observations_path is None


def test_runner_supports_p107_path_flag() -> None:
    args = _parse_args(["--p107-path", "/some/path/latest.json"])
    assert args.p107_path == "/some/path/latest.json"


def test_runner_supports_decision_observations_path_flag() -> None:
    args = _parse_args(["--decision-observations-path", "/some/observations.json"])
    assert args.decision_observations_path == "/some/observations.json"


def test_runner_load_json_packet_missing_file_returns_none() -> None:
    result = _load_json_packet("/nonexistent/path/latest.json")
    assert result is None


def test_runner_load_json_packet_none_returns_none() -> None:
    result = _load_json_packet(None)
    assert result is None


def test_runner_run_writes_output_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        packet = run_research_canary_decision_record.run(
            p107_packet=_VALID_P107_PACKET,
            decision_observations_packet=_decision_observations(),
            out_path=out_path,
        )
        assert out_path.exists()
        written = json.loads(out_path.read_text(encoding="utf-8"))
        assert written == packet
        assert written["status"] == "CANARY_DECISION_RECORD_EMITTED"


# ---------------------------------------------------------------------------
# Generated out/ artifacts remain untouched
# ---------------------------------------------------------------------------


def test_out_validation_latest_json_untouched() -> None:
    path = Path("out/validation/latest.json")
    assert path.exists(), "out/validation/latest.json must exist"
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_decision_record(p107_packet=None)
    content_after = path.read_text(encoding="utf-8")
    assert content_before == content_after


def test_out_projections_aal_viz_latest_json_untouched() -> None:
    path = Path("out/projections/aal_viz.latest.json")
    assert path.exists(), "out/projections/aal_viz.latest.json must exist"
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_decision_record(p107_packet=None)
    content_after = path.read_text(encoding="utf-8")
    assert content_before == content_after
