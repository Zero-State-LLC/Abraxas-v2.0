from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# These tests verify P129 remains advisory-only and projection-only.
# They do NOT implement P130 or grant final activation authority.

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from jsonschema import validate

from core.research_canary_activation_readiness_evidence_record import (
    build_research_canary_activation_readiness_evidence_record,
    write_research_canary_activation_readiness_evidence_record,
)
from scripts.research import run_research_canary_activation_readiness_evidence_record
from scripts.research.run_research_canary_activation_readiness_evidence_record import (
    P128_DEFAULT_PATH,
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
    "final_activation_authority": False,
}

_ANALYZED_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P128_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchCanaryActivationEnvelopeReviewRecord.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P128_RESEARCH_CANARY_ACTIVATION_ENVELOPE_REVIEW_RECORD",
    "status": "CANARY_ACTIVATION_ENVELOPE_REVIEW_RECORD_EMITTED",
    "upstream_lane_id": "P127_RESEARCH_CANARY_ACTIVATION_ENVELOPE_DRAFT",
    "upstream_status": "CANARY_ACTIVATION_ENVELOPE_DRAFT_EMITTED",
    "upstream_lane_status": "CANARY_ACTIVATION_ENVELOPE_DRAFT_COMPLETE",
    "lane_status": "CANARY_ACTIVATION_ENVELOPE_REVIEW_COMPLETE",
    "stabilized_candidates": list(_ANALYZED_CANDIDATES),
    "held_candidates": ["HOLD_KEEP"],
    "repair_candidates": ["REPAIR_KEEP"],
    "rejected_candidates": ["REJECT_KEEP"],
    "analyzed_candidates": list(_ANALYZED_CANDIDATES),
    "activation_envelope_review_complete_candidates": list(_ANALYZED_CANDIDATES),
    "candidate_statuses": [
        {
            "candidate_id": candidate_id,
            "canary_activation_envelope_review_status": "CANARY_ACTIVATION_ENVELOPE_REVIEW_COMPLETE",
        }
        for candidate_id in _ANALYZED_CANDIDATES
    ],
    "missing_requirements": {},
    "authority_locks": dict(_AUTHORITY_LOCKS),
    "recommended_next_lane": "P129_RESEARCH_CANARY_ACTIVATION_READINESS_EVIDENCE_RECORD",
    "recommended_next_lane_reason": "Proceed to P129.",
    "not_computable_reasons": [],
    "provenance": {"source": "p127"},
    "packet_hash": "a" * 64,
}


