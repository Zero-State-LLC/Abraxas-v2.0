from __future__ import annotations

import json
from pathlib import Path

from core.research_derived_subsystem_candidate_ledger import (
    build_research_derived_subsystem_candidate_ledger,
    write_research_derived_subsystem_candidate_ledger,
)
from scripts import run_research_derived_subsystem_candidate_ledger
from scripts.run_research_derived_subsystem_candidate_ledger import _load_p96_packet

_VALID_P96_PACKET: dict[str, object] = {
    "artifact_type": "ResearchFoldValidationPlan.v1",
    "canonical_status": "ADVISORY_ONLY",
    "advisory_only": True,
    "projection_only": True,
    "lane_id": "P96_RESEARCH_FOLD_VALIDATION_PLAN",
    "status": "PASS",
    "fixture_plan": [
        {"drop_id": "DROP006", "fixture_targets": ["fixture_drop006_intent_graph_valid.json"]},
        {
            "drop_id": "DROP007",
            "fixture_targets": ["fixture_drop007_hidden_intent_candidate_valid.json"],
        },
    ],
    "positive_proof_packet_plan": {
        "authority_locks_remain_false": True,
        "aal_viz_projection_only_posture_preserved": True,
    },
    "negative_failure_proof_packet_plan": {
        "rejected_conditions": ["hidden_intent_marked_as_known_intent"],
    },
    "operator_review_requirements": ["confirm_authority_locks_all_false_before_any_lane_transition"],
    "aal_viz_projection_constraints": ["aal_viz_projection_only"],
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
    "recommended_next_lane": "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER",
    "provenance": {
        "source": "p95_research_fold_drop_spec_builder",
    },
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

_EXPECTED_CANDIDATE_ORDER = [
    "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER",
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
    "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER",
    "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER",
]

_EXPECTED_STABILIZATION_REQUIREMENTS = {
    "12-run invariance proof required",
    "authority-lock invariance proof required",
    "NOT_COMPUTABLE failure proof required",
    "AAL-Viz projection-only proof required",
    "cross-drop conflict scan required",
    "operator review hold required",
}


def test_deterministic_repeated_output() -> None:
    first = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    second = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_p96_missing_returns_not_computable() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p96_packet_missing" in packet["not_computable_reasons"]
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["subsystem_candidates"] == []


def test_p96_malformed_returns_not_computable() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(  # type: ignore[arg-type]
        p96_packet="not_a_dict"
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p96_packet_malformed" in reason for reason in packet["not_computable_reasons"])


def test_p96_failed_returns_not_computable() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(
        p96_packet={**_VALID_P96_PACKET, "status": "NOT_COMPUTABLE"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p96_status_not_pass" in reason for reason in packet["not_computable_reasons"])


def test_p96_structurally_invalid_returns_not_computable() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(
        p96_packet={**_VALID_P96_PACKET, "fixture_plan": "bad"}  # type: ignore[dict-item]
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p96_fixture_plan_malformed" in packet["not_computable_reasons"]


def test_p96_authority_drift_returns_not_computable() -> None:
    drifted = {**_VALID_P96_PACKET["authority_locks"], "runtime_mutation": True}  # type: ignore[arg-type]
    packet = build_research_derived_subsystem_candidate_ledger(
        p96_packet={**_VALID_P96_PACKET, "authority_locks": drifted}
    )
    assert packet["status"] in {"NOT_COMPUTABLE", "REJECTED"}
    assert any("authority_drift" in reason for reason in packet["not_computable_reasons"])


def test_all_candidates_are_shadow_candidate_only() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    assert packet["status"] == "PASS"
    assert all(
        candidate["status"] == "SHADOW_CANDIDATE_ONLY"
        for candidate in packet["subsystem_candidates"]
    )


def test_drop_006_candidates_appear_before_drop_007_candidates() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    drop_ids = [candidate["drop_id"] for candidate in packet["subsystem_candidates"]]
    assert drop_ids[:3] == ["DROP006", "DROP006", "DROP006"]
    assert drop_ids[3:] == ["DROP007", "DROP007", "DROP007"]


def test_candidate_ordering_is_stable() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    candidate_ids = [candidate["candidate_id"] for candidate in packet["subsystem_candidates"]]
    assert candidate_ids == _EXPECTED_CANDIDATE_ORDER


def test_required_drop_006_and_drop_007_candidates_are_present() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    candidate_ids = {candidate["candidate_id"] for candidate in packet["subsystem_candidates"]}
    assert candidate_ids == set(_EXPECTED_CANDIDATE_ORDER)


def test_target_subsystems_are_included() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    assert "Skill Runtime Ontology" in packet["target_subsystems"]
    assert "AAL-Viz projection" in packet["target_subsystems"]
    assert "Phase Percolation Engine" in packet["target_subsystems"]


def test_stabilization_requirements_are_included() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    assert set(packet["stabilization_requirements"]) == _EXPECTED_STABILIZATION_REQUIREMENTS


def test_authority_locks_cannot_become_true() -> None:
    pass_packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    blocked_packet = build_research_derived_subsystem_candidate_ledger(
        p96_packet={**_VALID_P96_PACKET, "authority_locks": {field: True for field in _AUTHORITY_LOCK_FIELDS}}
    )
    assert set(pass_packet["authority_locks"]) == _AUTHORITY_LOCK_FIELDS
    assert all(value is False for value in pass_packet["authority_locks"].values())
    assert all(value is False for value in blocked_packet["authority_locks"].values())


def test_recommended_next_lane_is_p98_only_on_pass() -> None:
    pass_packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    assert pass_packet["recommended_next_lane"] == "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN"

    blocked_packet = build_research_derived_subsystem_candidate_ledger(p96_packet=None)
    assert blocked_packet["recommended_next_lane"] != "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN"


def test_schema_locks_authority_fields_false_and_shadow_status() -> None:
    schema = json.loads(
        Path(
            "contracts/canon/research_derived_subsystem_candidate_ledger.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    for field in _AUTHORITY_LOCK_FIELDS:
        assert schema["properties"]["authority_locks"]["properties"][field]["const"] is False
    assert (
        schema["properties"]["subsystem_candidates"]["items"]["properties"]["status"]["const"]
        == "SHADOW_CANDIDATE_ONLY"
    )


def test_writer_final_newline() -> None:
    packet = build_research_derived_subsystem_candidate_ledger(p96_packet=_VALID_P96_PACKET)
    out_path = Path("tests/.tmp_research_derived_subsystem_candidate_ledger.json")
    try:
        write_research_derived_subsystem_candidate_ledger(out_path, packet)
        assert out_path.read_text(encoding="utf-8").endswith("\n")
    finally:
        out_path.unlink(missing_ok=True)


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_derived_subsystem_candidate_ledger" / "latest.json"
    first = run_research_derived_subsystem_candidate_ledger.run(
        p96_packet=_VALID_P96_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")

    second = run_research_derived_subsystem_candidate_ledger.run(
        p96_packet=_VALID_P96_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")

    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_load_p96_packet_missing_returns_none(tmp_path: Path) -> None:
    assert _load_p96_packet(tmp_path / "nonexistent.json") is None


def test_load_p96_packet_malformed_json_returns_none(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    assert _load_p96_packet(bad) is None


def test_load_p96_packet_non_dict_returns_none(tmp_path: Path) -> None:
    arr = tmp_path / "arr.json"
    arr.write_text("[1, 2, 3]", encoding="utf-8")
    assert _load_p96_packet(arr) is None


def test_load_p96_packet_valid_returns_dict(tmp_path: Path) -> None:
    p = tmp_path / "p96.json"
    p.write_text(json.dumps(_VALID_P96_PACKET), encoding="utf-8")
    loaded = _load_p96_packet(p)
    assert isinstance(loaded, dict)
    assert loaded["artifact_type"] == "ResearchFoldValidationPlan.v1"


def test_p96_default_path_constant() -> None:
    from scripts.run_research_derived_subsystem_candidate_ledger import P96_DEFAULT_PATH

    assert str(P96_DEFAULT_PATH) == "out/research_fold_validation_plan/latest.json"


def test_parse_args_default_p96_path() -> None:
    from scripts.run_research_derived_subsystem_candidate_ledger import _parse_args

    args = _parse_args([])
    assert args.p96_path == "out/research_fold_validation_plan/latest.json"


def test_parse_args_custom_p96_path(tmp_path: Path) -> None:
    from scripts.run_research_derived_subsystem_candidate_ledger import _parse_args

    custom = str(tmp_path / "my_p96.json")
    args = _parse_args(["--p96-path", custom])
    assert args.p96_path == custom
