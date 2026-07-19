from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from core.research_shadow_replay_audit import (
    REQUIRED_REPLAY_PROOF_FLAGS,
    build_research_shadow_replay_audit,
    write_research_shadow_replay_audit,
)
from scripts.research import run_research_shadow_replay_audit
from scripts.research.run_research_shadow_replay_audit import (
    P102_DEFAULT_PATH,
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
}

_WINDOW_COMPLETE_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P102_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchStabilizationWindowMonitor.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P102_RESEARCH_STABILIZATION_WINDOW_MONITOR",
    "status": "STABILIZATION_WINDOW_MONITOR_EMITTED",
    "upstream_lane_id": "P101_RESEARCH_SHADOW_STABILIZATION_RECEIPT",
    "upstream_stabilization_receipt_status": "SHADOW_STABILIZATION_RECEIPT_EMITTED",
    "stabilization_window_monitor_status": "EMITTED",
    "stabilized_candidates": list(_WINDOW_COMPLETE_CANDIDATES),
    "held_candidates": ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"],
    "repair_candidates": ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"],
    "rejected_candidates": ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"],
    "minimum_shadow_cycles_required": 12,
    "candidate_window_statuses": [],
    "window_complete_candidates": list(_WINDOW_COMPLETE_CANDIDATES),
    "window_incomplete_candidates": [],
    "missing_proof_flags": {},
    "authority_locks": dict(_AUTHORITY_LOCKS),
    "recommended_next_lane": "P103_RESEARCH_SHADOW_REPLAY_AUDIT",
    "recommended_next_lane_reason": "All stabilized candidates meet gate; proceed to P103.",
    "not_computable_reasons": [],
    "provenance": {"source": "p101"},
}

_REPLAY_HASH = "abc123def456abc123def456abc123def456abc123def456abc123def456abc1"


def _all_true_proof_flags() -> dict[str, bool]:
    return {flag: True for flag in REQUIRED_REPLAY_PROOF_FLAGS}


