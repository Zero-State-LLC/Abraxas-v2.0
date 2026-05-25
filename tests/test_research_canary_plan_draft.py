from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P109 is advisory-only and projection-only.
# It does NOT activate canary mode.
# It does NOT grant canary authority.
# It does NOT execute any canary plan.
# It does NOT promote any candidate to canon.
# It does NOT grant runtime authority.
# It does NOT execute runtime behavior.
# It does NOT create proactive or autonomous behavior.
# It does NOT mutate runtime, scheduler, baseline, canon, or forecast weights.
# It does NOT grant AAL-Viz inference authority.
# It does NOT implement P110 behavior.

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from jsonschema import validate

from core.research_canary_plan_draft import (
    build_research_canary_plan_draft,
    write_research_canary_plan_draft,
)
from scripts import run_research_canary_plan_draft
from scripts.run_research_canary_plan_draft import (
    P108_DEFAULT_PATH,
    _load_json_packet,
    _parse_args,
)

_AUTHORITY_LOCKS_P108 = {
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

_APPROVED_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P108_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchCanaryDecisionRecord.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P108_RESEARCH_CANARY_DECISION_RECORD",
    "status": "CANARY_DECISION_RECORD_EMITTED",
    "upstream_lane_id": "P107_RESEARCH_CANARY_REVIEW_PACKET",
    "upstream_canary_review_packet_status": "CANARY_REVIEW_PACKET_EMITTED",
    "canary_decision_record_status": "EMITTED",
    "stabilized_candidates": list(_APPROVED_CANDIDATES),
    "held_candidates": ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"],
    "repair_candidates": ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"],
    "rejected_candidates": ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"],
    "analyzed_candidates": list(_APPROVED_CANDIDATES),
    "approved_for_future_canary_plan_candidates": list(_APPROVED_CANDIDATES),
    "held_for_review_candidates": [],
    "repair_requested_candidates": [],
    "rejected_by_decision_candidates": [],
    "candidate_decision_statuses": [],
    "allowed_decisions": [],
    "forbidden_decisions": [],
    "missing_decision_requirements": {},
    "authority_locks": dict(_AUTHORITY_LOCKS_P108),
    "recommended_next_lane": "P109_RESEARCH_CANARY_PLAN_DRAFT",
    "recommended_next_lane_reason": "Proceed to P109.",
    "not_computable_reasons": [],
    "provenance": {"source": "p107"},
    "packet_hash": "a" * 64,
}


