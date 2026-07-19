from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from core.research_promotion_blocker_ledger import (
    MANDATORY_BLOCKER_CATEGORIES,
    build_research_promotion_blocker_ledger,
    write_research_promotion_blocker_ledger,
)
from scripts.research import run_research_promotion_blocker_ledger
from scripts.research.run_research_promotion_blocker_ledger import (
    P104_DEFAULT_PATH,
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

_BOUNDARY_STABLE_CANDIDATES = [
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
]

_VALID_P104_PACKET: dict[str, Any] = {
    "artifact_type": "ResearchBoundaryDecayAnalysis.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS",
    "status": "BOUNDARY_DECAY_ANALYSIS_EMITTED",
    "upstream_lane_id": "P103_RESEARCH_SHADOW_REPLAY_AUDIT",
    "upstream_shadow_replay_audit_status": "SHADOW_REPLAY_AUDIT_EMITTED",
    "boundary_decay_analysis_status": "BOUNDARY_STABLE",
    "stabilized_candidates": list(_BOUNDARY_STABLE_CANDIDATES),
    "held_candidates": ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"],
    "repair_candidates": ["DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"],
    "rejected_candidates": ["DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"],
    "analyzed_candidates": list(_BOUNDARY_STABLE_CANDIDATES),
    "boundary_stable_candidates": list(_BOUNDARY_STABLE_CANDIDATES),
    "boundary_decay_candidates": [],
    "boundary_incomplete_candidates": [],
    "candidate_boundary_statuses": [],
    "missing_boundary_requirements": {},
    "authority_locks": dict(_AUTHORITY_LOCKS),
    "recommended_next_lane": "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER",
    "recommended_next_lane_reason": "Proceed to P105.",
    "not_computable_reasons": [],
    "provenance": {"source": "p103"},
}


def _complete_observations() -> dict[str, Any]:
    return {
        "candidate_blocker_observations": {
            candidate_id: {
                "candidate_id": candidate_id,
                "reviewed_blocker_categories": list(MANDATORY_BLOCKER_CATEGORIES),
                "active_blocker_categories": [],
                "waived_blocker_categories": [],
                "blocker_review_complete": True,
                "operator_review_observed": True,
                "provenance_complete_observed": True,
                "replay_stability_observed": True,
                "boundary_stability_observed": True,
                "authority_drift_observed": False,
                "notes": "all blockers reviewed",
            }
            for candidate_id in _BOUNDARY_STABLE_CANDIDATES
        }
    }


def _schema() -> dict[str, Any]:
    return json.loads(
        Path(
            "contracts/canon/research_promotion_blocker_ledger.v1.schema.json"
        ).read_text(encoding="utf-8")
    )


def test_deterministic_output_across_repeated_runs() -> None:
    observations = _complete_observations()
    first = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=observations,
    )
    second = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=observations,
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_schema_validates_representative_blocked_packet() -> None:
    packet = build_research_promotion_blocker_ledger(p104_packet=_VALID_P104_PACKET)
    validate(packet, _schema())


def test_schema_validates_representative_complete_packet() -> None:
    packet = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=_complete_observations(),
    )
    validate(packet, _schema())


def test_schema_validates_representative_failure_packet() -> None:
    packet = build_research_promotion_blocker_ledger(p104_packet=None)
    validate(packet, _schema())


