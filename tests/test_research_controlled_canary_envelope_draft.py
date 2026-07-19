from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# These tests verify P118 remains advisory-only/projection-only envelope drafting.
# They do NOT activate canary mode, grant authority, execute plans, or implement P119.

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import validate

from core.research_controlled_canary_envelope_draft import (
    build_research_controlled_canary_envelope_draft,
    write_research_controlled_canary_envelope_draft,
)
from scripts.research import run_research_controlled_canary_envelope_draft
from scripts.research.run_research_controlled_canary_envelope_draft import (
    P117_DEFAULT_PATH,
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
}

_ANALYZED_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P117_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchCanaryAuthorizationDenialHoldRouting.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING",
    "status": "CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING_EMITTED",
    "upstream_lane_id": "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD",
    "upstream_status": "CANARY_AUTHORIZATION_DECISION_RECORD_EMITTED",
    "lane_status": "CANARY_AUTHORIZATION_ROUTE_APPROVED_FOR_ENVELOPE_DRAFT",
    "stabilized_candidates": list(_ANALYZED_CANDIDATES),
    "held_candidates": ["HOLD_KEEP"],
    "repair_candidates": ["REPAIR_KEEP"],
    "rejected_candidates": ["REJECT_KEEP"],
    "analyzed_candidates": list(_ANALYZED_CANDIDATES),
    "approved_for_controlled_envelope_planning_candidates": list(_ANALYZED_CANDIDATES),
    "candidate_statuses": [
        {
            "candidate_id": candidate_id,
            "decision": "approve_for_controlled_envelope_planning",
        }
        for candidate_id in _ANALYZED_CANDIDATES
    ],
    "authority_locks": dict(_AUTHORITY_LOCKS),
    "recommended_next_lane": "P118_RESEARCH_CONTROLLED_CANARY_ENVELOPE_DRAFT",
    "recommended_next_lane_reason": "Proceed to P118.",
    "not_computable_reasons": [],
    "provenance": {"source": "p116"},
    "packet_hash": "a" * 64,
}