def _plan_observations() -> dict[str, Any]:
    return {
        "candidate_plan_observations": {
            candidate_id: {
                "candidate_id": candidate_id,
                "canary_scope_defined": True,
                "rollback_plan_defined": True,
                "monitoring_plan_defined": True,
                "blast_radius_defined": True,
                "exit_criteria_defined": True,
                "operator_review_required": True,
                "provenance_bundle_attached": True,
                "safety_notes_attached": True,
                "execution_disabled_confirmed": True,
                "authority_drift_observed": False,
                "notes": "draft observations captured",
            }
            for candidate_id in _APPROVED_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_canary_plan_draft.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_output_across_repeated_runs() -> None:
    observations = _plan_observations()
    first = build_research_canary_plan_draft(
        p108_packet=_VALID_P108_PACKET,
        plan_observations_packet=observations,
    )
    second = build_research_canary_plan_draft(
        p108_packet=_VALID_P108_PACKET,
        plan_observations_packet=observations,
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def test_schema_validates_representative_complete_packet() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet=_VALID_P108_PACKET,
        plan_observations_packet=_plan_observations(),
    )
    validate(packet, _schema())


def test_schema_validates_representative_continue_packet() -> None:
    packet = build_research_canary_plan_draft(p108_packet=_VALID_P108_PACKET)
    validate(packet, _schema())


def test_schema_validates_representative_failure_packet() -> None:
    packet = build_research_canary_plan_draft(p108_packet=None)
    validate(packet, _schema())


# ---------------------------------------------------------------------------
# NOT_COMPUTABLE cases
# ---------------------------------------------------------------------------


def test_p108_missing_returns_not_computable() -> None:
    packet = build_research_canary_plan_draft(p108_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p108_packet_missing" in packet["not_computable_reasons"]


def test_malformed_p108_returns_not_computable() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet="bad"  # type: ignore[arg-type]
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["not_computable_reasons"] == ["p108_packet_malformed:not_a_dict"]


def test_wrong_chain_p108_returns_not_computable() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet={**_VALID_P108_PACKET, "recommended_next_lane": "P999_WRONG"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p108_recommendation_chain_mismatch" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_non_emitted_non_pass_p108_returns_not_computable() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet={
            **_VALID_P108_PACKET,
            "status": "NOT_COMPUTABLE",
            "canary_decision_record_status": "NOT_COMPUTABLE",
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p108_status_not_emitted" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_p108_without_p109_recommendation_never_recommends_p110() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet={
            **_VALID_P108_PACKET,
            "recommended_next_lane": "P108_RESEARCH_CANARY_DECISION_RECORD_CONTINUE",
        },
        plan_observations_packet=_plan_observations(),
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] != "P110_RESEARCH_CANARY_PLAN_REVIEW_RECORD"


def test_no_approved_for_future_canary_plan_candidates_returns_not_computable() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet={**_VALID_P108_PACKET, "approved_for_future_canary_plan_candidates": []}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert (
        "p108_no_approved_for_future_canary_plan_candidates"
        in packet["not_computable_reasons"]
    )


# ---------------------------------------------------------------------------
# REJECTED_AUTHORITY_DRIFT cases
# ---------------------------------------------------------------------------


def test_p108_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet={
            **_VALID_P108_PACKET,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "canary_decision_record_status": "REJECTED_AUTHORITY_DRIFT",
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_p108_authority_lock_true_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet={
            **_VALID_P108_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS_P108, "canary_authority": True},
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_plan_observation_authority_drift_returns_rejected_authority_drift() -> None:
    observations = _plan_observations()
    first_candidate = _APPROVED_CANDIDATES[0]
    observations["candidate_plan_observations"][first_candidate][
        "authority_drift_observed"
    ] = True
    packet = build_research_canary_plan_draft(
        p108_packet=_VALID_P108_PACKET,
        plan_observations_packet=observations,
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


# ---------------------------------------------------------------------------
# Recommendation routing
# ---------------------------------------------------------------------------


def test_default_missing_plan_observations_recommend_p109_continue() -> None:
    packet = build_research_canary_plan_draft(p108_packet=_VALID_P108_PACKET)
    assert packet["status"] == "CANARY_PLAN_DRAFT_EMITTED"
    assert packet["canary_plan_draft_status"] == "CANARY_PLAN_DRAFT_INCOMPLETE"
    assert packet["recommended_next_lane"] == "P109_RESEARCH_CANARY_PLAN_DRAFT_CONTINUE"
    for cs in packet["candidate_plan_statuses"]:
        assert cs["canary_plan_draft_status"] == "CANARY_PLAN_DRAFT_INCOMPLETE"


def test_complete_plan_observations_for_every_candidate_recommend_p110() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet=_VALID_P108_PACKET,
        plan_observations_packet=_plan_observations(),
    )
    assert packet["status"] == "CANARY_PLAN_DRAFT_EMITTED"
    assert packet["canary_plan_draft_status"] == "CANARY_PLAN_DRAFT_COMPLETE"
    assert packet["recommended_next_lane"] == "P110_RESEARCH_CANARY_PLAN_REVIEW_RECORD"
    for cs in packet["candidate_plan_statuses"]:
        assert cs["canary_plan_draft_status"] == "CANARY_PLAN_DRAFT_COMPLETE"


@pytest.mark.parametrize(
    "missing_field",
    [
        "canary_scope_defined",
        "rollback_plan_defined",
        "monitoring_plan_defined",
        "blast_radius_defined",
        "exit_criteria_defined",
        "operator_review_required",
        "provenance_bundle_attached",
        "safety_notes_attached",
        "execution_disabled_confirmed",
    ],
)
def test_missing_required_plan_observation_blocks_p110(missing_field: str) -> None:
    observations = _plan_observations()
    for candidate_id in _APPROVED_CANDIDATES:
        observations["candidate_plan_observations"][candidate_id][missing_field] = False
    packet = build_research_canary_plan_draft(
        p108_packet=_VALID_P108_PACKET,
        plan_observations_packet=observations,
    )
    assert packet["status"] == "CANARY_PLAN_DRAFT_EMITTED"
    assert packet["recommended_next_lane"] != "P110_RESEARCH_CANARY_PLAN_REVIEW_RECORD"
    for cs in packet["candidate_plan_statuses"]:
        assert cs["canary_plan_draft_status"] == "CANARY_PLAN_DRAFT_INCOMPLETE"
        assert any(missing_field in req for req in cs["missing_plan_requirements"])


# ---------------------------------------------------------------------------
# Candidate list preservation
# ---------------------------------------------------------------------------


def test_held_repair_rejected_candidates_from_upstream_are_preserved_separately() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet=_VALID_P108_PACKET,
        plan_observations_packet=_plan_observations(),
    )
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]
    assert packet["repair_candidates"] == [
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"
    ]
    assert packet["rejected_candidates"] == [
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"
    ]


def test_only_approved_for_future_canary_plan_candidates_are_analyzed() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet={
            **_VALID_P108_PACKET,
            "approved_for_future_canary_plan_candidates": [_APPROVED_CANDIDATES[0]],
        },
        plan_observations_packet=_plan_observations(),
    )
    assert packet["analyzed_candidates"] == [_APPROVED_CANDIDATES[0]]
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------


