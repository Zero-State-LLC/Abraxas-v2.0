from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# These tests verify P126 remains advisory-only and projection-only.
# They do NOT create activation envelope behavior, activate canary mode,
# execute any canary plan, grant runtime authority, or implement P127.

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from jsonschema import validate

from core.research_canary_activation_denial_hold_routing import (
    build_research_canary_activation_denial_hold_routing,
    write_research_canary_activation_denial_hold_routing,
)
from scripts import run_research_canary_activation_denial_hold_routing
from scripts.run_research_canary_activation_denial_hold_routing import (
    P125_DEFAULT_PATH,
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
    "canary_activation": False,
    "canary_authority": False,
    "canary_plan_execution": False,
    "canary_authorization": False,
    "canary_authorization_execution": False,
    "canary_final_precheck_authority": False,
    "canary_package_authority": False,
    "canary_package_execution": False,
    "canary_runtime_envelope_authority": False,
    "canary_runtime_execution": False,
    "canary_runtime_control": False,
    "rollback_execution_authority": False,
    "termination_execution_authority": False,
    "activation_package_authority": False,
    "activation_package_execution": False,
    "activation_decision_authority": False,
    "activation_execution_authority": False,
    "activation_envelope_authority": False,
}

_ANALYZED_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P125_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchCanaryActivationDecisionReviewRecord.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P125_RESEARCH_CANARY_ACTIVATION_DECISION_REVIEW_RECORD",
    "status": "CANARY_ACTIVATION_DECISION_REVIEW_RECORD_EMITTED",
    "upstream_lane_id": "P124_RESEARCH_CANARY_ACTIVATION_DECISION_RECORD",
    "upstream_status": "CANARY_ACTIVATION_DECISION_RECORD_EMITTED",
    "upstream_lane_status": "CANARY_ACTIVATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING",
    "lane_status": "CANARY_ACTIVATION_DECISION_REVIEW_COMPLETE",
    "stabilized_candidates": list(_ANALYZED_CANDIDATES),
    "held_candidates": ["HOLD_KEEP"],
    "repair_candidates": ["REPAIR_KEEP"],
    "rejected_candidates": ["REJECT_KEEP"],
    "analyzed_candidates": list(_ANALYZED_CANDIDATES),
    "candidate_statuses": [
        {
            "candidate_id": candidate_id,
            "activation_decision": "approve_for_activation_envelope_planning",
            "activation_decision_record_observed": "approve_for_activation_envelope_planning",
            "activation_decision_review_complete": True,
            "denial_review_recorded": False,
            "hold_review_recorded": False,
            "repair_review_recorded": False,
            "approval_review_recorded": True,
            "activation_disabled_review_confirmed": True,
            "execution_disabled_review_confirmed": True,
            "runtime_control_disabled_review_confirmed": True,
            "provenance_review_complete": True,
            "authority_drift_observed": False,
            "missing_requirements": [],
            "canary_activation_decision_review_status": "CANARY_ACTIVATION_DECISION_REVIEW_COMPLETE",
        }
        for candidate_id in _ANALYZED_CANDIDATES
    ],
    "missing_requirements": {},
    "authority_locks": dict(_AUTHORITY_LOCKS),
    "recommended_next_lane": "P126_RESEARCH_CANARY_ACTIVATION_DENIAL_HOLD_ROUTING",
    "recommended_next_lane_reason": "Proceed to P126.",
    "not_computable_reasons": [],
    "provenance": {"source": "p124"},
    "packet_hash": "a" * 64,
}


