from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# These tests verify P117 remains advisory-only and projection-only.
# They do NOT create runtime envelope behavior, authorize activation, grant
# canary authority, execute canary plans, or implement P118 runtime behavior.

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from jsonschema import validate

from core.research_canary_authorization_denial_hold_routing import (
    build_research_canary_authorization_denial_hold_routing,
    write_research_canary_authorization_denial_hold_routing,
)
from scripts.research import run_research_canary_authorization_denial_hold_routing
from scripts.research.run_research_canary_authorization_denial_hold_routing import (
    P116_DEFAULT_PATH,
    _load_json_packet,
    _parse_args,
)

_AUTHORITY_LOCKS_P116 = {
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
}

_ANALYZED_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P116_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchCanaryAuthorizationDecisionRecord.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD",
    "status": "CANARY_AUTHORIZATION_DECISION_RECORD_EMITTED",
    "upstream_lane_id": "P115_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD",
    "upstream_status": "CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD_EMITTED",
    "upstream_lane_status": "CANARY_AUTHORIZATION_PACKAGE_REVIEW_COMPLETE",
    "lane_status": "CANARY_AUTHORIZATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING",
    "canary_authorization_decision_record_status": "CANARY_AUTHORIZATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING",
    "stabilized_candidates": list(_ANALYZED_CANDIDATES),
    "held_candidates": ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"],
    "repair_candidates": ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"],
    "rejected_candidates": ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"],
    "analyzed_candidates": list(_ANALYZED_CANDIDATES),
    "denied_candidates": [],
    "held_for_review_candidates": [],
    "repair_requested_candidates": [],
    "approved_for_controlled_envelope_planning_candidates": list(_ANALYZED_CANDIDATES),
    "candidate_statuses": [
        {
            "candidate_id": candidate_id,
            "decision": "approve_for_controlled_envelope_planning",
            "operator_decision_observed": True,
            "decision_rationale_attached": True,
            "package_review_complete_observed": True,
            "provenance_bundle_attached": True,
            "authority_drift_observed": False,
            "missing_requirements": [],
            "canary_authorization_decision_status": "CANARY_AUTHORIZATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING",
        }
        for candidate_id in _ANALYZED_CANDIDATES
    ],
    "candidate_authorization_decision_statuses": [],
    "missing_requirements": {},
    "missing_authorization_decision_requirements": {},
    "required_authorization_decision_observations": [],
    "allowed_decisions": [
        "deny",
        "hold",
        "request_repair",
        "approve_for_controlled_envelope_planning",
    ],
    "forbidden_decisions": ["activate_canary"],
    "authority_locks": dict(_AUTHORITY_LOCKS_P116),
    "recommended_next_lane": "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING",
    "recommended_next_lane_reason": "Proceed to P117.",
    "not_computable_reasons": [],
    "provenance": {"source": "p115"},
    "packet_hash": "a" * 64,
}