def test_p104_missing_returns_not_computable() -> None:
    packet = build_research_promotion_blocker_ledger(p104_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p104_packet_missing" in packet["not_computable_reasons"]


def test_malformed_p104_returns_not_computable() -> None:
    packet = build_research_promotion_blocker_ledger(
        p104_packet="bad"  # type: ignore[arg-type]
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["not_computable_reasons"] == ["p104_packet_malformed:not_a_dict"]


def test_wrong_chain_p104_returns_not_computable() -> None:
    packet = build_research_promotion_blocker_ledger(
        p104_packet={**_VALID_P104_PACKET, "recommended_next_lane": "P999_WRONG"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p104_recommendation_chain_mismatch" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_non_emitted_non_pass_p104_returns_not_computable() -> None:
    packet = build_research_promotion_blocker_ledger(
        p104_packet={
            **_VALID_P104_PACKET,
            "status": "NOT_COMPUTABLE",
            "boundary_decay_analysis_status": "NOT_COMPUTABLE",
        }
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p104_status_not_emitted_stable" in reason
        for reason in packet["not_computable_reasons"]
    )


def test_p104_without_p105_recommendation_never_recommends_p106() -> None:
    packet = build_research_promotion_blocker_ledger(
        p104_packet={
            **_VALID_P104_PACKET,
            "recommended_next_lane": "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS_CONTINUE",
        },
        blocker_observations_packet=_complete_observations(),
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] != "P106_RESEARCH_CANARY_ELIGIBILITY_DOSSIER"


def test_no_boundary_stable_candidates_returns_not_computable() -> None:
    packet = build_research_promotion_blocker_ledger(
        p104_packet={**_VALID_P104_PACKET, "boundary_stable_candidates": []}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["not_computable_reasons"] == ["p104_no_boundary_stable_candidates"]


def test_p104_authority_drift_returns_rejected_authority_drift() -> None:
    packet = build_research_promotion_blocker_ledger(
        p104_packet={
            **_VALID_P104_PACKET,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "boundary_decay_analysis_status": "REJECTED_AUTHORITY_DRIFT",
        }
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_blocker_observation_authority_drift_returns_rejected_authority_drift() -> None:
    observations = _complete_observations()
    observations["candidate_blocker_observations"][_BOUNDARY_STABLE_CANDIDATES[0]][
        "authority_drift_observed"
    ] = True
    packet = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=observations,
    )
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"


def test_default_missing_blocker_observations_marks_active_and_recommends_continue() -> None:
    packet = build_research_promotion_blocker_ledger(p104_packet=_VALID_P104_PACKET)
    assert (
        packet["recommended_next_lane"]
        == "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER_CONTINUE"
    )
    for candidate_status in packet["candidate_blocker_statuses"]:
        assert candidate_status["promotion_blocker_status"] == "PROMOTION_BLOCKED"
        assert set(candidate_status["active_blocker_categories"]) == set(
            MANDATORY_BLOCKER_CATEGORIES
        )


def test_incomplete_blocker_review_blocks_p106() -> None:
    observations = _complete_observations()
    observations["candidate_blocker_observations"][_BOUNDARY_STABLE_CANDIDATES[0]][
        "blocker_review_complete"
    ] = False
    packet = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] != "P106_RESEARCH_CANARY_ELIGIBILITY_DOSSIER"


def test_complete_blocker_review_for_every_candidate_recommends_p106() -> None:
    packet = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=_complete_observations(),
    )
    assert packet["recommended_next_lane"] == "P106_RESEARCH_CANARY_ELIGIBILITY_DOSSIER"


def test_missing_operator_review_observed_blocks_p106() -> None:
    observations = _complete_observations()
    observations["candidate_blocker_observations"][_BOUNDARY_STABLE_CANDIDATES[0]][
        "operator_review_observed"
    ] = False
    packet = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] == "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER_CONTINUE"


def test_missing_provenance_complete_observed_blocks_p106() -> None:
    observations = _complete_observations()
    observations["candidate_blocker_observations"][_BOUNDARY_STABLE_CANDIDATES[0]][
        "provenance_complete_observed"
    ] = False
    packet = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] == "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER_CONTINUE"


def test_missing_replay_stability_observed_blocks_p106() -> None:
    observations = _complete_observations()
    observations["candidate_blocker_observations"][_BOUNDARY_STABLE_CANDIDATES[0]][
        "replay_stability_observed"
    ] = False
    packet = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] == "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER_CONTINUE"


def test_missing_boundary_stability_observed_blocks_p106() -> None:
    observations = _complete_observations()
    observations["candidate_blocker_observations"][_BOUNDARY_STABLE_CANDIDATES[0]][
        "boundary_stability_observed"
    ] = False
    packet = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=observations,
    )
    assert packet["recommended_next_lane"] == "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER_CONTINUE"


def test_waived_blockers_do_not_bypass_review_requirements() -> None:
    observations = _complete_observations()
    observations["candidate_blocker_observations"][_BOUNDARY_STABLE_CANDIDATES[0]] = {
        "candidate_id": _BOUNDARY_STABLE_CANDIDATES[0],
        "reviewed_blocker_categories": ["operator_review_blocker"],
        "active_blocker_categories": [],
        "waived_blocker_categories": ["implementation_authority_blocker"],
        "blocker_review_complete": False,
        "operator_review_observed": False,
        "provenance_complete_observed": False,
        "replay_stability_observed": False,
        "boundary_stability_observed": False,
        "authority_drift_observed": False,
    }
    packet = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=observations,
    )
    status = next(
        entry
        for entry in packet["candidate_blocker_statuses"]
        if entry["candidate_id"] == _BOUNDARY_STABLE_CANDIDATES[0]
    )
    assert "implementation_authority_blocker" in status["active_blocker_categories"]
    assert packet["recommended_next_lane"] == "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER_CONTINUE"


