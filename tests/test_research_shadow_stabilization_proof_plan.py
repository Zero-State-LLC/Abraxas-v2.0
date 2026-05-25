from __future__ import annotations

import json
from pathlib import Path

from core.research_shadow_stabilization_proof_plan import (
    build_research_shadow_stabilization_proof_plan,
    write_research_shadow_stabilization_proof_plan,
)
from scripts import run_research_shadow_stabilization_proof_plan
from scripts.run_research_shadow_stabilization_proof_plan import _load_p97_packet

_VALID_P97_PACKET: dict[str, object] = {
    "artifact_type": "ResearchDerivedSubsystemCandidateLedger.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER",
    "status": "PASS",
    "candidate_ledger_status": "READY",
    "subsystem_candidates": [
        {
            "drop_id": "DROP006",
            "candidate_id": "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER",
            "status": "SHADOW_CANDIDATE_ONLY",
            "primary_targets": ["Skill Runtime Ontology"],
            "candidate_contracts": ["IndirectDependencyTrace.v1"],
        },
        {
            "drop_id": "DROP006",
            "candidate_id": "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
            "status": "SHADOW_CANDIDATE_ONLY",
            "primary_targets": ["Oracle Signal Layer"],
            "candidate_contracts": ["IntendedEndpointConstraint.v1"],
        },
        {
            "drop_id": "DROP006",
            "candidate_id": "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER",
            "status": "SHADOW_CANDIDATE_ONLY",
            "primary_targets": ["PSE calibration surfaces"],
            "candidate_contracts": ["IsotonicCalibrationProjection.v1"],
        },
        {
            "drop_id": "DROP007",
            "candidate_id": "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
            "status": "SHADOW_CANDIDATE_ONLY",
            "primary_targets": ["AAL-Viz operator projection"],
            "candidate_contracts": ["HiddenIntentCandidate.v1"],
        },
        {
            "drop_id": "DROP007",
            "candidate_id": "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER",
            "status": "SHADOW_CANDIDATE_ONLY",
            "primary_targets": ["YGGDRASIL topology"],
            "candidate_contracts": ["CoordinationThreshold.v1"],
        },
        {
            "drop_id": "DROP007",
            "candidate_id": "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER",
            "status": "SHADOW_CANDIDATE_ONLY",
            "primary_targets": ["AAL-Viz projection"],
            "candidate_contracts": ["InterleavedIntentTrace.v1"],
        },
    ],
    "target_subsystems": ["Skill Runtime Ontology", "AAL-Viz projection"],
    "stabilization_requirements": [
        "12-run invariance proof required",
        "authority-lock invariance proof required",
    ],
    "authority_locks": {
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
    },
    "recommended_next_lane": "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN",
    "provenance": {"source": "p96_research_fold_validation_plan"},
}

_AUTHORITY_LOCK_FIELDS = {
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
}

_REQUIRED_PROOFS = {
    "12-run invariance proof required",
    "authority-lock invariance proof required",
    "NOT_COMPUTABLE failure proof required",
    "AAL-Viz projection-only proof required",
    "cross-drop conflict scan required",
    "operator review hold required",
}