def _observations(
    decision: str = "approve_for_activation_envelope_planning",
) -> dict[str, Any]:
    return {
        "candidate_activation_routing_observations": {
            candidate_id: {
                "candidate_id": candidate_id,
                "activation_decision_review_observed": decision,
                "denial_route_recorded": decision == "deny_activation",
                "hold_route_recorded": decision == "hold_activation",
                "repair_route_recorded": decision == "request_activation_repair",
                "approval_route_recorded": decision
                == "approve_for_activation_envelope_planning",
                "operator_routing_review_observed": True,
                "provenance_bundle_attached": True,
                "activation_envelope_disabled_confirmed": True,
                "activation_disabled_confirmed": True,
                "execution_disabled_confirmed": True,
                "runtime_control_disabled_confirmed": True,
                "authority_drift_observed": False,
                "notes": "activation routing evidence captured",
            }
            for candidate_id in _ANALYZED_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_canary_activation_denial_hold_routing.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


def test_deterministic_output_across_repeated_runs() -> None:
    first = build_research_canary_activation_denial_hold_routing(
        p125_packet=_VALID_P125_PACKET,
        activation_routing_observations_packet=_observations(),
    )
    second = build_research_canary_activation_denial_hold_routing(
        p125_packet=_VALID_P125_PACKET,
        activation_routing_observations_packet=_observations(),
    )
    assert first == second


def test_schema_validates_representative_complete_continue_failure_packets() -> None:
    validate(
        build_research_canary_activation_denial_hold_routing(
            p125_packet=_VALID_P125_PACKET,
            activation_routing_observations_packet=_observations(),
        ),
        _schema(),
    )
    validate(
        build_research_canary_activation_denial_hold_routing(p125_packet=_VALID_P125_PACKET),
        _schema(),
    )
    validate(build_research_canary_activation_denial_hold_routing(p125_packet=None), _schema())


def test_missing_malformed_non_emitted_non_pass_wrong_chain_no_reviewed_decisions_returns_not_computable() -> (
    None
):
    assert build_research_canary_activation_denial_hold_routing(p125_packet=None)[
        "status"
    ] == "NOT_COMPUTABLE"
    assert build_research_canary_activation_denial_hold_routing(
        p125_packet="bad"  # type: ignore[arg-type]
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_activation_denial_hold_routing(
        p125_packet={**_VALID_P125_PACKET, "status": "NOT_COMPUTABLE"}
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_activation_denial_hold_routing(
        p125_packet={
            **_VALID_P125_PACKET,
            "lane_status": "CANARY_ACTIVATION_DECISION_REVIEW_INCOMPLETE",
        }
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_activation_denial_hold_routing(
        p125_packet={**_VALID_P125_PACKET, "recommended_next_lane": "P125_CONTINUE"}
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_activation_denial_hold_routing(
        p125_packet={**_VALID_P125_PACKET, "analyzed_candidates": []}
    )["status"] == "NOT_COMPUTABLE"


def test_upstream_without_expected_recommendation_never_recommends_p127() -> None:
    packet = build_research_canary_activation_denial_hold_routing(
        p125_packet={**_VALID_P125_PACKET, "recommended_next_lane": "P125_CONTINUE"},
        activation_routing_observations_packet=_observations(),
    )
    assert packet["recommended_next_lane"] != "P127_RESEARCH_CANARY_ACTIVATION_ENVELOPE_DRAFT"


def test_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_activation_denial_hold_routing(
        p125_packet={**_VALID_P125_PACKET, "status": "REJECTED_AUTHORITY_DRIFT"}
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_default_missing_observations_continue_current_lane() -> None:
    packet = build_research_canary_activation_denial_hold_routing(
        p125_packet=_VALID_P125_PACKET
    )
    assert packet["recommended_next_lane"] == (
        "P126_RESEARCH_CANARY_ACTIVATION_DENIAL_HOLD_ROUTING_CONTINUE"
    )


def test_complete_observations_recommend_p127_only_when_all_approved() -> None:
    packet = build_research_canary_activation_denial_hold_routing(
        p125_packet=_VALID_P125_PACKET,
        activation_routing_observations_packet=_observations(),
    )
    assert packet["recommended_next_lane"] == "P127_RESEARCH_CANARY_ACTIVATION_ENVELOPE_DRAFT"


@pytest.mark.parametrize(
    "missing_field",
    [
        "operator_routing_review_observed",
        "provenance_bundle_attached",
        "activation_envelope_disabled_confirmed",
        "activation_disabled_confirmed",
        "execution_disabled_confirmed",
        "runtime_control_disabled_confirmed",
    ],
)
def test_missing_required_fields_block_advancement(missing_field: str) -> None:
    observations = _observations()
    for candidate_id in _ANALYZED_CANDIDATES:
        observations["candidate_activation_routing_observations"][candidate_id][
            missing_field
        ] = False
    packet = build_research_canary_activation_denial_hold_routing(
        p125_packet=_VALID_P125_PACKET,
        activation_routing_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] != "P127_RESEARCH_CANARY_ACTIVATION_ENVELOPE_DRAFT"


@pytest.mark.parametrize(
    ("decision", "bucket"),
    [
        ("deny_activation", "denied_activation_candidates"),
        ("hold_activation", "held_activation_candidates"),
        ("request_activation_repair", "activation_repair_requested_candidates"),
        (
            "approve_for_activation_envelope_planning",
            "approved_for_activation_envelope_planning_candidates",
        ),
    ],
)
def test_denied_held_repair_approved_partitions_preserved(
    decision: str,
    bucket: str,
) -> None:
    packet = build_research_canary_activation_denial_hold_routing(
        p125_packet={
            **_VALID_P125_PACKET,
            "candidate_statuses": [
                {
                    "candidate_id": candidate_id,
                    "activation_decision": decision,
                }
                for candidate_id in _ANALYZED_CANDIDATES
            ],
        },
        activation_routing_observations_packet=_observations(decision=decision),
    )
    assert set(packet[bucket]) == set(_ANALYZED_CANDIDATES)


def test_held_repair_rejected_upstream_partitions_preserved_separately() -> None:
    packet = build_research_canary_activation_denial_hold_routing(
        p125_packet=_VALID_P125_PACKET,
        activation_routing_observations_packet=_observations(),
    )
    assert packet["held_candidates"] == ["HOLD_KEEP"]
    assert packet["repair_candidates"] == ["REPAIR_KEEP"]
    assert packet["rejected_candidates"] == ["REJECT_KEEP"]


def test_only_candidates_included_in_p125_decision_review_output_are_analyzed() -> None:
    packet = build_research_canary_activation_denial_hold_routing(
        p125_packet={
            **_VALID_P125_PACKET,
            "analyzed_candidates": [_ANALYZED_CANDIDATES[0]],
            "candidate_statuses": [
                {
                    "candidate_id": _ANALYZED_CANDIDATES[0],
                    "activation_decision": "approve_for_activation_envelope_planning",
                }
            ],
        },
        activation_routing_observations_packet=_observations(),
    )
    assert packet["analyzed_candidates"] == [_ANALYZED_CANDIDATES[0]]


def test_all_authority_locks_remain_false_including_activation_decision_execution_envelope() -> (
    None
):
    packet = build_research_canary_activation_denial_hold_routing(
        p125_packet=_VALID_P125_PACKET,
        activation_routing_observations_packet=_observations(),
    )
    assert packet["authority_locks"].get("activation_decision_authority") is False
    assert packet["authority_locks"].get("activation_execution_authority") is False
    assert packet["authority_locks"].get("activation_envelope_authority") is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_packet_hash_deterministic_and_excludes_itself() -> None:
    packet = build_research_canary_activation_denial_hold_routing(
        p125_packet=_VALID_P125_PACKET,
        activation_routing_observations_packet=_observations(),
    )
    base_without_hash = {k: v for k, v in packet.items() if k != "packet_hash"}
    serialized = json.dumps(
        base_without_hash,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    assert packet["packet_hash"] == hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def test_output_writer_emits_canonical_json_with_trailing_newline() -> None:
    packet = build_research_canary_activation_denial_hold_routing(
        p125_packet=_VALID_P125_PACKET,
        activation_routing_observations_packet=_observations(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        write_research_canary_activation_denial_hold_routing(out_path, packet)
        content = out_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert json.loads(content) == packet


def test_runner_flags_and_loader() -> None:
    args = _parse_args([])
    assert args.p125_path == str(P125_DEFAULT_PATH)
    assert args.activation_routing_observations_path is None
    args = _parse_args(["--p125-path", "/tmp/p125.json"])
    assert args.p125_path == "/tmp/p125.json"
    args = _parse_args(["--activation-routing-observations-path", "/tmp/o.json"])
    assert args.activation_routing_observations_path == "/tmp/o.json"
    assert _load_json_packet("/nonexistent/path/latest.json") is None
    assert _load_json_packet(None) is None


def test_runner_run_writes_output_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        packet = run_research_canary_activation_denial_hold_routing.run(
            p125_packet=_VALID_P125_PACKET,
            activation_routing_observations_packet=_observations(),
            out_path=out_path,
        )
        assert out_path.exists()
        assert json.loads(out_path.read_text(encoding="utf-8")) == packet


def test_out_validation_latest_json_untouched() -> None:
    path = Path("out/validation/latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_activation_denial_hold_routing(p125_packet=None)
    assert path.read_text(encoding="utf-8") == content_before


def test_out_projections_aal_viz_latest_json_untouched() -> None:
    path = Path("out/projections/aal_viz.latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_activation_denial_hold_routing(p125_packet=None)
    assert path.read_text(encoding="utf-8") == content_before
