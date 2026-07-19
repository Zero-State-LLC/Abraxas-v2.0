from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# These tests verify P120 remains advisory-only/projection-only governance drafting.
# They do NOT execute rollback/termination, grant authority, or implement P121.

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import validate

from core.research_canary_rollback_termination_governance import (
    build_research_canary_rollback_termination_governance,
    write_research_canary_rollback_termination_governance,
)
from scripts.research import run_research_canary_rollback_termination_governance
from scripts.research.run_research_canary_rollback_termination_governance import (
    P119_DEFAULT_PATH,
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

_VALID_P119_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchCanaryRuntimeObservationRecord.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P119_RESEARCH_CANARY_RUNTIME_OBSERVATION_RECORD",
    "status": "CANARY_RUNTIME_OBSERVATION_RECORD_EMITTED",
    "upstream_lane_id": "P118_RESEARCH_CONTROLLED_CANARY_ENVELOPE_DRAFT",
    "upstream_status": "CONTROLLED_CANARY_ENVELOPE_DRAFT_EMITTED",
    "lane_status": "CANARY_RUNTIME_OBSERVATION_COMPLETE",
    "stabilized_candidates": list(_ANALYZED_CANDIDATES),
    "held_candidates": ["HOLD_KEEP"],
    "repair_candidates": ["REPAIR_KEEP"],
    "rejected_candidates": ["REJECT_KEEP"],
    "analyzed_candidates": list(_ANALYZED_CANDIDATES),
    "runtime_observation_complete_candidates": list(_ANALYZED_CANDIDATES),
    "candidate_statuses": [
        {
            "candidate_id": candidate_id,
            "canary_runtime_observation_status": "CANARY_RUNTIME_OBSERVATION_COMPLETE",
        }
        for candidate_id in _ANALYZED_CANDIDATES
    ],
    "authority_locks": dict(_AUTHORITY_LOCKS),
    "recommended_next_lane": "P120_RESEARCH_CANARY_ROLLBACK_TERMINATION_GOVERNANCE",
    "recommended_next_lane_reason": "Proceed to P120.",
    "not_computable_reasons": [],
    "provenance": {"source": "p118"},
    "packet_hash": "a" * 64,
}