def _evidence() -> dict[str, Any]:
    return {
        "candidate_activation_readiness_evidence": {
            candidate_id: {
                "candidate_id": candidate_id,
                "activation_envelope_review_complete_observed": True,
                "readiness_scope_evidence_attached": True,
                "disabled_authority_evidence_attached": True,
                "observation_readiness_evidence_attached": True,
                "rollback_readiness_evidence_attached": True,
                "termination_readiness_evidence_attached": True,
                "operator_supervision_evidence_attached": True,
                "final_review_required": True,
                "activation_disabled_confirmed": True,
                "execution_disabled_confirmed": True,
                "runtime_control_disabled_confirmed": True,
                "provenance_bundle_attached": True,
                "authority_drift_observed": False,
                "notes": "activation readiness evidence captured",
            }
            for candidate_id in _ANALYZED_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_canary_activation_readiness_evidence_record.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


def test_deterministic_output_across_repeated_runs() -> None:
    first = build_research_canary_activation_readiness_evidence_record(
        p128_packet=_VALID_P128_PACKET,
        activation_readiness_evidence_packet=_evidence(),
    )
    second = build_research_canary_activation_readiness_evidence_record(
        p128_packet=_VALID_P128_PACKET,
        activation_readiness_evidence_packet=_evidence(),
    )
    assert first == second


def test_schema_validates_representative_complete_continue_failure_packets() -> None:
    validate(
        build_research_canary_activation_readiness_evidence_record(
            p128_packet=_VALID_P128_PACKET,
            activation_readiness_evidence_packet=_evidence(),
        ),
        _schema(),
    )
    validate(
        build_research_canary_activation_readiness_evidence_record(
            p128_packet=_VALID_P128_PACKET
        ),
        _schema(),
    )
    validate(
        build_research_canary_activation_readiness_evidence_record(p128_packet=None),
        _schema(),
    )


def test_missing_malformed_non_emitted_non_pass_wrong_chain_no_candidates_returns_not_computable() -> (
    None
):
    assert build_research_canary_activation_readiness_evidence_record(p128_packet=None)[
        "status"
    ] == "NOT_COMPUTABLE"
    assert build_research_canary_activation_readiness_evidence_record(
        p128_packet="bad"  # type: ignore[arg-type]
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_activation_readiness_evidence_record(
        p128_packet={**_VALID_P128_PACKET, "status": "NOT_COMPUTABLE"}
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_activation_readiness_evidence_record(
        p128_packet={
            **_VALID_P128_PACKET,
            "lane_status": "CANARY_ACTIVATION_ENVELOPE_REVIEW_INCOMPLETE",
        }
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_activation_readiness_evidence_record(
        p128_packet={**_VALID_P128_PACKET, "recommended_next_lane": "P128_CONTINUE"}
    )["status"] == "NOT_COMPUTABLE"
    assert build_research_canary_activation_readiness_evidence_record(
        p128_packet={**_VALID_P128_PACKET, "activation_envelope_review_complete_candidates": []}
    )["status"] == "NOT_COMPUTABLE"


def test_upstream_without_expected_recommendation_never_recommends_p130() -> None:
    packet = build_research_canary_activation_readiness_evidence_record(
        p128_packet={**_VALID_P128_PACKET, "recommended_next_lane": "P128_CONTINUE"},
        activation_readiness_evidence_packet=_evidence(),
    )
    assert packet["recommended_next_lane"] != (
        "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW"
    )


def test_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_canary_activation_readiness_evidence_record(
        p128_packet={**_VALID_P128_PACKET, "status": "REJECTED_AUTHORITY_DRIFT"}
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_default_missing_observations_continue_current_lane() -> None:
    packet = build_research_canary_activation_readiness_evidence_record(
        p128_packet=_VALID_P128_PACKET
    )
    assert packet["recommended_next_lane"] == (
        "P129_RESEARCH_CANARY_ACTIVATION_READINESS_EVIDENCE_RECORD_CONTINUE"
    )


def test_complete_evidence_recommend_p130_only_when_all_candidates_complete() -> None:
    packet = build_research_canary_activation_readiness_evidence_record(
        p128_packet=_VALID_P128_PACKET,
        activation_readiness_evidence_packet=_evidence(),
    )
    assert packet["recommended_next_lane"] == (
        "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW"
    )


@pytest.mark.parametrize(
    "missing_field",
    [
        "activation_envelope_review_complete_observed",
        "readiness_scope_evidence_attached",
        "disabled_authority_evidence_attached",
        "observation_readiness_evidence_attached",
        "rollback_readiness_evidence_attached",
        "termination_readiness_evidence_attached",
        "operator_supervision_evidence_attached",
        "final_review_required",
        "activation_disabled_confirmed",
        "execution_disabled_confirmed",
        "runtime_control_disabled_confirmed",
        "provenance_bundle_attached",
    ],
)
def test_missing_required_fields_block_advancement(missing_field: str) -> None:
    evidence = _evidence()
    for candidate_id in _ANALYZED_CANDIDATES:
        evidence["candidate_activation_readiness_evidence"][candidate_id][missing_field] = (
            False
        )
    packet = build_research_canary_activation_readiness_evidence_record(
        p128_packet=_VALID_P128_PACKET,
        activation_readiness_evidence_packet=evidence,
    )
    assert packet["recommended_next_lane"] != (
        "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW"
    )


def test_held_repair_rejected_upstream_partitions_preserved_separately() -> None:
    packet = build_research_canary_activation_readiness_evidence_record(
        p128_packet=_VALID_P128_PACKET,
        activation_readiness_evidence_packet=_evidence(),
    )
    assert packet["held_candidates"] == ["HOLD_KEEP"]
    assert packet["repair_candidates"] == ["REPAIR_KEEP"]
    assert packet["rejected_candidates"] == ["REJECT_KEEP"]


def test_only_p128_activation_envelope_review_complete_candidates_are_analyzed() -> None:
    packet = build_research_canary_activation_readiness_evidence_record(
        p128_packet={
            **_VALID_P128_PACKET,
            "activation_envelope_review_complete_candidates": [_ANALYZED_CANDIDATES[0]],
        },
        activation_readiness_evidence_packet=_evidence(),
    )
    assert packet["analyzed_candidates"] == [_ANALYZED_CANDIDATES[0]]


def test_all_authority_locks_remain_false_including_activation_envelope_execution_final() -> (
    None
):
    packet = build_research_canary_activation_readiness_evidence_record(
        p128_packet=_VALID_P128_PACKET,
        activation_readiness_evidence_packet=_evidence(),
    )
    assert packet["authority_locks"].get("activation_envelope_authority") is False
    assert packet["authority_locks"].get("activation_execution_authority") is False
    assert packet["authority_locks"].get("final_activation_authority") is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_packet_hash_deterministic_and_excludes_itself() -> None:
    packet = build_research_canary_activation_readiness_evidence_record(
        p128_packet=_VALID_P128_PACKET,
        activation_readiness_evidence_packet=_evidence(),
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
    packet = build_research_canary_activation_readiness_evidence_record(
        p128_packet=_VALID_P128_PACKET,
        activation_readiness_evidence_packet=_evidence(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        write_research_canary_activation_readiness_evidence_record(out_path, packet)
        content = out_path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert json.loads(content) == packet


def test_runner_flags_and_loader() -> None:
    args = _parse_args([])
    assert args.p128_path == str(P128_DEFAULT_PATH)
    assert args.activation_readiness_evidence_path is None
    args = _parse_args(["--p128-path", "/tmp/p128.json"])
    assert args.p128_path == "/tmp/p128.json"
    args = _parse_args(["--activation-readiness-evidence-path", "/tmp/o.json"])
    assert args.activation_readiness_evidence_path == "/tmp/o.json"
    assert _load_json_packet("/nonexistent/path/latest.json") is None
    assert _load_json_packet(None) is None


def test_runner_run_writes_output_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "latest.json"
        packet = run_research_canary_activation_readiness_evidence_record.run(
            p128_packet=_VALID_P128_PACKET,
            activation_readiness_evidence_packet=_evidence(),
            out_path=out_path,
        )
        assert out_path.exists()
        assert json.loads(out_path.read_text(encoding="utf-8")) == packet


def test_out_validation_latest_json_untouched() -> None:
    path = Path("out/validation/latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_activation_readiness_evidence_record(p128_packet=None)
    assert path.read_text(encoding="utf-8") == content_before


def test_out_projections_aal_viz_latest_json_untouched() -> None:
    path = Path("out/projections/aal_viz.latest.json")
    content_before = path.read_text(encoding="utf-8")
    build_research_canary_activation_readiness_evidence_record(p128_packet=None)
    assert path.read_text(encoding="utf-8") == content_before
