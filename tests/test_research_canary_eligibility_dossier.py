from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from jsonschema import validate

from core.research_canary_eligibility_dossier import (
    build_research_canary_eligibility_dossier,
    write_research_canary_eligibility_dossier,
)
from scripts.research import run_research_canary_eligibility_dossier
from scripts.research.run_research_canary_eligibility_dossier import (
    P105_DEFAULT_PATH,
    _load_json_packet,
    _parse_args,
)

_AUTHORITY_LOCKS_P105 = {
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

_BLOCKER_REVIEW_COMPLETE_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P105_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchPromotionBlockerLedger.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER",
    "status": "PROMOTION_BLOCKER_LEDGER_EMITTED",
    "upstream_lane_id": "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS",
    "upstream_boundary_decay_analysis_status": "BOUNDARY_DECAY_ANALYSIS_EMITTED",
    "promotion_blocker_ledger_status": "EMITTED",
    "stabilized_candidates": list(_BLOCKER_REVIEW_COMPLETE_CANDIDATES),
    "held_candidates": ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"],
    "repair_candidates": ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"],
    "rejected_candidates": ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"],
    "analyzed_candidates": list(_BLOCKER_REVIEW_COMPLETE_CANDIDATES),
    "promotion_blocked_candidates": [],
    "blocker_review_complete_candidates": list(_BLOCKER_REVIEW_COMPLETE_CANDIDATES),
    "blocker_review_incomplete_candidates": [],
    "candidate_blocker_statuses": [],
    "mandatory_blocker_categories": [],
    "missing_blocker_requirements": {},
    "authority_locks": dict(_AUTHORITY_LOCKS_P105),
    "recommended_next_lane": "P106_RESEARCH_CANARY_ELIGIBILITY_DOSSIER",
    "recommended_next_lane_reason": "Proceed to P106.",
    "not_computable_reasons": [],
    "provenance": {"source": "p104"},
    "packet_hash": "a" * 64,
}