def _observations() -> dict[str, Any]:
    return {
        "candidate_envelope_observations": {
            candidate_id: {
                "candidate_id": candidate_id,
                "approval_route_observed": True,
                "envelope_scope_defined": True,
                "runtime_boundary_defined": True,
                "observation_surface_defined": True,
                "rollback_hook_defined": True,
                "termination_condition_defined": True,
                "blast_radius_limit_defined": True,
                "operator_supervision_required": True,
                "execution_disabled_confirmed": True,
                "provenance_bundle_attached": True,
                "authority_drift_observed": False,
                "notes": "envelope evidence captured",
            }
            for candidate_id in _ANALYZED_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_controlled_canary_envelope_draft.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


def test_deterministic_output_across_repeated_runs() -> None:
    first = build_research_controlled_canary_envelope_draft(
        p117_packet=_VALID_P117_PACKET,
        envelope_observations_packet=_observations(),
    )
    second = build_research_controlled_canary_envelope_draft(
        p117_packet=_VALID_P117_PACKET,
        envelope_observations_packet=_observations(),
    )
    assert first == second


def test_schema_validates_representative_complete_continue_failure_packets() -> None:
    validate(
        build_research_controlled_canary_envelope_draft(
            p117_packet=_VALID_P117_PACKET,
            envelope_observations_packet=_observations(),
        ),
        _schema(),
    )
    validate(
        build_research_controlled_canary_envelope_draft(p117_packet=_VALID_P117_PACKET),
        _schema(),
    )
    validate(build_research_controlled_canary_envelope_draft(p117_packet=None), _schema())


def test_missing_malformed_non_emitted_non_pass_wrong_chain_or_no_candidates_returns_not_computable() -> (
    None
):
    assert build_research_controlled_canary_envelope_draft(p117_packet=None)[
        "status"
    ] == "NOT_COMPUTABLE"
    assert build_research_controlled_canary_envelope_draft(
        p117_packet="bad"  # type: ignore[arg-type]
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_controlled_canary_envelope_draft(
        p117_packet={**_VALID_P117_PACKET, "status": "NOT_COMPUTABLE"}
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_controlled_canary_envelope_draft(
        p117_packet={
            **_VALID_P117_PACKET,
            "lane_status": "CANARY_AUTHORIZATION_ROUTE_HELD",
        }
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_controlled_canary_envelope_draft(
        p117_packet={
            **_VALID_P117_PACKET,
            "recommended_next_lane": "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING_CONTINUE",
        }
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_controlled_canary_envelope_draft(
        p117_packet={
            **_VALID_P117_PACKET,
            "approved_for_controlled_envelope_planning_candidates": [],
        }
    )["status"] == "NOT_COMPUTABLE"


def test_upstream_without_expected_recommendation_never_recommends_p119() -> None:
    packet = build_research_controlled_canary_envelope_draft(
        p117_packet={
            **_VALID_P117_PACKET,
            "recommended_next_lane": "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING_CONTINUE",
        },
        envelope_observations_packet=_observations(),
    )
    assert packet["recommended_next_lane"] != "P119_RESEARCH_CANARY_RUNTIME_OBSERVATION_RECORD"


def test_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_controlled_canary_envelope_draft(
        p117_packet={**_VALID_P117_PACKET, "status": "REJECTED_AUTHORITY_DRIFT"}
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_default_missing_observations_continue_current_lane() -> None:
    packet = build_research_controlled_canary_envelope_draft(p117_packet=_VALID_P117_PACKET)
    assert packet["recommended_next_lane"] == (
        "P118_RESEARCH_CONTROLLED_CANARY_ENVELOPE_DRAFT_CONTINUE"
    )


def test_complete_observations_recommend_p119_only_when_all_candidates_complete() -> None:
    packet = build_research_controlled_canary_envelope_draft(
        p117_packet=_VALID_P117_PACKET,
        envelope_observations_packet=_observations(),
    )
    assert packet["recommended_next_lane"] == "P119_RESEARCH_CANARY_RUNTIME_OBSERVATION_RECORD"


def test_missing_required_fields_block_advancement() -> None:
    observations = _observations()
    for candidate_id in _ANALYZED_CANDIDATES:
        observations["candidate_envelope_observations"][candidate_id][
            "execution_disabled_confirmed"
        ] = False
    packet = build_research_controlled_canary_envelope_draft(
        p117_packet=_VALID_P117_PACKET,
        envelope_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] != "P119_RESEARCH_CANARY_RUNTIME_OBSERVATION_RECORD"


def test_held_repair_rejected_upstream_partitions_preserved_separately() -> None:
    packet = build_research_controlled_canary_envelope_draft(
        p117_packet=_VALID_P117_PACKET,
        envelope_observations_packet=_observations(),
    )
    assert packet["held_candidates"] == ["HOLD_KEEP"]
    assert packet["repair_candidates"] == ["REPAIR_KEEP"]
    assert packet["rejected_candidates"] == ["REJECT_KEEP"]


def test_only_approved_bucket_candidates_are_analyzed() -> None:
    packet = build_research_controlled_canary_envelope_draft(
        p117_packet={
            **_VALID_P117_PACKET,
            "approved_for_controlled_envelope_planning_candidates": [_ANALYZED_CANDIDATES[0]],
            "analyzed_candidates": [
                _ANALYZED_CANDIDATES[0],
                _ANALYZED_CANDIDATES[1],
                "EXTRA_SHOULD_NOT_BE_ANALYZED",
            ],
        },
        envelope_observations_packet=_observations(),
    )
    assert packet["analyzed_candidates"] == [_ANALYZED_CANDIDATES[0]]


def test_all_authority_locks_remain_false_including_required_runtime_rollback_termination_locks() -> (
    None
):
    packet = build_research_controlled_canary_envelope_draft(
        p117_packet=_VALID_P117_PACKET,
        envelope_observations_packet=_observations(),
    )
    assert packet["authority_locks"].get("canary_runtime_execution") is False
    assert packet["authority_locks"].get("canary_runtime_control") is False
    assert packet["authority_locks"].get("rollback_execution_authority") is False
    assert packet["authority_locks"].get("termination_execution_authority") is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_packet_hash_deterministic_and_excludes_itself() -> None:
    packet = build_research_controlled_canary_envelope_draft(
        p117_packet=_VALID_P117_PACKET,
        envelope_observations_packet=_observations(),
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
    packet = build_research_controlled_canary_envelope_draft(
        p117_packet=_VALID_P117_PACKET,
        envelope_observations_packet=_observations(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        write_research_controlled_canary_envelope_draft(out_path, packet)
        content = out_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert json.loads(content) == packet


def test_runner_flags_and_loader() -> None:
    args = _parse_args([])
    assert args.p117_path == str(P117_DEFAULT_PATH)
    assert args.envelope_observations_path is None
    args = _parse_args(["--p117-path", "/tmp/p117.json"])
    assert args.p117_path == "/tmp/p117.json"
    args = _parse_args(["--envelope-observations-path", "/tmp/o.json"])
    assert args.envelope_observations_path == "/tmp/o.json"
    assert _load_json_packet("/nonexistent/path/latest.json") is None
    assert _load_json_packet(None) is None


def test_runner_run_writes_output_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        packet = run_research_controlled_canary_envelope_draft.run(
            p117_packet=_VALID_P117_PACKET,
            envelope_observations_packet=_observations(),
            out_path=out_path,
        )
        assert out_path.exists()
        assert json.loads(out_path.read_text(encoding="utf-8")) == packet


def test_out_validation_latest_json_untouched() -> None:
    path = Path("out/validation/latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_controlled_canary_envelope_draft(p117_packet=None)
    assert path.read_text(encoding="utf-8") == content_before


def test_out_projections_aal_viz_latest_json_untouched() -> None:
    path = Path("out/projections/aal_viz.latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_controlled_canary_envelope_draft(p117_packet=None)
    assert path.read_text(encoding="utf-8") == content_before
