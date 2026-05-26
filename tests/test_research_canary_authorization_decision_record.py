from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# These tests verify P116 remains advisory-only and projection-only.
# They do NOT authorize canary mode, activate canary mode, grant canary authority,
# execute any canary plan, grant runtime envelope authority, or implement P117.

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from jsonschema import validate

from core.research_canary_authorization_decision_record import (
    build_research_canary_authorization_decision_record,
    write_research_canary_authorization_decision_record,
)
from scripts import run_research_canary_authorization_decision_record
from scripts.run_research_canary_authorization_decision_record import (
    P115_DEFAULT_PATH,
    _load_json_packet,
    _parse_args,
)

_AUTHORITY_LOCKS_P115 = {
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

_PACKAGE_REVIEW_COMPLETE_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P115_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchCanaryAuthorizationPackageReviewRecord.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P115_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD",
    "status": "CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD_EMITTED",
    "upstream_lane_id": "P114_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_DRAFT",
    "upstream_status": "CANARY_AUTHORIZATION_PACKAGE_DRAFT_EMITTED",
    "upstream_canary_authorization_package_draft_status": "CANARY_AUTHORIZATION_PACKAGE_DRAFT_COMPLETE",
    "lane_status": "CANARY_AUTHORIZATION_PACKAGE_REVIEW_COMPLETE",
    "canary_authorization_package_review_record_status": "CANARY_AUTHORIZATION_PACKAGE_REVIEW_COMPLETE",
    "stabilized_candidates": list(_PACKAGE_REVIEW_COMPLETE_CANDIDATES),
    "held_candidates": ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"],
    "repair_candidates": ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"],
    "rejected_candidates": ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"],
    "analyzed_candidates": list(_PACKAGE_REVIEW_COMPLETE_CANDIDATES),
    "package_review_complete_candidates": list(_PACKAGE_REVIEW_COMPLETE_CANDIDATES),
    "package_review_incomplete_candidates": [],
    "candidate_statuses": [],
    "candidate_package_review_statuses": [],
    "missing_requirements": {},
    "missing_package_review_requirements": {},
    "required_package_review_observations": [],
    "authority_locks": dict(_AUTHORITY_LOCKS_P115),
    "recommended_next_lane": "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD",
    "recommended_next_lane_reason": "Proceed to P116.",
    "not_computable_reasons": [],
    "provenance": {"source": "p114"},
    "packet_hash": "a" * 64,
}


