from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P111 is advisory-only and projection-only.
# It does NOT authorize canary mode.
# It does NOT activate canary mode.
# It does NOT grant canary authority.
# It does NOT execute any canary plan.
# It does NOT authorize canary execution.
# It does NOT promote any candidate to canon.
# It does NOT grant runtime authority.
# It does NOT execute runtime behavior.
# It does NOT create proactive or autonomous behavior.
# It does NOT mutate runtime, scheduler, baseline, canon, or forecast weights.
# It does NOT grant AAL-Viz inference authority.
# It does NOT implement P112 behavior.

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from jsonschema import validate

from core.research_canary_authorization_draft import (
    build_research_canary_authorization_draft,
    write_research_canary_authorization_draft,
)
from scripts.research import run_research_canary_authorization_draft
from scripts.research.run_research_canary_authorization_draft import (
    P110_DEFAULT_PATH,
    _load_json_packet,
    _parse_args,
)

_AUTHORITY_LOCKS_P110 = {
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
    "canary_authorization": False,
}

_PLAN_REVIEW_COMPLETE_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P110_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchCanaryPlanReviewRecord.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P110_RESEARCH_CANARY_PLAN_REVIEW_RECORD",
    "status": "CANARY_PLAN_REVIEW_RECORD_EMITTED",
    "upstream_lane_id": "P109_RESEARCH_CANARY_PLAN_DRAFT",
    "upstream_canary_plan_draft_status": "CANARY_PLAN_DRAFT_EMITTED",
    "canary_plan_review_record_status": "CANARY_PLAN_REVIEW_COMPLETE",
    "stabilized_candidates": list(_PLAN_REVIEW_COMPLETE_CANDIDATES),
    "held_candidates": ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"],
    "repair_candidates": ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"],
    "rejected_candidates": ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"],
    "analyzed_candidates": list(_PLAN_REVIEW_COMPLETE_CANDIDATES),
    "plan_review_complete_candidates": list(_PLAN_REVIEW_COMPLETE_CANDIDATES),
    "plan_review_incomplete_candidates": [],
    "candidate_plan_review_statuses": [],
    "required_plan_review_observations": [],
    "missing_plan_review_requirements": {},
    "authority_locks": dict(_AUTHORITY_LOCKS_P110),
    "recommended_next_lane": "P111_RESEARCH_CANARY_AUTHORIZATION_DRAFT",
    "recommended_next_lane_reason": "Proceed to P111.",
    "not_computable_reasons": [],
    "provenance": {"source": "p109"},
    "packet_hash": "a" * 64,
}


