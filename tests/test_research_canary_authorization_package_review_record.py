from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# These tests verify P115 remains advisory-only and projection-only.
# They do NOT authorize canary mode, activate canary mode, grant canary authority,
# execute any canary plan, grant runtime envelope authority, or implement P116.

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from jsonschema import validate

from core.research_canary_authorization_package_review_record import (
    build_research_canary_authorization_package_review_record,
    write_research_canary_authorization_package_review_record,
)
from scripts.research import run_research_canary_authorization_package_review_record
from scripts.research.run_research_canary_authorization_package_review_record import (
    P114_DEFAULT_PATH,
    _load_json_packet,
    _parse_args,
)

_AUTHORITY_LOCKS_P114 = {
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
}

_PACKAGE_DRAFT_COMPLETE_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P114_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchCanaryAuthorizationPackageDraft.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P114_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_DRAFT",
    "status": "CANARY_AUTHORIZATION_PACKAGE_DRAFT_EMITTED",
    "upstream_lane_id": "P113_RESEARCH_CANARY_FINAL_PRECHECK_RECORD",
    "upstream_canary_final_precheck_record_status": "CANARY_FINAL_PRECHECK_RECORD_EMITTED",
    "canary_authorization_package_draft_status": "CANARY_AUTHORIZATION_PACKAGE_DRAFT_COMPLETE",
    "stabilized_candidates": list(_PACKAGE_DRAFT_COMPLETE_CANDIDATES),
    "held_candidates": ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"],
    "repair_candidates": ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"],
    "rejected_candidates": ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"],
    "analyzed_candidates": list(_PACKAGE_DRAFT_COMPLETE_CANDIDATES),
    "authorization_package_draft_complete_candidates": list(
        _PACKAGE_DRAFT_COMPLETE_CANDIDATES
    ),
    "authorization_package_draft_incomplete_candidates": [],
    "candidate_authorization_package_draft_statuses": [],
    "required_authorization_package_observations": [],
    "missing_authorization_package_requirements": {},
    "authority_locks": dict(_AUTHORITY_LOCKS_P114),
    "recommended_next_lane": "P115_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD",
    "recommended_next_lane_reason": "Proceed to P115.",
    "not_computable_reasons": [],
    "provenance": {"source": "p113"},
    "packet_hash": "a" * 64,
}