def _observations() -> dict[str, Any]:
    return {
        "candidate_rollback_termination_observations": {
            candidate_id: {
                "candidate_id": candidate_id,
                "runtime_observation_complete_observed": True,
                "rollback_condition_defined": True,
                "rollback_procedure_documented": True,
                "termination_condition_defined": True,
                "termination_procedure_documented": True,
                "rollback_authority_withheld_confirmed": True,
                "termination_authority_withheld_confirmed": True,
                "operator_go_no_go_required": True,
                "provenance_bundle_attached": True,
                "authority_drift_observed": False,
                "notes": "governance observation captured",
            }
            for candidate_id in _ANALYZED_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_canary_rollback_termination_governance.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


def test_deterministic_output_across_repeated_runs() -> None:
    first = build_research_canary_rollback_termination_governance(
        p119_packet=_VALID_P119_PACKET,
        rollback_termination_observations_packet=_observations(),
    )
    second = build_research_canary_rollback_termination_governance(
        p119_packet=_VALID_P119_PACKET,
        rollback_termination_observations_packet=_observations(),
    )
    assert first == second


def test_schema_validates_representative_complete_continue_failure_packets() -> None:
    validate(
        build_research_canary_rollback_termination_governance(
            p119_packet=_VALID_P119_PACKET,
            rollback_termination_observations_packet=_observations(),
        ),
        _schema(),
    )
    validate(
        build_research_canary_rollback_termination_governance(p119_packet=_VALID_P119_PACKET),
        _schema(),
    )
    validate(
        build_research_canary_rollback_termination_governance(p119_packet=None), _schema()
    )


def test_missing_malformed_non_emitted_non_pass_wrong_chain_or_no_candidates_returns_not_computable() -> (
    None
):
    assert build_research_canary_rollback_termination_governance(p119_packet=None)[
        "status"
    ] == "NOT_COMPUTABLE"
    assert build_research_canary_rollback_termination_governance(
        p119_packet="bad"  # type: ignore[arg-type]
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_rollback_termination_governance(
        p119_packet={**_VALID_P119_PACKET, "status": "NOT_COMPUTABLE"}
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_rollback_termination_governance(
        p119_packet={
            **_VALID_P119_PACKET,
            "lane_status": "CANARY_RUNTIME_OBSERVATION_INCOMPLETE",
        }
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_rollback_termination_governance(
        p119_packet={
            **_VALID_P119_PACKET,
            "recommended_next_lane": "P119_RESEARCH_CANARY_RUNTIME_OBSERVATION_RECORD_CONTINUE",
        }
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_rollback_termination_governance(
        p119_packet={
            **_VALID_P119_PACKET,
            "runtime_observation_complete_candidates": [],
        }
    )["status"] == "NOT_COMPUTABLE"


def test_upstream_without_expected_recommendation_never_recommends_p121() -> None:
    packet = build_research_canary_rollback_termination_governance(
        p119_packet={
            **_VALID_P119_PACKET,
            "recommended_next_lane": "P119_RESEARCH_CANARY_RUNTIME_OBSERVATION_RECORD_CONTINUE",
        },
        rollback_termination_observations_packet=_observations(),
    )
    assert packet["recommended_next_lane"] != "P121_RESEARCH_CANARY_OPERATOR_GO_NO_GO_REVIEW"


def test_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_rollback_termination_governance(
        p119_packet={**_VALID_P119_PACKET, "status": "REJECTED_AUTHORITY_DRIFT"}
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_default_missing_observations_continue_current_lane() -> None:
    packet = build_research_canary_rollback_termination_governance(
        p119_packet=_VALID_P119_PACKET
    )
    assert packet["recommended_next_lane"] == (
        "P120_RESEARCH_CANARY_ROLLBACK_TERMINATION_GOVERNANCE_CONTINUE"
    )


def test_complete_observations_recommend_p121_only_when_all_candidates_complete() -> None:
    packet = build_research_canary_rollback_termination_governance(
        p119_packet=_VALID_P119_PACKET,
        rollback_termination_observations_packet=_observations(),
    )
    assert packet["recommended_next_lane"] == "P121_RESEARCH_CANARY_OPERATOR_GO_NO_GO_REVIEW"


def test_missing_required_fields_block_advancement() -> None:
    observations = _observations()
    for candidate_id in _ANALYZED_CANDIDATES:
        observations["candidate_rollback_termination_observations"][candidate_id][
            "rollback_authority_withheld_confirmed"
        ] = False
    packet = build_research_canary_rollback_termination_governance(
        p119_packet=_VALID_P119_PACKET,
        rollback_termination_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] != "P121_RESEARCH_CANARY_OPERATOR_GO_NO_GO_REVIEW"


def test_held_repair_rejected_upstream_partitions_preserved_separately() -> None:
    packet = build_research_canary_rollback_termination_governance(
        p119_packet=_VALID_P119_PACKET,
        rollback_termination_observations_packet=_observations(),
    )
    assert packet["held_candidates"] == ["HOLD_KEEP"]
    assert packet["repair_candidates"] == ["REPAIR_KEEP"]
    assert packet["rejected_candidates"] == ["REJECT_KEEP"]


def test_only_runtime_observation_complete_bucket_candidates_are_analyzed() -> None:
    packet = build_research_canary_rollback_termination_governance(
        p119_packet={
            **_VALID_P119_PACKET,
            "runtime_observation_complete_candidates": [_ANALYZED_CANDIDATES[0]],
            "analyzed_candidates": [
                _ANALYZED_CANDIDATES[0],
                _ANALYZED_CANDIDATES[1],
                "EXTRA_SHOULD_NOT_BE_ANALYZED",
            ],
        },
        rollback_termination_observations_packet=_observations(),
    )
    assert packet["analyzed_candidates"] == [_ANALYZED_CANDIDATES[0]]


def test_all_authority_locks_remain_false_including_required_runtime_rollback_termination_locks() -> (
    None
):
    packet = build_research_canary_rollback_termination_governance(
        p119_packet=_VALID_P119_PACKET,
        rollback_termination_observations_packet=_observations(),
    )
    assert packet["authority_locks"].get("canary_runtime_execution") is False
    assert packet["authority_locks"].get("canary_runtime_control") is False
    assert packet["authority_locks"].get("rollback_execution_authority") is False
    assert packet["authority_locks"].get("termination_execution_authority") is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_packet_hash_deterministic_and_excludes_itself() -> None:
    packet = build_research_canary_rollback_termination_governance(
        p119_packet=_VALID_P119_PACKET,
        rollback_termination_observations_packet=_observations(),
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
    packet = build_research_canary_rollback_termination_governance(
        p119_packet=_VALID_P119_PACKET,
        rollback_termination_observations_packet=_observations(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        write_research_canary_rollback_termination_governance(out_path, packet)
        content = out_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert json.loads(content) == packet


def test_runner_flags_and_loader() -> None:
    args = _parse_args([])
    assert args.p119_path == str(P119_DEFAULT_PATH)
    assert args.rollback_termination_observations_path is None
    args = _parse_args(["--p119-path", "/tmp/p119.json"])
    assert args.p119_path == "/tmp/p119.json"
    args = _parse_args(["--rollback-termination-observations-path", "/tmp/o.json"])
    assert args.rollback_termination_observations_path == "/tmp/o.json"
    assert _load_json_packet("/nonexistent/path/latest.json") is None
    assert _load_json_packet(None) is None


def test_runner_run_writes_output_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        packet = run_research_canary_rollback_termination_governance.run(
            p119_packet=_VALID_P119_PACKET,
            rollback_termination_observations_packet=_observations(),
            out_path=out_path,
        )
        assert out_path.exists()
        assert json.loads(out_path.read_text(encoding="utf-8")) == packet


def test_out_validation_latest_json_untouched() -> None:
    path = Path("out/validation/latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_rollback_termination_governance(p119_packet=None)
    assert path.read_text(encoding="utf-8") == content_before


def test_out_projections_aal_viz_latest_json_untouched() -> None:
    path = Path("out/projections/aal_viz.latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_rollback_termination_governance(p119_packet=None)
    assert path.read_text(encoding="utf-8") == content_before