def _complete_eligibility_observations() -> dict[str, Any]:
    return {
        "candidate_eligibility_observations": {
            candidate_id: {
                "candidate_id": candidate_id,
                "blocker_review_complete_observed": True,
                "operator_review_observed": True,
                "provenance_complete_observed": True,
                "replay_stability_observed": True,
                "boundary_stability_observed": True,
                "canary_scope_defined": True,
                "rollback_plan_defined": True,
                "monitoring_plan_defined": True,
                "blast_radius_defined": True,
                "exit_criteria_defined": True,
                "authority_drift_observed": False,
                "notes": "all eligibility criteria confirmed",
            }
            for candidate_id in _BLOCKER_REVIEW_COMPLETE_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_canary_eligibility_dossier.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_output_across_repeated_runs() -> None:
    observations = _complete_eligibility_observations()
    first = build_research_canary_eligibility_dossier(
        p105_packet=_VALID_P105_PACKET,
        eligibility_observations_packet=observations,
    )
    second = build_research_canary_eligibility_dossier(
        p105_packet=_VALID_P105_PACKET,
        eligibility_observations_packet=observations,
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def test_schema_validates_representative_eligible_packet() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet=_VALID_P105_PACKET,
        eligibility_observations_packet=_complete_eligibility_observations(),
    )
    validate(packet, _schema())


def test_schema_validates_representative_continue_packet() -> None:
    packet = build_research_canary_eligibility_dossier(p105_packet=_VALID_P105_PACKET)
    validate(packet, _schema())


def test_schema_validates_representative_failure_packet() -> None:
    packet = build_research_canary_eligibility_dossier(p105_packet=None)
    validate(packet, _schema())


# ---------------------------------------------------------------------------
# NOT_COMPUTABLE cases
# ---------------------------------------------------------------------------


def test_p105_missing_returns_not_computable() -> None:
    packet = build_research_canary_eligibility_dossier(p105_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p105_packet_missing" in packet["not_computable_reasons"]


def test_malformed_p105_returns_not_computable() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet="bad"  # type: ignore[arg-type]
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["not_computable_reasons"] == ["p105_packet_malformed:not_a_dict"]


def test_wrong_chain_p105_returns_not_computable() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet={**_VALID_P105_PACKET, "recommended_next_lane": "P999_WRONG"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p105_recommendation_chain_mismatch" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_non_emitted_non_pass_p105_returns_not_computable() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet={
            **_VALID_P105_PACKET,
            "status": "NOT_COMPUTABLE",
            "promotion_blocker_ledger_status": "NOT_COMPUTABLE",
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p105_status_not_emitted" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_p105_without_p106_recommendation_never_recommends_p107() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet={
            **_VALID_P105_PACKET,
            "recommended_next_lane": "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER_CONTINUE",
        },
        eligibility_observations_packet=_complete_eligibility_observations(),
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] != "P107_RESEARCH_CANARY_REVIEW_PACKET"


def test_no_blocker_review_complete_candidates_returns_not_computable() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet={**_VALID_P105_PACKET, "blocker_review_complete_candidates": []}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert (
        "p105_no_blocker_review_complete_candidates" in packet["not_computable_reasons"]
    )


# ---------------------------------------------------------------------------
# REJECTED_AUTHORITY_DRIFT cases
# ---------------------------------------------------------------------------


def test_p105_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet={
            **_VALID_P105_PACKET,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "promotion_blocker_ledger_status": "REJECTED_AUTHORITY_DRIFT",
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_eligibility_observation_authority_drift_returns_rejected_authority_drift() -> None:
    observations = _complete_eligibility_observations()
    first_candidate = _BLOCKER_REVIEW_COMPLETE_CANDIDATES[0]
    observations["candidate_eligibility_observations"][first_candidate][
        "authority_drift_observed"
    ] = True
    packet = build_research_canary_eligibility_dossier(
        p105_packet=_VALID_P105_PACKET,
        eligibility_observations_packet=observations,
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


# ---------------------------------------------------------------------------
# Recommendation routing
# ---------------------------------------------------------------------------


def test_default_missing_eligibility_observations_recommend_p106_continue() -> None:
    packet = build_research_canary_eligibility_dossier(p105_packet=_VALID_P105_PACKET)
    assert packet["status"] == "CANARY_ELIGIBILITY_DOSSIER_EMITTED"
    assert (
        packet["recommended_next_lane"]
        == "P106_RESEARCH_CANARY_ELIGIBILITY_DOSSIER_CONTINUE"
    )
    for cs in packet["candidate_eligibility_statuses"]:
        assert (
            cs["canary_eligibility_status"]
            == "CANARY_ELIGIBILITY_BLOCKED_MISSING_OBSERVATIONS"
        )


def test_complete_eligibility_observations_for_every_candidate_recommend_p107() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet=_VALID_P105_PACKET,
        eligibility_observations_packet=_complete_eligibility_observations(),
    )
    assert packet["status"] == "CANARY_ELIGIBILITY_DOSSIER_EMITTED"
    assert packet["recommended_next_lane"] == "P107_RESEARCH_CANARY_REVIEW_PACKET"
    for cs in packet["candidate_eligibility_statuses"]:
        assert cs["canary_eligibility_status"] == "CANARY_DOSSIER_ELIGIBLE"


@pytest.mark.parametrize(
    "missing_field",
    [
        "rollback_plan_defined",
        "monitoring_plan_defined",
        "blast_radius_defined",
        "exit_criteria_defined",
        "canary_scope_defined",
        "operator_review_observed",
    ],
)
def test_missing_criteria_blocks_p107(missing_field: str) -> None:
    observations = _complete_eligibility_observations()
    for candidate_id in _BLOCKER_REVIEW_COMPLETE_CANDIDATES:
        observations["candidate_eligibility_observations"][candidate_id][
            missing_field
        ] = False
    packet = build_research_canary_eligibility_dossier(
        p105_packet=_VALID_P105_PACKET,
        eligibility_observations_packet=observations,
    )
    assert packet["status"] == "CANARY_ELIGIBILITY_DOSSIER_EMITTED"
    assert (
        packet["recommended_next_lane"]
        != "P107_RESEARCH_CANARY_REVIEW_PACKET"
    )
    for cs in packet["candidate_eligibility_statuses"]:
        assert cs["canary_eligibility_status"] == "CANARY_ELIGIBILITY_INCOMPLETE"
        assert any(
            missing_field in req
            for req in cs["missing_eligibility_requirements"]
        )


# ---------------------------------------------------------------------------
# Candidate list preservation
# ---------------------------------------------------------------------------


def test_held_repair_rejected_candidates_are_preserved_separately() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet=_VALID_P105_PACKET,
        eligibility_observations_packet=_complete_eligibility_observations(),
    )
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]
    assert packet["repair_candidates"] == [
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"
    ]
    assert packet["rejected_candidates"] == [
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"
    ]


def test_only_blocker_review_complete_candidates_are_analyzed() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet=_VALID_P105_PACKET,
        eligibility_observations_packet=_complete_eligibility_observations(),
    )
    analyzed = set(packet["analyzed_candidates"])
    assert analyzed == set(_BLOCKER_REVIEW_COMPLETE_CANDIDATES)
    held = set(packet["held_candidates"])
    repair = set(packet["repair_candidates"])
    rejected = set(packet["rejected_candidates"])
    assert not analyzed.intersection(held | repair | rejected)


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------