def _authorization_draft_observations() -> dict[str, Any]:
    return {
        "candidate_authorization_draft_observations": {
            candidate_id: {
                "candidate_id": candidate_id,
                "plan_review_complete_observed": True,
                "authorization_scope_defined": True,
                "authorization_conditions_defined": True,
                "rollback_binding_defined": True,
                "monitoring_binding_defined": True,
                "blast_radius_binding_defined": True,
                "exit_criteria_binding_defined": True,
                "operator_authorization_required": True,
                "execution_disabled_confirmed": True,
                "provenance_bundle_attached": True,
                "authority_drift_observed": False,
                "notes": "authorization draft observations captured",
            }
            for candidate_id in _PLAN_REVIEW_COMPLETE_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_canary_authorization_draft.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


def test_deterministic_output_across_repeated_runs() -> None:
    observations = _authorization_draft_observations()
    first = build_research_canary_authorization_draft(
        p110_packet=_VALID_P110_PACKET,
        authorization_draft_observations_packet=observations,
    )
    second = build_research_canary_authorization_draft(
        p110_packet=_VALID_P110_PACKET,
        authorization_draft_observations_packet=observations,
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_schema_validates_representative_complete_packet() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet=_VALID_P110_PACKET,
        authorization_draft_observations_packet=_authorization_draft_observations(),
    )
    validate(packet, _schema())


def test_schema_validates_representative_continue_packet() -> None:
    packet = build_research_canary_authorization_draft(p110_packet=_VALID_P110_PACKET)
    validate(packet, _schema())


def test_schema_validates_representative_failure_packet() -> None:
    packet = build_research_canary_authorization_draft(p110_packet=None)
    validate(packet, _schema())


def test_p110_missing_returns_not_computable() -> None:
    packet = build_research_canary_authorization_draft(p110_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p110_packet_missing" in packet["not_computable_reasons"]


def test_malformed_p110_returns_not_computable() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet="bad"  # type: ignore[arg-type]
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["not_computable_reasons"] == ["p110_packet_malformed:not_a_dict"]


def test_wrong_chain_p110_returns_not_computable() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet={**_VALID_P110_PACKET, "recommended_next_lane": "P999_WRONG"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p110_recommendation_chain_mismatch" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_non_emitted_non_pass_p110_returns_not_computable() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet={
            **_VALID_P110_PACKET,
            "status": "NOT_COMPUTABLE",
            "canary_plan_review_record_status": "NOT_COMPUTABLE",
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p110_status_not_emitted" in reason for reason in packet["not_computable_reasons"]
    )


def test_p110_without_p111_recommendation_never_recommends_p112() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet={
            **_VALID_P110_PACKET,
            "recommended_next_lane": "P110_RESEARCH_CANARY_PLAN_REVIEW_RECORD_CONTINUE",
        },
        authorization_draft_observations_packet=_authorization_draft_observations(),
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert (
        packet["recommended_next_lane"]
        != "P112_RESEARCH_CANARY_AUTHORIZATION_REVIEW_RECORD"
    )


def test_no_plan_review_complete_candidates_returns_not_computable() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet={**_VALID_P110_PACKET, "plan_review_complete_candidates": []}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p110_no_plan_review_complete_candidates" in packet["not_computable_reasons"]


def test_p110_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet={
            **_VALID_P110_PACKET,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "canary_plan_review_record_status": "CANARY_PLAN_REVIEW_REJECTED_AUTHORITY_DRIFT",
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_p110_authority_lock_true_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet={
            **_VALID_P110_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS_P110, "canary_authority": True},
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_authorization_observation_authority_drift_returns_rejected_authority_drift() -> (
    None
):
    observations = _authorization_draft_observations()
    first_candidate = _PLAN_REVIEW_COMPLETE_CANDIDATES[0]
    observations["candidate_authorization_draft_observations"][first_candidate][
        "authority_drift_observed"
    ] = True
    packet = build_research_canary_authorization_draft(
        p110_packet=_VALID_P110_PACKET,
        authorization_draft_observations_packet=observations,
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_default_missing_authorization_observations_recommend_p111_continue() -> None:
    packet = build_research_canary_authorization_draft(p110_packet=_VALID_P110_PACKET)
    assert packet["status"] == "CANARY_AUTHORIZATION_DRAFT_EMITTED"
    assert packet["canary_authorization_draft_status"] == "CANARY_AUTHORIZATION_DRAFT_INCOMPLETE"
    assert (
        packet["recommended_next_lane"]
        == "P111_RESEARCH_CANARY_AUTHORIZATION_DRAFT_CONTINUE"
    )
    for candidate_status in packet["candidate_authorization_draft_statuses"]:
        assert (
            candidate_status["canary_authorization_draft_status"]
            == "CANARY_AUTHORIZATION_DRAFT_INCOMPLETE"
        )


def test_complete_authorization_observations_for_every_candidate_recommend_p112() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet=_VALID_P110_PACKET,
        authorization_draft_observations_packet=_authorization_draft_observations(),
    )
    assert packet["status"] == "CANARY_AUTHORIZATION_DRAFT_EMITTED"
    assert packet["canary_authorization_draft_status"] == "CANARY_AUTHORIZATION_DRAFT_COMPLETE"
    assert packet["recommended_next_lane"] == "P112_RESEARCH_CANARY_AUTHORIZATION_REVIEW_RECORD"
    for candidate_status in packet["candidate_authorization_draft_statuses"]:
        assert (
            candidate_status["canary_authorization_draft_status"]
            == "CANARY_AUTHORIZATION_DRAFT_COMPLETE"
        )


@pytest.mark.parametrize(
    "missing_field",
    [
        "plan_review_complete_observed",
        "authorization_scope_defined",
        "authorization_conditions_defined",
        "rollback_binding_defined",
        "monitoring_binding_defined",
        "blast_radius_binding_defined",
        "exit_criteria_binding_defined",
        "operator_authorization_required",
        "provenance_bundle_attached",
    ],
)
def test_missing_required_authorization_observation_blocks_p112(
    missing_field: str,
) -> None:
    observations = _authorization_draft_observations()
    for candidate_id in _PLAN_REVIEW_COMPLETE_CANDIDATES:
        observations["candidate_authorization_draft_observations"][candidate_id][
            missing_field
        ] = False
    packet = build_research_canary_authorization_draft(
        p110_packet=_VALID_P110_PACKET,
        authorization_draft_observations_packet=observations,
    )
    assert (
        packet["recommended_next_lane"]
        != "P112_RESEARCH_CANARY_AUTHORIZATION_REVIEW_RECORD"
    )
    for candidate_status in packet["candidate_authorization_draft_statuses"]:
        assert (
            candidate_status["canary_authorization_draft_status"]
            == "CANARY_AUTHORIZATION_DRAFT_INCOMPLETE"
        )
        assert any(
            missing_field in requirement
            for requirement in candidate_status["missing_authorization_draft_requirements"]
        )


def test_execution_disabled_confirmed_false_blocks_p112() -> None:
    observations = _authorization_draft_observations()
    for candidate_id in _PLAN_REVIEW_COMPLETE_CANDIDATES:
        observations["candidate_authorization_draft_observations"][candidate_id][
            "execution_disabled_confirmed"
        ] = False
    packet = build_research_canary_authorization_draft(
        p110_packet=_VALID_P110_PACKET,
        authorization_draft_observations_packet=observations,
    )
    assert (
        packet["recommended_next_lane"]
        != "P112_RESEARCH_CANARY_AUTHORIZATION_REVIEW_RECORD"
    )
    for candidate_status in packet["candidate_authorization_draft_statuses"]:
        assert any(
            "execution_disabled_confirmed" in requirement
            for requirement in candidate_status["missing_authorization_draft_requirements"]
        )


def test_held_repair_rejected_candidates_from_upstream_are_preserved_separately() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet=_VALID_P110_PACKET,
        authorization_draft_observations_packet=_authorization_draft_observations(),
    )
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]
    assert packet["repair_candidates"] == [
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"
    ]
    assert packet["rejected_candidates"] == [
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"
    ]


def test_only_plan_review_complete_candidates_are_analyzed() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet={
            **_VALID_P110_PACKET,
            "plan_review_complete_candidates": [_PLAN_REVIEW_COMPLETE_CANDIDATES[0]],
        },
        authorization_draft_observations_packet=_authorization_draft_observations(),
    )
    assert packet["analyzed_candidates"] == [_PLAN_REVIEW_COMPLETE_CANDIDATES[0]]
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]


