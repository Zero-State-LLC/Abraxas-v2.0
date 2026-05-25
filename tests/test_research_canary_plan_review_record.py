from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P110 is advisory-only and projection-only.
# It does NOT activate canary mode.
# It does NOT grant canary authority.
# It does NOT execute any canary plan.
# It does NOT authorize any canary operation.
# It does NOT promote any candidate to canon.
# It does NOT grant runtime authority.
# It does NOT execute runtime behavior.
# It does NOT create proactive or autonomous behavior.
# It does NOT mutate runtime, scheduler, baseline, canon, or forecast weights.
# It does NOT grant AAL-Viz inference authority.
# It does NOT implement P111 behavior.

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from jsonschema import validate

from core.research_canary_plan_review_record import (
    build_research_canary_plan_review_record,
    write_research_canary_plan_review_record,
)
from scripts import run_research_canary_plan_review_record
from scripts.run_research_canary_plan_review_record import (
    P109_DEFAULT_PATH,
    _load_json_packet,
    _parse_args,
)

_AUTHORITY_LOCKS_P109 = {
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
    "canary_plan_execution": False,
}

_PLAN_DRAFT_COMPLETE_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P109_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchCanaryPlanDraft.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P109_RESEARCH_CANARY_PLAN_DRAFT",
    "status": "CANARY_PLAN_DRAFT_EMITTED",
    "upstream_lane_id": "P108_RESEARCH_CANARY_DECISION_RECORD",
    "upstream_canary_decision_record_status": "CANARY_DECISION_RECORD_EMITTED",
    "canary_plan_draft_status": "CANARY_PLAN_DRAFT_COMPLETE",
    "stabilized_candidates": list(_PLAN_DRAFT_COMPLETE_CANDIDATES),
    "held_candidates": ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"],
    "repair_candidates": ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"],
    "rejected_candidates": ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"],
    "analyzed_candidates": list(_PLAN_DRAFT_COMPLETE_CANDIDATES),
    "plan_draft_complete_candidates": list(_PLAN_DRAFT_COMPLETE_CANDIDATES),
    "plan_draft_incomplete_candidates": [],
    "candidate_plan_statuses": [],
    "required_plan_observations": [],
    "missing_plan_requirements": {},
    "authority_locks": dict(_AUTHORITY_LOCKS_P109),
    "recommended_next_lane": "P110_RESEARCH_CANARY_PLAN_REVIEW_RECORD",
    "recommended_next_lane_reason": "Proceed to P110.",
    "not_computable_reasons": [],
    "provenance": {"source": "p108"},
    "packet_hash": "a" * 64,
}