def _observations() -> dict[str, Any]:
    return {
        "candidate_package_review_observations": {
            candidate_id: {
                "candidate_id": candidate_id,
                "package_draft_complete_observed": True,
                "package_scope_review_complete": True,
                "package_conditions_review_complete": True,
                "rollback_binding_review_complete": True,
                "monitoring_binding_review_complete": True,
                "blast_radius_binding_review_complete": True,
                "exit_criteria_binding_review_complete": True,
                "provenance_review_complete": True,
                "safety_review_complete": True,
                "execution_disabled_review_complete": True,
                "operator_review_observed": True,
                "authority_drift_observed": False,
                "notes": "package review observations captured",
            }
            for candidate_id in _PACKAGE_DRAFT_COMPLETE_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_canary_authorization_package_review_record.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


def test_deterministic_output_across_repeated_runs() -> None:
    first = build_research_canary_authorization_package_review_record(
        p114_packet=_VALID_P114_PACKET,
        package_review_observations_packet=_observations(),
    )
    second = build_research_canary_authorization_package_review_record(
        p114_packet=_VALID_P114_PACKET,
        package_review_observations_packet=_observations(),
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_schema_validates_representative_complete_packet() -> None:
    packet = build_research_canary_authorization_package_review_record(
        p114_packet=_VALID_P114_PACKET,
        package_review_observations_packet=_observations(),
    )
    validate(packet, _schema())


def test_schema_validates_representative_continue_packet() -> None:
    packet = build_research_canary_authorization_package_review_record(
        p114_packet=_VALID_P114_PACKET
    )
    validate(packet, _schema())


def test_schema_validates_representative_failure_packet() -> None:
    packet = build_research_canary_authorization_package_review_record(p114_packet=None)
    validate(packet, _schema())


def test_missing_malformed_non_emitted_wrong_chain_or_no_candidates_returns_not_computable() -> (
    None
):
    assert build_research_canary_authorization_package_review_record(
        p114_packet=None
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_authorization_package_review_record(
        p114_packet="bad"  # type: ignore[arg-type]
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_authorization_package_review_record(
        p114_packet={**_VALID_P114_PACKET, "status": "NOT_COMPUTABLE"}
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_authorization_package_review_record(
        p114_packet={
            **_VALID_P114_PACKET,
            "recommended_next_lane": "P114_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_DRAFT_CONTINUE",
        }
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_authorization_package_review_record(
        p114_packet={**_VALID_P114_PACKET, "authorization_package_draft_complete_candidates": []}
    )["status"] == "NOT_COMPUTABLE"


def test_upstream_without_expected_recommendation_never_recommends_p116() -> None:
    packet = build_research_canary_authorization_package_review_record(
        p114_packet={
            **_VALID_P114_PACKET,
            "recommended_next_lane": "P114_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_DRAFT_CONTINUE",
        },
        package_review_observations_packet=_observations(),
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] != "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD"


def test_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_authorization_package_review_record(
        p114_packet={
            **_VALID_P114_PACKET,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "canary_authorization_package_draft_status": "CANARY_AUTHORIZATION_PACKAGE_DRAFT_REJECTED_AUTHORITY_DRIFT",
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_true_authority_lock_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_authorization_package_review_record(
        p114_packet={
            **_VALID_P114_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS_P114, "canary_authority": True},
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_default_missing_observations_continue_current_lane() -> None:
    packet = build_research_canary_authorization_package_review_record(
        p114_packet=_VALID_P114_PACKET
    )
    assert packet["status"] == "CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD_EMITTED"
    assert packet["lane_status"] == "CANARY_AUTHORIZATION_PACKAGE_REVIEW_INCOMPLETE"
    assert (
        packet["recommended_next_lane"]
        == "P115_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD_CONTINUE"
    )


def test_complete_observations_recommend_next_lane_only_when_all_candidates_pass() -> None:
    packet = build_research_canary_authorization_package_review_record(
        p114_packet=_VALID_P114_PACKET,
        package_review_observations_packet=_observations(),
    )
    assert packet["lane_status"] == "CANARY_AUTHORIZATION_PACKAGE_REVIEW_COMPLETE"
    assert (
        packet["recommended_next_lane"]
        == "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD"
    )


@pytest.mark.parametrize(
    "missing_field",
    [
        "package_draft_complete_observed",
        "package_scope_review_complete",
        "package_conditions_review_complete",
        "rollback_binding_review_complete",
        "monitoring_binding_review_complete",
        "blast_radius_binding_review_complete",
        "exit_criteria_binding_review_complete",
        "provenance_review_complete",
        "safety_review_complete",
        "execution_disabled_review_complete",
        "operator_review_observed",
    ],
)
def test_missing_required_fields_block_advancement(missing_field: str) -> None:
    observations = _observations()
    for candidate_id in _PACKAGE_DRAFT_COMPLETE_CANDIDATES:
        observations["candidate_package_review_observations"][candidate_id][missing_field] = False
    packet = build_research_canary_authorization_package_review_record(
        p114_packet=_VALID_P114_PACKET,
        package_review_observations_packet=observations,
    )
    assert (
        packet["recommended_next_lane"]
        != "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD"
    )


def test_held_repair_rejected_partitions_preserved() -> None:
    packet = build_research_canary_authorization_package_review_record(
        p114_packet=_VALID_P114_PACKET,
        package_review_observations_packet=_observations(),
    )
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]
    assert packet["repair_candidates"] == ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"]
    assert packet["rejected_candidates"] == ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"]


def test_only_upstream_complete_bucket_is_analyzed() -> None:
    packet = build_research_canary_authorization_package_review_record(
        p114_packet={
            **_VALID_P114_PACKET,
            "authorization_package_draft_complete_candidates": [
                _PACKAGE_DRAFT_COMPLETE_CANDIDATES[0]
            ],
            "stabilized_candidates": list(_PACKAGE_DRAFT_COMPLETE_CANDIDATES),
        },
        package_review_observations_packet=_observations(),
    )
    assert packet["analyzed_candidates"] == [_PACKAGE_DRAFT_COMPLETE_CANDIDATES[0]]


def test_all_authority_locks_remain_false_including_runtime_envelope_authority() -> None:
    packet = build_research_canary_authorization_package_review_record(
        p114_packet=_VALID_P114_PACKET,
        package_review_observations_packet=_observations(),
    )
    expected = {
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
        "canary_final_precheck_authority",
        "canary_package_authority",
        "canary_package_execution",
        "canary_runtime_envelope_authority",
    }
    assert set(packet["authority_locks"].keys()) == expected
    assert all(value is False for value in packet["authority_locks"].values())


def test_packet_hash_deterministic_and_excludes_itself() -> None:
    packet = build_research_canary_authorization_package_review_record(
        p114_packet=_VALID_P114_PACKET,
        package_review_observations_packet=_observations(),
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
    packet = build_research_canary_authorization_package_review_record(
        p114_packet=_VALID_P114_PACKET,
        package_review_observations_packet=_observations(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        write_research_canary_authorization_package_review_record(out_path, packet)
        content = out_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert json.loads(content) == packet


def test_runner_flags_and_loader() -> None:
    args = _parse_args([])
    assert args.p114_path == str(P114_DEFAULT_PATH)
    assert args.package_review_observations_path is None
    args = _parse_args(["--p114-path", "/tmp/p114.json"])
    assert args.p114_path == "/tmp/p114.json"
    args = _parse_args(["--package-review-observations-path", "/tmp/o.json"])
    assert args.package_review_observations_path == "/tmp/o.json"
    assert _load_json_packet("/nonexistent/path/latest.json") is None
    assert _load_json_packet(None) is None


def test_runner_run_writes_output_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        packet = run_research_canary_authorization_package_review_record.run(
            p114_packet=_VALID_P114_PACKET,
            package_review_observations_packet=_observations(),
            out_path=out_path,
        )
        assert out_path.exists()
        assert json.loads(out_path.read_text(encoding="utf-8")) == packet


def test_out_validation_latest_json_untouched() -> None:
    path = Path("out/validation/latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_authorization_package_review_record(p114_packet=None)
    assert path.read_text(encoding="utf-8") == content_before


def test_out_projections_aal_viz_latest_json_untouched() -> None:
    path = Path("out/projections/aal_viz.latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_authorization_package_review_record(p114_packet=None)
    assert path.read_text(encoding="utf-8") == content_before