def test_deterministic_repeated_output() -> None:
    first = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    second = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_p97_missing_returns_not_computable() -> None:
    packet = build_research_shadow_stabilization_proof_plan(p97_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p97_packet_missing" in packet["not_computable_reasons"]
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_p97_malformed_returns_not_computable() -> None:
    packet = build_research_shadow_stabilization_proof_plan(  # type: ignore[arg-type]
        p97_packet="not_a_dict"
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p97_packet_malformed" in r for r in packet["not_computable_reasons"])


def test_p97_non_pass_returns_not_computable() -> None:
    packet = build_research_shadow_stabilization_proof_plan(
        p97_packet={**_VALID_P97_PACKET, "status": "NOT_COMPUTABLE"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p97_status_not_pass" in r for r in packet["not_computable_reasons"])


def test_p97_authority_drift_returns_not_computable() -> None:
    drifted = {**_VALID_P97_PACKET["authority_locks"], "runtime_mutation": True}  # type: ignore[arg-type]
    packet = build_research_shadow_stabilization_proof_plan(
        p97_packet={**_VALID_P97_PACKET, "authority_locks": drifted}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("authority_drift" in r for r in packet["not_computable_reasons"])


def test_p97_missing_required_drop_returns_not_computable() -> None:
    only_drop006 = [
        candidate
        for candidate in _VALID_P97_PACKET["subsystem_candidates"]  # type: ignore[index]
        if candidate["drop_id"] == "DROP006"
    ]
    packet = build_research_shadow_stabilization_proof_plan(
        p97_packet={**_VALID_P97_PACKET, "subsystem_candidates": only_drop006}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "p97_required_drop_candidates_missing" in r
        for r in packet["not_computable_reasons"]
    )


def test_all_authority_locks_remain_false_even_when_upstream_drifted() -> None:
    pass_packet = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    drifted_locks = {field: True for field in _AUTHORITY_LOCK_FIELDS}
    blocked_packet = build_research_shadow_stabilization_proof_plan(
        p97_packet={**_VALID_P97_PACKET, "authority_locks": drifted_locks}
    )
    assert set(pass_packet["authority_locks"]) == _AUTHORITY_LOCK_FIELDS
    assert all(v is False for v in pass_packet["authority_locks"].values())
    assert all(v is False for v in blocked_packet["authority_locks"].values())


def test_candidate_proof_requirements_present_for_drop006_and_drop007() -> None:
    packet = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    assert packet["status"] == "PASS"

    requirements = packet["stabilization_proof_requirements"]
    assert len(requirements) == 6

    drop_ids = {item["drop_id"] for item in requirements}
    assert drop_ids == {"DROP006", "DROP007"}

    for item in requirements:
        assert set(item["proof_requirements"]) == _REQUIRED_PROOFS
        assert item["stabilization_execution"] == "PROHIBITED_IN_P98"


def test_global_requirements_include_not_computable_and_projection_only_proofs() -> None:
    packet = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    assert set(packet["global_proof_requirements"]) == _REQUIRED_PROOFS
    assert packet["cross_drop_conflict_scan_required"] is True
    assert packet["operator_review_hold_required"] is True


def test_recommended_next_lane_is_p99_only_on_pass() -> None:
    pass_packet = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    assert pass_packet["recommended_next_lane"] == "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN"

    blocked_packet = build_research_shadow_stabilization_proof_plan(p97_packet=None)
    assert blocked_packet["recommended_next_lane"] != "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN"


def test_schema_locks_authority_fields_false() -> None:
    schema = json.loads(
        Path(
            "contracts/canon/research_shadow_stabilization_proof_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    for field in _AUTHORITY_LOCK_FIELDS:
        assert schema["properties"]["authority_locks"]["properties"][field]["const"] is False


def test_writer_final_newline(tmp_path: Path) -> None:
    packet = build_research_shadow_stabilization_proof_plan(p97_packet=_VALID_P97_PACKET)
    out_path = tmp_path / "research_shadow_stabilization_proof_plan_test.json"
    write_research_shadow_stabilization_proof_plan(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_shadow_stabilization_proof_plan" / "latest.json"
    first = run_research_shadow_stabilization_proof_plan.run(
        p97_packet=_VALID_P97_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")

    second = run_research_shadow_stabilization_proof_plan.run(
        p97_packet=_VALID_P97_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")

    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_load_p97_packet_missing_returns_none(tmp_path: Path) -> None:
    assert _load_p97_packet(tmp_path / "nonexistent.json") is None


def test_load_p97_packet_malformed_json_returns_none(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    assert _load_p97_packet(bad) is None


def test_load_p97_packet_non_dict_returns_none(tmp_path: Path) -> None:
    arr = tmp_path / "arr.json"
    arr.write_text("[1, 2, 3]", encoding="utf-8")
    assert _load_p97_packet(arr) is None


def test_load_p97_packet_valid_returns_dict(tmp_path: Path) -> None:
    p = tmp_path / "p97.json"
    p.write_text(json.dumps(_VALID_P97_PACKET), encoding="utf-8")
    loaded = _load_p97_packet(p)
    assert isinstance(loaded, dict)
    assert loaded["artifact_type"] == "ResearchDerivedSubsystemCandidateLedger.v1"


def test_p97_default_path_constant() -> None:
    from scripts.run_research_shadow_stabilization_proof_plan import P97_DEFAULT_PATH

    assert str(P97_DEFAULT_PATH) == "out/research_derived_subsystem_candidate_ledger/latest.json"


def test_parse_args_default_p97_path() -> None:
    from scripts.run_research_shadow_stabilization_proof_plan import _parse_args

    args = _parse_args([])
    assert args.p97_path == "out/research_derived_subsystem_candidate_ledger/latest.json"


def test_parse_args_custom_p97_path(tmp_path: Path) -> None:
    from scripts.run_research_shadow_stabilization_proof_plan import _parse_args

    custom = str(tmp_path / "my_p97.json")
    args = _parse_args(["--p97-path", custom])
    assert args.p97_path == custom