def _observations(decision: str = "approve_for_controlled_envelope_planning") -> dict[str, Any]:
    return {
        "candidate_authorization_decision_observations": {
            candidate_id: {
                "candidate_id": candidate_id,
                "decision": decision,
                "operator_decision_observed": True,
                "decision_rationale_attached": True,
                "package_review_complete_observed": True,
                "provenance_bundle_attached": True,
                "authority_drift_observed": False,
                "notes": "authorization decision captured",
            }
            for candidate_id in _PACKAGE_REVIEW_COMPLETE_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_canary_authorization_decision_record.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


def test_deterministic_output_across_repeated_runs() -> None:
    first = build_research_canary_authorization_decision_record(
        p115_packet=_VALID_P115_PACKET,
        authorization_decision_observations_packet=_observations(),
    )
    second = build_research_canary_authorization_decision_record(
        p115_packet=_VALID_P115_PACKET,
        authorization_decision_observations_packet=_observations(),
    )
    assert first == second


def test_schema_validates_representative_packets() -> None:
    validate(
        build_research_canary_authorization_decision_record(
            p115_packet=_VALID_P115_PACKET,
            authorization_decision_observations_packet=_observations(),
        ),
        _schema(),
    )
    validate(
        build_research_canary_authorization_decision_record(p115_packet=_VALID_P115_PACKET),
        _schema(),
    )
    validate(
        build_research_canary_authorization_decision_record(p115_packet=None),
        _schema(),
    )


def test_missing_malformed_non_emitted_wrong_chain_or_no_candidates_returns_not_computable() -> (
    None
):
    assert build_research_canary_authorization_decision_record(p115_packet=None)[
        "status"
    ] == "NOT_COMPUTABLE"
    assert build_research_canary_authorization_decision_record(
        p115_packet="bad"  # type: ignore[arg-type]
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_authorization_decision_record(
        p115_packet={**_VALID_P115_PACKET, "status": "NOT_COMPUTABLE"}
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_authorization_decision_record(
        p115_packet={
            **_VALID_P115_PACKET,
            "recommended_next_lane": "P115_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD_CONTINUE",
        }
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_authorization_decision_record(
        p115_packet={**_VALID_P115_PACKET, "package_review_complete_candidates": []}
    )["status"] == "NOT_COMPUTABLE"


def test_upstream_without_expected_recommendation_never_recommends_p117() -> None:
    packet = build_research_canary_authorization_decision_record(
        p115_packet={
            **_VALID_P115_PACKET,
            "recommended_next_lane": "P115_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD_CONTINUE",
        },
        authorization_decision_observations_packet=_observations(),
    )
    assert packet["recommended_next_lane"] != "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING"


def test_authority_drift_or_forbidden_decision_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_authorization_decision_record(
        p115_packet={**_VALID_P115_PACKET, "status": "REJECTED_AUTHORITY_DRIFT"}
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"

    forbidden = _observations(decision="activate_canary")
    packet = build_research_canary_authorization_decision_record(
        p115_packet=_VALID_P115_PACKET,
        authorization_decision_observations_packet=forbidden,
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_default_missing_observations_continue_current_lane() -> None:
    packet = build_research_canary_authorization_decision_record(
        p115_packet=_VALID_P115_PACKET
    )
    assert packet["status"] == "CANARY_AUTHORIZATION_DECISION_RECORD_EMITTED"
    assert packet["recommended_next_lane"] == (
        "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD_CONTINUE"
    )


def test_complete_valid_decisions_recommend_next_lane_only_when_all_candidates_pass() -> None:
    packet = build_research_canary_authorization_decision_record(
        p115_packet=_VALID_P115_PACKET,
        authorization_decision_observations_packet=_observations(),
    )
    assert packet["lane_status"] == "CANARY_AUTHORIZATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING"
    assert packet["recommended_next_lane"] == (
        "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING"
    )


@pytest.mark.parametrize(
    "missing_field",
    [
        "operator_decision_observed",
        "decision_rationale_attached",
        "package_review_complete_observed",
        "provenance_bundle_attached",
    ],
)
def test_missing_required_fields_block_advancement(missing_field: str) -> None:
    observations = _observations()
    for candidate_id in _PACKAGE_REVIEW_COMPLETE_CANDIDATES:
        observations["candidate_authorization_decision_observations"][candidate_id][
            missing_field
        ] = False
    packet = build_research_canary_authorization_decision_record(
        p115_packet=_VALID_P115_PACKET,
        authorization_decision_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] != (
        "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING"
    )


def test_held_repair_rejected_upstream_partitions_preserved() -> None:
    packet = build_research_canary_authorization_decision_record(
        p115_packet=_VALID_P115_PACKET,
        authorization_decision_observations_packet=_observations(),
    )
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]
    assert packet["repair_candidates"] == ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"]
    assert packet["rejected_candidates"] == ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"]


def test_only_package_review_complete_candidates_are_analyzed() -> None:
    packet = build_research_canary_authorization_decision_record(
        p115_packet={
            **_VALID_P115_PACKET,
            "package_review_complete_candidates": [_PACKAGE_REVIEW_COMPLETE_CANDIDATES[0]],
            "stabilized_candidates": list(_PACKAGE_REVIEW_COMPLETE_CANDIDATES),
        },
        authorization_decision_observations_packet=_observations(),
    )
    assert packet["analyzed_candidates"] == [_PACKAGE_REVIEW_COMPLETE_CANDIDATES[0]]


def test_all_authority_locks_remain_false_including_runtime_envelope_authority() -> None:
    packet = build_research_canary_authorization_decision_record(
        p115_packet=_VALID_P115_PACKET,
        authorization_decision_observations_packet=_observations(),
    )
    assert packet["authority_locks"].get("canary_runtime_envelope_authority") is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_packet_hash_deterministic_and_excludes_itself() -> None:
    packet = build_research_canary_authorization_decision_record(
        p115_packet=_VALID_P115_PACKET,
        authorization_decision_observations_packet=_observations(),
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
    packet = build_research_canary_authorization_decision_record(
        p115_packet=_VALID_P115_PACKET,
        authorization_decision_observations_packet=_observations(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        write_research_canary_authorization_decision_record(out_path, packet)
        content = out_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert json.loads(content) == packet


def test_runner_flags_and_loader() -> None:
    args = _parse_args([])
    assert args.p115_path == str(P115_DEFAULT_PATH)
    assert args.authorization_decision_observations_path is None
    args = _parse_args(["--p115-path", "/tmp/p115.json"])
    assert args.p115_path == "/tmp/p115.json"
    args = _parse_args(["--authorization-decision-observations-path", "/tmp/o.json"])
    assert args.authorization_decision_observations_path == "/tmp/o.json"
    assert _load_json_packet("/nonexistent/path/latest.json") is None
    assert _load_json_packet(None) is None


def test_runner_run_writes_output_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        packet = run_research_canary_authorization_decision_record.run(
            p115_packet=_VALID_P115_PACKET,
            authorization_decision_observations_packet=_observations(),
            out_path=out_path,
        )
        assert out_path.exists()
        assert json.loads(out_path.read_text(encoding="utf-8")) == packet


def test_out_validation_latest_json_untouched() -> None:
    path = Path("out/validation/latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_authorization_decision_record(p115_packet=None)
    assert path.read_text(encoding="utf-8") == content_before


def test_out_projections_aal_viz_latest_json_untouched() -> None:
    path = Path("out/projections/aal_viz.latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_authorization_decision_record(p115_packet=None)
    assert path.read_text(encoding="utf-8") == content_before