def test_all_authority_locks_remain_false_including_canary_locks() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet=_VALID_P108_PACKET,
        plan_observations_packet=_plan_observations(),
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
        "canary_plan_execution",
    }
    assert set(locks.keys()) == expected_keys
    for key, value in locks.items():
        assert value is False, f"authority_lock {key!r} must be False, got {value!r}"


# ---------------------------------------------------------------------------
# Packet hash
# ---------------------------------------------------------------------------


def test_packet_hash_is_deterministic_and_excludes_itself() -> None:
    packet = build_research_canary_plan_draft(
        p108_packet=_VALID_P108_PACKET,
        plan_observations_packet=_plan_observations(),
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
    packet = build_research_canary_plan_draft(
        p108_packet=_VALID_P108_PACKET,
        plan_observations_packet=_plan_observations(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        write_research_canary_plan_draft(out_path, packet)
        content = out_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    parsed = json.loads(content)
    assert parsed == packet


# ---------------------------------------------------------------------------
# Runner CLI
# ---------------------------------------------------------------------------


def test_runner_default_p108_path() -> None:
    args = _parse_args([])
    assert args.p108_path == str(P108_DEFAULT_PATH)
    assert args.plan_observations_path is None


def test_runner_supports_p108_path_flag() -> None:
    args = _parse_args(["--p108-path", "/some/path/latest.json"])
    assert args.p108_path == "/some/path/latest.json"


def test_runner_supports_plan_observations_path_flag() -> None:
    args = _parse_args(["--plan-observations-path", "/some/observations.json"])
    assert args.plan_observations_path == "/some/observations.json"


def test_runner_load_json_packet_missing_file_returns_none() -> None:
    result = _load_json_packet("/nonexistent/path/latest.json")
    assert result is None


def test_runner_load_json_packet_none_returns_none() -> None:
    result = _load_json_packet(None)
    assert result is None


def test_runner_run_writes_output_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        packet = run_research_canary_plan_draft.run(
            p108_packet=_VALID_P108_PACKET,
            plan_observations_packet=_plan_observations(),
            out_path=out_path,
        )
        assert out_path.exists()
        written = json.loads(out_path.read_text(encoding="utf-8"))
        assert written == packet
        assert written["status"] == "CANARY_PLAN_DRAFT_EMITTED"


# ---------------------------------------------------------------------------
# Generated out/ artifacts remain untouched
# ---------------------------------------------------------------------------


def test_out_validation_latest_json_untouched() -> None:
    path = Path("out/validation/latest.json")
    assert path.exists(), "out/validation/latest.json must exist"
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_plan_draft(p108_packet=None)
    content_after = path.read_text(encoding="utf-8")
    assert content_before == content_after


def test_out_projections_aal_viz_latest_json_untouched() -> None:
    path = Path("out/projections/aal_viz.latest.json")
    assert path.exists(), "out/projections/aal_viz.latest.json must exist"
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_plan_draft(p108_packet=None)
    content_after = path.read_text(encoding="utf-8")
    assert content_before == content_after