def _complete_replay_observations() -> dict[str, Any]:
    return {
        "candidate_replay_observations": {
            candidate_id: {
                "replay_run_hashes": [_REPLAY_HASH] * 12,
                "proof_flags": _all_true_proof_flags(),
            }
            for candidate_id in _WINDOW_COMPLETE_CANDIDATES
        }
    }


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_output_across_repeated_runs() -> None:
    observations = _complete_replay_observations()
    first = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=observations,
    )
    second = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=observations,
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def test_schema_validates_pass_packet() -> None:
    schema = json.loads(
        Path("contracts/canon/research_shadow_replay_audit.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    packet = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=_complete_replay_observations(),
    )
    validate(packet, schema)


def test_schema_validates_continue_packet() -> None:
    schema = json.loads(
        Path("contracts/canon/research_shadow_replay_audit.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    packet = build_research_shadow_replay_audit(p102_packet=_VALID_P102_PACKET)
    validate(packet, schema)


def test_schema_validates_not_computable_packet() -> None:
    schema = json.loads(
        Path("contracts/canon/research_shadow_replay_audit.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    packet = build_research_shadow_replay_audit(p102_packet=None)
    validate(packet, schema)


# ---------------------------------------------------------------------------
# P102 missing / malformed / wrong-chain / non-emitted
# ---------------------------------------------------------------------------


def test_p102_missing_returns_not_computable() -> None:
    packet = build_research_shadow_replay_audit(p102_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p102_packet_missing" in packet["not_computable_reasons"]


def test_malformed_p102_returns_not_computable() -> None:
    packet = build_research_shadow_replay_audit(
        p102_packet="bad"  # type: ignore[arg-type]
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p102_packet_malformed" in r for r in packet["not_computable_reasons"])


def test_wrong_chain_p102_returns_not_computable() -> None:
    packet = build_research_shadow_replay_audit(
        p102_packet={**_VALID_P102_PACKET, "recommended_next_lane": "P999_WRONG"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p102_recommendation_chain_mismatch" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_non_emitted_p102_returns_not_computable() -> None:
    packet = build_research_shadow_replay_audit(
        p102_packet={
            **_VALID_P102_PACKET,
            "status": "NOT_COMPUTABLE",
            "stabilization_window_monitor_status": "NOT_COMPUTABLE",
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p102_status_not_emitted_or_rejected_drift" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_p102_without_p103_recommendation_never_recommends_p104() -> None:
    packet = build_research_shadow_replay_audit(
        p102_packet={**_VALID_P102_PACKET, "recommended_next_lane": "P102_CONTINUE"}
    )
    assert packet["recommended_next_lane"] != "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS"
    assert packet["status"] == "NOT_COMPUTABLE"


def test_no_window_complete_candidates_returns_not_computable() -> None:
    packet = build_research_shadow_replay_audit(
        p102_packet={**_VALID_P102_PACKET, "window_complete_candidates": []}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["not_computable_reasons"] == ["p102_no_window_complete_candidates"]


# ---------------------------------------------------------------------------
# Authority drift
# ---------------------------------------------------------------------------


def test_p102_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_shadow_replay_audit(
        p102_packet={
            **_VALID_P102_PACKET,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "stabilization_window_monitor_status": "REJECTED_AUTHORITY_DRIFT",
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"
    assert packet["shadow_replay_audit_status"] == "REJECTED_AUTHORITY_DRIFT"


def test_p102_authority_lock_true_returns_rejected_authority_drift() -> None:
    packet = build_research_shadow_replay_audit(
        p102_packet={
            **_VALID_P102_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS, "runtime_mutation": True},
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_replay_observation_authority_drift_returns_rejected_authority_drift() -> None:
    observations = _complete_replay_observations()
    candidate_id = _WINDOW_COMPLETE_CANDIDATES[0]
    observations["candidate_replay_observations"][candidate_id]["proof_flags"][
        "authority_lock_invariance_observed"
    ] = False
    packet = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=observations,
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"
    assert packet["shadow_replay_audit_status"] == "REJECTED_AUTHORITY_DRIFT"


# ---------------------------------------------------------------------------
# Replay observation scenarios
# ---------------------------------------------------------------------------


def test_default_missing_replay_observations_recommend_continue() -> None:
    packet = build_research_shadow_replay_audit(p102_packet=_VALID_P102_PACKET)
    assert packet["recommended_next_lane"] == "P103_RESEARCH_SHADOW_REPLAY_AUDIT_CONTINUE"
    for cs in packet["candidate_replay_statuses"]:
        assert cs["shadow_replay_status"] == "REPLAY_NOT_STARTED"


def test_12_identical_hashes_all_proofs_recommend_p104() -> None:
    packet = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=_complete_replay_observations(),
    )
    assert packet["recommended_next_lane"] == "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS"
    assert packet["status"] == "SHADOW_REPLAY_AUDIT_EMITTED"
    for cs in packet["candidate_replay_statuses"]:
        assert cs["shadow_replay_status"] == "REPLAY_PASS"


def test_fewer_than_12_replay_hashes_blocks_p104() -> None:
    observations: dict[str, Any] = {
        "candidate_replay_observations": {
            candidate_id: {
                "replay_run_hashes": [_REPLAY_HASH] * 11,
                "proof_flags": _all_true_proof_flags(),
            }
            for candidate_id in _WINDOW_COMPLETE_CANDIDATES
        }
    }
    packet = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] != "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS"
    for cs in packet["candidate_replay_statuses"]:
        assert cs["shadow_replay_status"] == "REPLAY_IN_PROGRESS"


def test_divergent_replay_hashes_produce_fail_and_block_p104() -> None:
    observations: dict[str, Any] = {
        "candidate_replay_observations": {
            candidate_id: {
                "replay_run_hashes": [_REPLAY_HASH] * 11 + ["different_hash_xyz"],
                "proof_flags": _all_true_proof_flags(),
            }
            for candidate_id in _WINDOW_COMPLETE_CANDIDATES
        }
    }
    packet = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] != "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS"
    for cs in packet["candidate_replay_statuses"]:
        assert cs["shadow_replay_status"] == "REPLAY_FAIL_HASH_DIVERGENCE"
        assert not cs["identical_replay_hashes"]
        assert "replay_hash_divergence" in cs["missing_replay_requirements"]


def test_missing_proof_flags_produce_blocked_and_block_p104() -> None:
    observations = _complete_replay_observations()
    candidate_id = _WINDOW_COMPLETE_CANDIDATES[0]
    observations["candidate_replay_observations"][candidate_id]["proof_flags"][
        "operator_review_observed"
    ] = False
    packet = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] != "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS"
    blocked = next(
        cs
        for cs in packet["candidate_replay_statuses"]
        if cs["candidate_id"] == candidate_id
    )
    assert blocked["shadow_replay_status"] == "REPLAY_BLOCKED_MISSING_PROOFS"
    assert "operator_review_observed" in blocked["missing_replay_requirements"]


# ---------------------------------------------------------------------------
# Candidate list preservation and audit scope
# ---------------------------------------------------------------------------


def test_held_repair_rejected_candidates_preserved_separately() -> None:
    packet = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=_complete_replay_observations(),
    )
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]
    assert packet["repair_candidates"] == [
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"
    ]
    assert packet["rejected_candidates"] == [
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"
    ]


def test_only_window_complete_candidates_are_audited() -> None:
    packet = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=_complete_replay_observations(),
    )
    audited_ids = {cs["candidate_id"] for cs in packet["candidate_replay_statuses"]}
    assert audited_ids == set(_WINDOW_COMPLETE_CANDIDATES)
    # held/repair/rejected must not appear in audited
    assert "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER" not in audited_ids
    assert "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER" not in audited_ids
    assert "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER" not in audited_ids


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------


def test_all_authority_locks_remain_false() -> None:
    emitted = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=_complete_replay_observations(),
    )
    blocked = build_research_shadow_replay_audit(p102_packet=None)
    rejected = build_research_shadow_replay_audit(
        p102_packet={
            **_VALID_P102_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS, "canon_promotion": True},
        }
    )
    assert emitted["authority_locks"] == _AUTHORITY_LOCKS
    assert blocked["authority_locks"] == _AUTHORITY_LOCKS
    assert rejected["authority_locks"] == _AUTHORITY_LOCKS


# ---------------------------------------------------------------------------
# Packet hash
# ---------------------------------------------------------------------------


def test_packet_hash_is_deterministic_and_excludes_itself() -> None:
    observations = _complete_replay_observations()
    p1 = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=observations,
    )
    p2 = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=observations,
    )
    assert p1["packet_hash"] == p2["packet_hash"]
    # packet_hash must not be a key in the hashed payload
    import hashlib
    payload_without_hash = {k: v for k, v in p1.items() if k != "packet_hash"}
    canonical = json.dumps(
        payload_without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert p1["packet_hash"] == expected_hash


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------


def test_output_writer_emits_canonical_json_with_trailing_newline(
    tmp_path: Path,
) -> None:
    packet = build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=_complete_replay_observations(),
    )
    out_path = tmp_path / "audit.json"
    write_research_shadow_replay_audit(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    loaded = json.loads(text)
    assert loaded["packet_hash"] == packet["packet_hash"]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_shadow_replay_audit" / "latest.json"
    observations = _complete_replay_observations()
    first = run_research_shadow_replay_audit.run(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=observations,
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_research_shadow_replay_audit.run(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=observations,
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_runner_supports_p102_path_and_replay_observations_path(
    tmp_path: Path,
) -> None:
    assert str(P102_DEFAULT_PATH) == "out/research_stabilization_window_monitor/latest.json"

    missing = _load_json_packet(tmp_path / "missing.json")
    assert missing is None

    bad_path = tmp_path / "bad.json"
    bad_path.write_text("{not json", encoding="utf-8")
    assert _load_json_packet(bad_path) is None

    payload_path = tmp_path / "p102.json"
    payload_path.write_text(json.dumps(_VALID_P102_PACKET), encoding="utf-8")
    loaded = _load_json_packet(payload_path)
    assert isinstance(loaded, dict)
    assert loaded["artifact_type"] == "ResearchStabilizationWindowMonitor.v1"

    default_args = _parse_args([])
    assert (
        default_args.p102_path
        == "out/research_stabilization_window_monitor/latest.json"
    )
    assert default_args.replay_observations_path is None

    obs_path = str(tmp_path / "observations.json")
    custom_args = _parse_args(
        [
            "--p102-path",
            str(payload_path),
            "--replay-observations-path",
            obs_path,
        ]
    )
    assert custom_args.p102_path == str(payload_path)
    assert custom_args.replay_observations_path == obs_path


# ---------------------------------------------------------------------------
# Generated out/ artifacts untouched
# ---------------------------------------------------------------------------


def test_generated_out_artifacts_remain_untouched() -> None:
    validation_path = Path("out/validation/latest.json")
    aal_viz_path = Path("out/projections/aal_viz.latest.json")

    validation_hash_before = (
        validation_path.read_bytes() if validation_path.exists() else None
    )
    aal_viz_hash_before = aal_viz_path.read_bytes() if aal_viz_path.exists() else None

    # Running P103 must not modify these files
    build_research_shadow_replay_audit(
        p102_packet=_VALID_P102_PACKET,
        replay_observations_packet=_complete_replay_observations(),
    )

    if validation_hash_before is not None:
        assert validation_path.read_bytes() == validation_hash_before
    if aal_viz_hash_before is not None:
        assert aal_viz_path.read_bytes() == aal_viz_hash_before
