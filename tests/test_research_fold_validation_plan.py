from __future__ import annotations

import json
from pathlib import Path

from core.research_fold_validation_plan import (
    build_research_fold_validation_plan,
    write_research_fold_validation_plan,
)
from scripts import run_research_fold_validation_plan
from scripts.run_research_fold_validation_plan import _load_p95_packet

_VALID_P95_PACKET: dict[str, object] = {
    "artifact_type": "ResearchFoldDropSpecBuilder.v1",
    "status": "PASS",
    "generated_drop_specs": [
        {"drop_id": "DROP006", "spec_id": "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_SPEC"},
        {
            "drop_id": "DROP007",
            "spec_id": "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_SPEC",
        },
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

_DROP_006_FIXTURES = [
    "fixture_drop006_intent_graph_valid.json",
    "fixture_drop006_active_inference_valid.json",
    "fixture_drop006_survival_calibration_valid.json",
    "fixture_drop006_missing_source_not_computable.json",
    "fixture_drop006_authority_escalation_rejected.json",
    "fixture_drop006_forecast_weight_mutation_rejected.json",
]

_DROP_007_FIXTURES = [
    "fixture_drop007_hidden_intent_candidate_valid.json",
    "fixture_drop007_cross_session_dependency_valid.json",
    "fixture_drop007_interleaved_intent_trace_valid.json",
    "fixture_drop007_contextual_intervention_window_valid.json",
    "fixture_drop007_coordination_threshold_valid.json",
    "fixture_drop007_hidden_intent_overclaim_rejected.json",
    "fixture_drop007_operator_bypass_rejected.json",
    "fixture_drop007_autonomous_execution_rejected.json",
]


def test_deterministic_repeated_output() -> None:
    first = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    second = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_p95_missing_returns_not_computable() -> None:
    packet = build_research_fold_validation_plan(p95_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p95_packet_missing" in packet["not_computable_reasons"]
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_p95_malformed_returns_not_computable() -> None:
    packet = build_research_fold_validation_plan(p95_packet="not_a_dict")  # type: ignore[arg-type]
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p95_packet_malformed" in r for r in packet["not_computable_reasons"])


def test_p95_failed_returns_not_computable() -> None:
    packet = build_research_fold_validation_plan(
        p95_packet={**_VALID_P95_PACKET, "status": "NOT_COMPUTABLE"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p95_status_not_pass" in r for r in packet["not_computable_reasons"])


def test_p95_authority_drift_returns_not_computable() -> None:
    drifted_locks = {**_VALID_P95_PACKET["authority_locks"], "operator_bypass": True}  # type: ignore[arg-type]
    packet = build_research_fold_validation_plan(
        p95_packet={**_VALID_P95_PACKET, "authority_locks": drifted_locks}
    )
    assert packet["status"] in {"NOT_COMPUTABLE", "REJECTED"}
    assert any("authority_drift" in r for r in packet["not_computable_reasons"])


def test_fixture_list_is_deterministic() -> None:
    packet = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    assert packet["fixture_plan"] == [
        {"drop_id": "DROP006", "fixture_targets": _DROP_006_FIXTURES},
        {"drop_id": "DROP007", "fixture_targets": _DROP_007_FIXTURES},
    ]


def test_drop_006_and_drop_007_fixture_targets_included() -> None:
    packet = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    fixture_targets = {
        entry["drop_id"]: entry["fixture_targets"] for entry in packet["fixture_plan"]
    }
    assert fixture_targets["DROP006"] == _DROP_006_FIXTURES
    assert fixture_targets["DROP007"] == _DROP_007_FIXTURES


def test_positive_and_negative_proof_packet_plans_included() -> None:
    packet = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    positive_plan = packet["positive_proof_packet_plan"]
    negative_plan = packet["negative_failure_proof_packet_plan"]

    assert positive_plan["authority_locks_remain_false"] is True
    assert positive_plan["advisory_only_posture_preserved"] is True
    assert positive_plan["aal_viz_projection_only_posture_preserved"] is True
    assert positive_plan["next_state"] == "VALIDATION_PLANNING_ONLY"

    rejected_conditions = set(negative_plan["rejected_conditions"])
    assert "hidden_intent_marked_as_known_intent" in rejected_conditions
    assert "proactive_suggestion_marked_autonomous" in rejected_conditions
    assert "intent_graph_dependency_marked_confirmed_intent" in rejected_conditions
    assert "endpoint_constraint_marked_known_goal" in rejected_conditions
    assert "calibration_candidate_mutating_forecast_weights" in rejected_conditions
    assert "aal_viz_claiming_inference_authority" in rejected_conditions
    assert "missing_provenance" in rejected_conditions
    assert "missing_source_identity" in rejected_conditions
    assert "runtime_scheduler_baseline_canon_mutation_request" in rejected_conditions


def test_aal_viz_remains_projection_only() -> None:
    packet = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    constraints = set(packet["aal_viz_projection_constraints"])
    assert "aal_viz_projection_only" in constraints
    assert "aal_viz_no_inference_or_execution_authority_claim" in constraints


def test_authority_locks_always_false() -> None:
    packet = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    assert set(packet["authority_locks"]) == _AUTHORITY_LOCK_FIELDS
    assert all(v is False for v in packet["authority_locks"].values())


def test_recommended_next_lane_p97_only_on_pass() -> None:
    pass_packet = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    assert pass_packet["status"] == "PASS"
    assert pass_packet["recommended_next_lane"] == "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER"

    blocked_packet = build_research_fold_validation_plan(p95_packet=None)
    assert blocked_packet["status"] == "NOT_COMPUTABLE"
    assert blocked_packet["recommended_next_lane"] != "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER"


def test_schema_locks_authority_fields_false() -> None:
    schema = json.loads(
        Path("contracts/canon/research_fold_validation_plan.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    for field in _AUTHORITY_LOCK_FIELDS:
        assert schema["properties"]["authority_locks"]["properties"][field]["const"] is False


def test_writer_final_newline(tmp_path: Path) -> None:
    packet = build_research_fold_validation_plan(p95_packet=_VALID_P95_PACKET)
    out_path = tmp_path / "research_fold_validation_plan_test.json"
    write_research_fold_validation_plan(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_fold_validation_plan" / "latest.json"
    first = run_research_fold_validation_plan.run(
        p95_packet=_VALID_P95_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")

    second = run_research_fold_validation_plan.run(
        p95_packet=_VALID_P95_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")

    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_load_p95_packet_missing_returns_none(tmp_path: Path) -> None:
    assert _load_p95_packet(tmp_path / "nonexistent.json") is None


def test_load_p95_packet_malformed_json_returns_none(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    assert _load_p95_packet(bad) is None


def test_load_p95_packet_non_dict_returns_none(tmp_path: Path) -> None:
    arr = tmp_path / "arr.json"
    arr.write_text("[1, 2, 3]", encoding="utf-8")
    assert _load_p95_packet(arr) is None


def test_load_p95_packet_valid_returns_dict(tmp_path: Path) -> None:
    p = tmp_path / "p95.json"
    p.write_text(json.dumps(_VALID_P95_PACKET), encoding="utf-8")
    loaded = _load_p95_packet(p)
    assert isinstance(loaded, dict)
    assert loaded["artifact_type"] == "ResearchFoldDropSpecBuilder.v1"


def test_p95_default_path_constant() -> None:
    from scripts.run_research_fold_validation_plan import P95_DEFAULT_PATH

    assert str(P95_DEFAULT_PATH) == "out/research_fold_drop_spec_builder/latest.json"


def test_parse_args_default_p95_path() -> None:
    from scripts.run_research_fold_validation_plan import _parse_args

    args = _parse_args([])
    assert args.p95_path == "out/research_fold_drop_spec_builder/latest.json"


def test_parse_args_custom_p95_path(tmp_path: Path) -> None:
    from scripts.run_research_fold_validation_plan import _parse_args

    custom = str(tmp_path / "my_p95.json")
    args = _parse_args(["--p95-path", custom])
    assert args.p95_path == custom