def test_all_authority_locks_remain_false_including_canary_activation() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet=_VALID_P105_PACKET,
        eligibility_observations_packet=_complete_eligibility_observations(),
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
    }
    assert set(locks.keys()) == expected_keys
    for key, value in locks.items():
        assert value is False, f"authority_lock {key!r} must be False, got {value!r}"


def test_canary_activation_lock_false_on_not_computable() -> None:
    packet = build_research_canary_eligibility_dossier(p105_packet=None)
    assert packet["authority_locks"]["canary_activation"] is False


def test_canary_activation_lock_false_on_rejected_authority_drift() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet={
            **_VALID_P105_PACKET,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "promotion_blocker_ledger_status": "REJECTED_AUTHORITY_DRIFT",
        }
    )
    assert packet["authority_locks"]["canary_activation"] is False


# ---------------------------------------------------------------------------
# Packet hash
# ---------------------------------------------------------------------------


def test_packet_hash_is_deterministic_and_excludes_itself() -> None:
    packet = build_research_canary_eligibility_dossier(
        p105_packet=_VALID_P105_PACKET,
        eligibility_observations_packet=_complete_eligibility_observations(),
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
    packet = build_research_canary_eligibility_dossier(
        p105_packet=_VALID_P105_PACKET,
        eligibility_observations_packet=_complete_eligibility_observations(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        write_research_canary_eligibility_dossier(out_path, packet)
        content = out_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    parsed = json.loads(content)
    assert parsed == packet


# ---------------------------------------------------------------------------
# Runner CLI
# ---------------------------------------------------------------------------


def test_runner_default_p105_path() -> None:
    args = _parse_args([])
    assert args.p105_path == str(P105_DEFAULT_PATH)
    assert args.eligibility_observations_path is None


def test_runner_supports_p105_path_flag() -> None:
    args = _parse_args(["--p105-path", "/some/path/latest.json"])
    assert args.p105_path == "/some/path/latest.json"


def test_runner_supports_eligibility_observations_path_flag() -> None:
    args = _parse_args(
        ["--eligibility-observations-path", "/some/observations.json"]
    )
    assert args.eligibility_observations_path == "/some/observations.json"


def test_runner_load_json_packet_missing_file_returns_none() -> None:
    result = _load_json_packet("/nonexistent/path/latest.json")
    assert result is None


def test_runner_load_json_packet_none_returns_none() -> None:
    result = _load_json_packet(None)
    assert result is None


def test_runner_run_writes_output_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        packet = run_research_canary_eligibility_dossier.run(
            p105_packet=_VALID_P105_PACKET,
            eligibility_observations_packet=_complete_eligibility_observations(),
            out_path=out_path,
        )
        assert out_path.exists()
        written = json.loads(out_path.read_text(encoding="utf-8"))
        assert written == packet
        assert written["status"] == "CANARY_ELIGIBILITY_DOSSIER_EMITTED"


# ---------------------------------------------------------------------------
# Generated out/ artifacts remain untouched
# ---------------------------------------------------------------------------


def test_out_validation_latest_json_untouched() -> None:
    path = Path("out/validation/latest.json")
    assert path.exists(), "out/validation/latest.json must exist"
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_eligibility_dossier(p105_packet=None)
    content_after = path.read_text(encoding="utf-8")
    assert content_before == content_after


def test_out_projections_aal_viz_latest_json_untouched() -> None:
    path = Path("out/projections/aal_viz.latest.json")
    assert path.exists(), "out/projections/aal_viz.latest.json must exist"
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_eligibility_dossier(p105_packet=None)
    content_after = path.read_text(encoding="utf-8")
    assert content_before == content_after


# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P106 is advisory-only and projection-only.
# It does NOT activate canary mode.
# It does NOT promote any candidate to canon.
# It does NOT grant runtime authority.
# It does NOT mutate the scheduler, forecast weights, or baseline.
# canary_activation authority lock is always False.
# P106 may only recommend P107_RESEARCH_CANARY_REVIEW_PACKET (advisory only),
#   never canary activation.
# AAL-Viz remains projection-only throughout.
# ---------------------------------------------------------------------------