def _observations(decision: str = "approve_for_controlled_envelope_planning") -> dict[str, Any]:
    return {
        "candidate_routing_observations": {
            candidate_id: {
                "candidate_id": candidate_id,
                "authorization_decision_observed": decision,
                "denial_route_recorded": decision == "deny",
                "hold_route_recorded": decision == "hold",
                "repair_route_recorded": decision == "request_repair",
                "approval_route_recorded": decision
                == "approve_for_controlled_envelope_planning",
                "operator_routing_review_observed": True,
                "provenance_bundle_attached": True,
                "runtime_envelope_disabled_confirmed": True,
                "authority_drift_observed": False,
                "notes": "routing evidence captured",
            }
            for candidate_id in _ANALYZED_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_canary_authorization_denial_hold_routing.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


def test_deterministic_output_across_repeated_runs() -> None:
    first = build_research_canary_authorization_denial_hold_routing(
        p116_packet=_VALID_P116_PACKET,
        routing_observations_packet=_observations(),
    )
    second = build_research_canary_authorization_denial_hold_routing(
        p116_packet=_VALID_P116_PACKET,
        routing_observations_packet=_observations(),
    )
    assert first == second


def test_schema_validates_representative_packets() -> None:
    validate(
        build_research_canary_authorization_denial_hold_routing(
            p116_packet=_VALID_P116_PACKET,
            routing_observations_packet=_observations(),
        ),
        _schema(),
    )
    validate(
        build_research_canary_authorization_denial_hold_routing(
            p116_packet=_VALID_P116_PACKET
        ),
        _schema(),
    )
    validate(
        build_research_canary_authorization_denial_hold_routing(p116_packet=None),
        _schema(),
    )


def test_missing_malformed_non_emitted_wrong_chain_or_no_decisions_returns_not_computable() -> (
    None
):
    assert build_research_canary_authorization_denial_hold_routing(p116_packet=None)[
        "status"
    ] == "NOT_COMPUTABLE"
    assert build_research_canary_authorization_denial_hold_routing(
        p116_packet="bad"  # type: ignore[arg-type]
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_authorization_denial_hold_routing(
        p116_packet={**_VALID_P116_PACKET, "status": "NOT_COMPUTABLE"}
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_authorization_denial_hold_routing(
        p116_packet={
            **_VALID_P116_PACKET,
            "recommended_next_lane": "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD_CONTINUE",
        }
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_authorization_denial_hold_routing(
        p116_packet={**_VALID_P116_PACKET, "analyzed_candidates": []}
    )["status"] == "NOT_COMPUTABLE"


def test_upstream_without_expected_recommendation_never_recommends_p118() -> None:
    packet = build_research_canary_authorization_denial_hold_routing(
        p116_packet={
            **_VALID_P116_PACKET,
            "recommended_next_lane": "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD_CONTINUE",
        },
        routing_observations_packet=_observations(),
    )
    assert packet["recommended_next_lane"] != "P118_RESEARCH_CONTROLLED_CANARY_ENVELOPE_DRAFT"


def test_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_authorization_denial_hold_routing(
        p116_packet={**_VALID_P116_PACKET, "status": "REJECTED_AUTHORITY_DRIFT"}
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_default_missing_observations_continue_current_lane() -> None:
    packet = build_research_canary_authorization_denial_hold_routing(
        p116_packet=_VALID_P116_PACKET
    )
    assert packet["recommended_next_lane"] == (
        "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING_CONTINUE"
    )


def test_complete_routing_recommends_p118_only_when_all_approved() -> None:
    packet = build_research_canary_authorization_denial_hold_routing(
        p116_packet=_VALID_P116_PACKET,
        routing_observations_packet=_observations(),
    )
    assert packet["recommended_next_lane"] == "P118_RESEARCH_CONTROLLED_CANARY_ENVELOPE_DRAFT"


def test_missing_required_fields_block_advancement() -> None:
    observations = _observations()
    for candidate_id in _ANALYZED_CANDIDATES:
        observations["candidate_routing_observations"][candidate_id][
            "runtime_envelope_disabled_confirmed"
        ] = False
    packet = build_research_canary_authorization_denial_hold_routing(
        p116_packet=_VALID_P116_PACKET,
        routing_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] != "P118_RESEARCH_CONTROLLED_CANARY_ENVELOPE_DRAFT"


@pytest.mark.parametrize(
    ("decision", "bucket"),
    [
        ("deny", "denied_candidates"),
        ("hold", "held_for_review_candidates"),
        ("request_repair", "repair_requested_candidates"),
        (
            "approve_for_controlled_envelope_planning",
            "approved_for_controlled_envelope_planning_candidates",
        ),
    ],
)
def test_denied_held_repair_approved_partitions_preserved(
    decision: str,
    bucket: str,
) -> None:
    packet = build_research_canary_authorization_denial_hold_routing(
        p116_packet={
            **_VALID_P116_PACKET,
            "candidate_statuses": [
                {
                    "candidate_id": candidate_id,
                    "decision": decision,
                }
                for candidate_id in _ANALYZED_CANDIDATES
            ],
            "denied_candidates": _ANALYZED_CANDIDATES if decision == "deny" else [],
            "held_for_review_candidates": _ANALYZED_CANDIDATES if decision == "hold" else [],
            "repair_requested_candidates": _ANALYZED_CANDIDATES
            if decision == "request_repair"
            else [],
            "approved_for_controlled_envelope_planning_candidates": _ANALYZED_CANDIDATES
            if decision == "approve_for_controlled_envelope_planning"
            else [],
        },
        routing_observations_packet=_observations(decision=decision),
    )
    assert set(packet[bucket]) == set(_ANALYZED_CANDIDATES)


def test_only_candidates_included_in_p116_decision_output_are_analyzed() -> None:
    packet = build_research_canary_authorization_denial_hold_routing(
        p116_packet={
            **_VALID_P116_PACKET,
            "analyzed_candidates": [_ANALYZED_CANDIDATES[0]],
            "candidate_statuses": [{"candidate_id": _ANALYZED_CANDIDATES[0], "decision": "approve_for_controlled_envelope_planning"}],
        },
        routing_observations_packet=_observations(),
    )
    assert packet["analyzed_candidates"] == [_ANALYZED_CANDIDATES[0]]


def test_all_authority_locks_remain_false_including_runtime_envelope_authority() -> None:
    packet = build_research_canary_authorization_denial_hold_routing(
        p116_packet=_VALID_P116_PACKET,
        routing_observations_packet=_observations(),
    )
    assert packet["authority_locks"].get("canary_runtime_envelope_authority") is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_packet_hash_deterministic_and_excludes_itself() -> None:
    packet = build_research_canary_authorization_denial_hold_routing(
        p116_packet=_VALID_P116_PACKET,
        routing_observations_packet=_observations(),
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
    packet = build_research_canary_authorization_denial_hold_routing(
        p116_packet=_VALID_P116_PACKET,
        routing_observations_packet=_observations(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        write_research_canary_authorization_denial_hold_routing(out_path, packet)
        content = out_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert json.loads(content) == packet


def test_runner_flags_and_loader() -> None:
    args = _parse_args([])
    assert args.p116_path == str(P116_DEFAULT_PATH)
    assert args.routing_observations_path is None
    args = _parse_args(["--p116-path", "/tmp/p116.json"])
    assert args.p116_path == "/tmp/p116.json"
    args = _parse_args(["--routing-observations-path", "/tmp/o.json"])
    assert args.routing_observations_path == "/tmp/o.json"
    assert _load_json_packet("/nonexistent/path/latest.json") is None
    assert _load_json_packet(None) is None


def test_runner_run_writes_output_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        packet = run_research_canary_authorization_denial_hold_routing.run(
            p116_packet=_VALID_P116_PACKET,
            routing_observations_packet=_observations(),
            out_path=out_path,
        )
        assert out_path.exists()
        assert json.loads(out_path.read_text(encoding="utf-8")) == packet


def test_out_validation_latest_json_untouched() -> None:
    path = Path("out/validation/latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_authorization_denial_hold_routing(p116_packet=None)
    assert path.read_text(encoding="utf-8") == content_before


def test_out_projections_aal_viz_latest_json_untouched() -> None:
    path = Path("out/projections/aal_viz.latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_authorization_denial_hold_routing(p116_packet=None)
    assert path.read_text(encoding="utf-8") == content_before