def _plan_review_observations() -> dict[str, Any]:
    return {
        "candidate_plan_review_observations": {
            candidate_id: {
                "candidate_id": candidate_id,
                "plan_draft_complete_observed": True,
                "scope_review_complete": True,
                "rollback_review_complete": True,
                "monitoring_review_complete": True,
                "blast_radius_review_complete": True,
                "exit_criteria_review_complete": True,
                "provenance_review_complete": True,
                "safety_review_complete": True,
                "execution_disabled_review_complete": True,
                "operator_review_observed": True,
                "authority_drift_observed": False,
                "notes": "review observations captured",
            }
            for candidate_id in _PLAN_DRAFT_COMPLETE_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_canary_plan_review_record.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_output_across_repeated_runs() -> None:
    observations = _plan_review_observations()
    first = build_research_canary_plan_review_record(
        p109_packet=_VALID_P109_PACKET,
        plan_review_observations_packet=observations,
    )
    second = build_research_canary_plan_review_record(
        p109_packet=_VALID_P109_PACKET,
        plan_review_observations_packet=observations,
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def test_schema_validates_representative_complete_packet() -> None:
    packet = build_research_canary_plan_review_record(
        p109_packet=_VALID_P109_PACKET,
        plan_review_observations_packet=_plan_review_observations(),
    )
    validate(packet, _schema())


def test_schema_validates_representative_continue_packet() -> None:
    packet = build_research_canary_plan_review_record(p109_packet=_VALID_P109_PACKET)
    validate(packet, _schema())


def test_schema_validates_representative_failure_packet() -> None:
    packet = build_research_canary_plan_review_record(p109_packet=None)
    validate(packet, _schema())


# ---------------------------------------------------------------------------
# NOT_COMPUTABLE cases
# ---------------------------------------------------------------------------


def test_p109_missing_returns_not_computable() -> None:
    packet = build_research_canary_plan_review_record(p109_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p109_packet_missing" in packet["not_computable_reasons"]


def test_malformed_p109_returns_not_computable() -> None:
    packet = build_research_canary_plan_review_record(
        p109_packet="bad"  # type: ignore[arg-type]
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["not_computable_reasons"] == ["p109_packet_malformed:not_a_dict"]


def test_wrong_chain_p109_returns_not_computable() -> None:
    packet = build_research_canary_plan_review_record(
        p109_packet={**_VALID_P109_PACKET, "recommended_next_lane": "P999_WRONG"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p109_recommendation_chain_mismatch" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_non_emitted_non_pass_p109_returns_not_computable() -> None:
    packet = build_research_canary_plan_review_record(
        p109_packet={
            **_VALID_P109_PACKET,
            "status": "NOT_COMPUTABLE",
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p109_status_not_emitted" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_p109_without_p110_recommendation_never_recommends_p111() -> None:
    packet = build_research_canary_plan_review_record(
        p109_packet={
            **_VALID_P109_PACKET,
            "recommended_next_lane": "P109_RESEARCH_CANARY_PLAN_DRAFT_CONTINUE",
        },
        plan_review_observations_packet=_plan_review_observations(),
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert (
        packet["recommended_next_lane"]
        != "P111_RESEARCH_CANARY_AUTHORIZATION_DRAFT"
    )


def test_no_plan_draft_complete_candidates_returns_not_computable() -> None:
    packet = build_research_canary_plan_review_record(
        p109_packet={
            **_VALID_P109_PACKET,
            "plan_draft_complete_candidates": [],
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert (
        "p109_no_plan_draft_complete_candidates" in packet["not_computable_reasons"]
    )


# ---------------------------------------------------------------------------
# REJECTED_AUTHORITY_DRIFT cases
# ---------------------------------------------------------------------------


def test_p109_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_plan_review_record(
        p109_packet={
            **_VALID_P109_PACKET,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "canary_plan_draft_status": "CANARY_PLAN_DRAFT_REJECTED_AUTHORITY_DRIFT",
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_p109_authority_lock_true_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_plan_review_record(
        p109_packet={
            **_VALID_P109_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS_P109, "canary_authority": True},
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_plan_review_observation_authority_drift_returns_rejected_authority_drift() -> (
    None
):
    observations = _plan_review_observations()
    first_candidate = _PLAN_DRAFT_COMPLETE_CANDIDATES[0]
    observations["candidate_plan_review_observations"][first_candidate][
        "authority_drift_observed"
    ] = True
    packet = build_research_canary_plan_review_record(
        p109_packet=_VALID_P109_PACKET,
        plan_review_observations_packet=observations,
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


# ---------------------------------------------------------------------------
# Recommendation routing
# ---------------------------------------------------------------------------


def test_default_missing_plan_review_observations_recommend_p110_continue() -> None:
    packet = build_research_canary_plan_review_record(p109_packet=_VALID_P109_PACKET)
    assert packet["status"] == "CANARY_PLAN_REVIEW_RECORD_EMITTED"
    assert packet["canary_plan_review_record_status"] == "CANARY_PLAN_REVIEW_INCOMPLETE"
    assert (
        packet["recommended_next_lane"]
        == "P110_RESEARCH_CANARY_PLAN_REVIEW_RECORD_CONTINUE"
    )
    for cs in packet["candidate_plan_review_statuses"]:
        assert cs["canary_plan_review_status"] == "CANARY_PLAN_REVIEW_INCOMPLETE"


def test_complete_plan_review_observations_for_every_candidate_recommend_p111() -> (
    None
):
    packet = build_research_canary_plan_review_record(
        p109_packet=_VALID_P109_PACKET,
        plan_review_observations_packet=_plan_review_observations(),
    )
    assert packet["status"] == "CANARY_PLAN_REVIEW_RECORD_EMITTED"
    assert packet["canary_plan_review_record_status"] == "CANARY_PLAN_REVIEW_COMPLETE"
    assert (
        packet["recommended_next_lane"] == "P111_RESEARCH_CANARY_AUTHORIZATION_DRAFT"
    )
    for cs in packet["candidate_plan_review_statuses"]:
        assert cs["canary_plan_review_status"] == "CANARY_PLAN_REVIEW_COMPLETE"


@pytest.mark.parametrize(
    "missing_field",
    [
        "plan_draft_complete_observed",
        "scope_review_complete",
        "rollback_review_complete",
        "monitoring_review_complete",
        "blast_radius_review_complete",
        "exit_criteria_review_complete",
        "provenance_review_complete",
        "safety_review_complete",
        "execution_disabled_review_complete",
        "operator_review_observed",
    ],
)
def test_missing_required_plan_review_observation_blocks_p111(
    missing_field: str,
) -> None:
    observations = _plan_review_observations()
    for candidate_id in _PLAN_DRAFT_COMPLETE_CANDIDATES:
        observations["candidate_plan_review_observations"][candidate_id][
            missing_field
        ] = False
    packet = build_research_canary_plan_review_record(
        p109_packet=_VALID_P109_PACKET,
        plan_review_observations_packet=observations,
    )
    assert packet["status"] == "CANARY_PLAN_REVIEW_RECORD_EMITTED"
    assert (
        packet["recommended_next_lane"]
        != "P111_RESEARCH_CANARY_AUTHORIZATION_DRAFT"
    )
    for cs in packet["candidate_plan_review_statuses"]:
        assert cs["canary_plan_review_status"] == "CANARY_PLAN_REVIEW_INCOMPLETE"
        assert any(
            missing_field in req for req in cs["missing_plan_review_requirements"]
        )


# ---------------------------------------------------------------------------
# Candidate list preservation
# ---------------------------------------------------------------------------


def test_held_repair_rejected_candidates_from_upstream_are_preserved_separately() -> (
    None
):
    packet = build_research_canary_plan_review_record(
        p109_packet=_VALID_P109_PACKET,
        plan_review_observations_packet=_plan_review_observations(),
    )
    assert packet["held_candidates"] == [
        "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"
    ]
    assert packet["repair_candidates"] == [
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"
    ]
    assert packet["rejected_candidates"] == [
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"
    ]


def test_only_plan_draft_complete_candidates_are_analyzed() -> None:
    packet = build_research_canary_plan_review_record(
        p109_packet={
            **_VALID_P109_PACKET,
            "plan_draft_complete_candidates": [_PLAN_DRAFT_COMPLETE_CANDIDATES[0]],
        },
        plan_review_observations_packet=_plan_review_observations(),
    )
    assert packet["analyzed_candidates"] == [_PLAN_DRAFT_COMPLETE_CANDIDATES[0]]
    assert packet["held_candidates"] == [
        "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"
    ]


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------


def test_all_authority_locks_remain_false_including_canary_locks() -> None:
    packet = build_research_canary_plan_review_record(
        p109_packet=_VALID_P109_PACKET,
        plan_review_observations_packet=_plan_review_observations(),
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
        "canary_authorization",
    }
    assert set(locks.keys()) == expected_keys
    for key, value in locks.items():
        assert value is False, f"authority_lock {key!r} must be False, got {value!r}"


# ---------------------------------------------------------------------------
# Packet hash
# ---------------------------------------------------------------------------


def test_packet_hash_is_deterministic_and_excludes_itself() -> None:
    packet = build_research_canary_plan_review_record(
        p109_packet=_VALID_P109_PACKET,
        plan_review_observations_packet=_plan_review_observations(),
    )
    packet_hash = packet["packet_hash"]
    assert isinstance(packet_hash, str)
    assert len(packet_hash) == 64
    assert all(c in "0123456789abcdef" for c in packet_hash)

    base_without_hash = {k: v for k, v in packet.items() if k != "packet_hash"}
    serialized = json.dumps(
        base_without_hash,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    expected_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    assert packet_hash == expected_hash


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------


def test_output_writer_emits_canonical_json_with_trailing_newline() -> None:
    packet = build_research_canary_plan_review_record(
        p109_packet=_VALID_P109_PACKET,
        plan_review_observations_packet=_plan_review_observations(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        write_research_canary_plan_review_record(out_path, packet)
        content = out_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    parsed = json.loads(content)
    assert parsed == packet


# ---------------------------------------------------------------------------
# Runner CLI
# ---------------------------------------------------------------------------


def test_runner_default_p109_path() -> None:
    args = _parse_args([])
    assert args.p109_path == str(P109_DEFAULT_PATH)
    assert args.plan_review_observations_path is None


def test_runner_supports_p109_path_flag() -> None:
    args = _parse_args(["--p109-path", "/some/path/latest.json"])
    assert args.p109_path == "/some/path/latest.json"


def test_runner_supports_plan_review_observations_path_flag() -> None:
    args = _parse_args(
        ["--plan-review-observations-path", "/some/review_observations.json"]
    )
    assert args.plan_review_observations_path == "/some/review_observations.json"


def test_runner_load_json_packet_missing_file_returns_none() -> None:
    result = _load_json_packet("/nonexistent/path/latest.json")
    assert result is None


def test_runner_load_json_packet_none_returns_none() -> None:
    result = _load_json_packet(None)
    assert result is None


def test_runner_run_writes_output_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        packet = run_research_canary_plan_review_record.run(
            p109_packet=_VALID_P109_PACKET,
            plan_review_observations_packet=_plan_review_observations(),
            out_path=out_path,
        )
        assert out_path.exists()
        written = json.loads(out_path.read_text(encoding="utf-8"))
        assert written == packet
        assert written["status"] == "CANARY_PLAN_REVIEW_RECORD_EMITTED"


# ---------------------------------------------------------------------------
# Generated out/ artifacts remain untouched
# ---------------------------------------------------------------------------


def test_out_validation_latest_json_untouched() -> None:
    path = Path("out/validation/latest.json")
    assert path.exists(), "out/validation/latest.json must exist"
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_plan_review_record(p109_packet=None)
    content_after = path.read_text(encoding="utf-8")
    assert content_before == content_after


def test_out_projections_aal_viz_latest_json_untouched() -> None:
    path = Path("out/projections/aal_viz.latest.json")
    assert path.exists(), "out/projections/aal_viz.latest.json must exist"
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_plan_review_record(p109_packet=None)
    content_after = path.read_text(encoding="utf-8")
    assert content_before == content_after