def test_held_repair_rejected_candidates_are_preserved_separately() -> None:
    packet = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=_complete_observations(),
    )
    assert packet["held_candidates"] == ["DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"]
    assert packet["repair_candidates"] == [
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER"
    ]
    assert packet["rejected_candidates"] == [
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER"
    ]


def test_only_boundary_stable_candidates_are_analyzed() -> None:
    packet = build_research_promotion_blocker_ledger(
        p104_packet={
            **_VALID_P104_PACKET,
            "boundary_stable_candidates": [_BOUNDARY_STABLE_CANDIDATES[0]],
        },
        blocker_observations_packet=_complete_observations(),
    )
    analyzed_ids = {status["candidate_id"] for status in packet["candidate_blocker_statuses"]}
    assert analyzed_ids == {_BOUNDARY_STABLE_CANDIDATES[0]}
    assert "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER" not in analyzed_ids


def test_all_authority_locks_remain_false() -> None:
    emitted = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=_complete_observations(),
    )
    blocked = build_research_promotion_blocker_ledger(p104_packet=None)
    rejected = build_research_promotion_blocker_ledger(
        p104_packet={
            **_VALID_P104_PACKET,
            "authority_locks": {**_AUTHORITY_LOCKS, "runtime_mutation": True},
        }
    )
    assert emitted["authority_locks"] == _AUTHORITY_LOCKS
    assert blocked["authority_locks"] == _AUTHORITY_LOCKS
    assert rejected["authority_locks"] == _AUTHORITY_LOCKS


def test_packet_hash_is_deterministic_and_excludes_itself() -> None:
    packet = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=_complete_observations(),
    )
    payload_without_hash = {k: v for k, v in packet.items() if k != "packet_hash"}
    canonical = json.dumps(
        payload_without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert packet["packet_hash"] == expected_hash


def test_output_writer_emits_canonical_json_with_trailing_newline(tmp_path: Path) -> None:
    packet = build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=_complete_observations(),
    )
    out_path = tmp_path / "ledger.json"
    write_research_promotion_blocker_ledger(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    loaded = json.loads(text)
    assert loaded["packet_hash"] == packet["packet_hash"]


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_promotion_blocker_ledger" / "latest.json"
    observations = _complete_observations()
    first = run_research_promotion_blocker_ledger.run(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=observations,
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_research_promotion_blocker_ledger.run(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=observations,
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_runner_supports_p104_path_and_blocker_observations_path(tmp_path: Path) -> None:
    assert str(P104_DEFAULT_PATH) == "out/research_boundary_decay_analysis/latest.json"

    missing = _load_json_packet(tmp_path / "missing.json")
    assert missing is None

    bad_path = tmp_path / "bad.json"
    bad_path.write_text("{not json", encoding="utf-8")
    assert _load_json_packet(bad_path) is None

    payload_path = tmp_path / "p104.json"
    payload_path.write_text(json.dumps(_VALID_P104_PACKET), encoding="utf-8")
    loaded = _load_json_packet(payload_path)
    assert isinstance(loaded, dict)
    assert loaded["artifact_type"] == "ResearchBoundaryDecayAnalysis.v1"

    default_args = _parse_args([])
    assert default_args.p104_path == "out/research_boundary_decay_analysis/latest.json"
    assert default_args.blocker_observations_path is None

    observations_path = str(tmp_path / "observations.json")
    custom_args = _parse_args(
        [
            "--p104-path",
            str(payload_path),
            "--blocker-observations-path",
            observations_path,
        ]
    )
    assert custom_args.p104_path == str(payload_path)
    assert custom_args.blocker_observations_path == observations_path


def test_generated_out_artifacts_remain_untouched() -> None:
    validation_path = Path("out/validation/latest.json")
    aal_viz_path = Path("out/projections/aal_viz.latest.json")

    validation_content_before = validation_path.read_bytes() if validation_path.exists() else None
    aal_viz_content_before = aal_viz_path.read_bytes() if aal_viz_path.exists() else None

    build_research_promotion_blocker_ledger(
        p104_packet=_VALID_P104_PACKET,
        blocker_observations_packet=_complete_observations(),
    )

    if validation_content_before is not None:
        assert validation_path.read_bytes() == validation_content_before
    if aal_viz_content_before is not None:
        assert aal_viz_path.read_bytes() == aal_viz_content_before