def test_all_authority_locks_remain_false_including_required_canary_locks() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet=_VALID_P110_PACKET,
        authorization_draft_observations_packet=_authorization_draft_observations(),
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
        "canary_authorization_execution",
    }
    assert set(locks.keys()) == expected_keys
    for key, value in locks.items():
        assert value is False, f"authority_lock {key!r} must be False, got {value!r}"


def test_packet_hash_is_deterministic_and_excludes_itself() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet=_VALID_P110_PACKET,
        authorization_draft_observations_packet=_authorization_draft_observations(),
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


def test_output_writer_emits_canonical_json_with_trailing_newline() -> None:
    packet = build_research_canary_authorization_draft(
        p110_packet=_VALID_P110_PACKET,
        authorization_draft_observations_packet=_authorization_draft_observations(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        write_research_canary_authorization_draft(out_path, packet)
        content = out_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    parsed = json.loads(content)
    assert parsed == packet


def test_runner_default_p110_path() -> None:
    args = _parse_args([])
    assert args.p110_path == str(P110_DEFAULT_PATH)
    assert args.authorization_draft_observations_path is None


def test_runner_supports_p110_path_flag() -> None:
    args = _parse_args(["--p110-path", "/some/path/latest.json"])
    assert args.p110_path == "/some/path/latest.json"


def test_runner_supports_authorization_draft_observations_path_flag() -> None:
    args = _parse_args(
        ["--authorization-draft-observations-path", "/some/observations.json"]
    )
    assert args.authorization_draft_observations_path == "/some/observations.json"


def test_runner_load_json_packet_missing_file_returns_none() -> None:
    result = _load_json_packet("/nonexistent/path/latest.json")
    assert result is None


def test_runner_load_json_packet_none_returns_none() -> None:
    result = _load_json_packet(None)
    assert result is None


def test_runner_run_writes_output_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        packet = run_research_canary_authorization_draft.run(
            p110_packet=_VALID_P110_PACKET,
            authorization_draft_observations_packet=_authorization_draft_observations(),
            out_path=out_path,
        )
        assert out_path.exists()
        written = json.loads(out_path.read_text(encoding="utf-8"))
        assert written == packet
        assert written["status"] == "CANARY_AUTHORIZATION_DRAFT_EMITTED"


def test_out_validation_latest_json_untouched() -> None:
    path = Path("out/validation/latest.json")
    assert path.exists(), "out/validation/latest.json must exist"
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_authorization_draft(p110_packet=None)
    content_after = path.read_text(encoding="utf-8")
    assert content_before == content_after


def test_out_projections_aal_viz_latest_json_untouched() -> None:
    path = Path("out/projections/aal_viz.latest.json")
    assert path.exists(), "out/projections/aal_viz.latest.json must exist"
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_authorization_draft(p110_packet=None)
    content_after = path.read_text(encoding="utf-8")
    assert content_before == content_after
