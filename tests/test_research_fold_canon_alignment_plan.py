from __future__ import annotations

import json
from pathlib import Path

from core.research_fold_canon_alignment_plan import (
    build_research_fold_canon_alignment_plan,
    write_research_fold_canon_alignment_plan,
)
from scripts import run_research_fold_canon_alignment_plan


_PASS_SURFACES = {
    "canon_drop_006_research_folds": {
        "fold_ids": [
            "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER",
            "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
            "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER",
        ]
    },
    "canon_drop_007_research_folds": {
        "fold_ids": [
            "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
            "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER",
            "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER",
        ]
    },
}


def test_deterministic_repeated_output() -> None:
    first = build_research_fold_canon_alignment_plan(supplied_upstream_surfaces=_PASS_SURFACES)
    second = build_research_fold_canon_alignment_plan(supplied_upstream_surfaces=_PASS_SURFACES)
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_drop_006_and_drop_007_targets_included() -> None:
    packet = build_research_fold_canon_alignment_plan(supplied_upstream_surfaces=_PASS_SURFACES)
    observed_drop_ids = {target["drop_id"] for target in packet["research_fold_targets"]}
    assert observed_drop_ids == {"DROP006", "DROP007"}


def test_missing_upstream_surfaces_produce_not_computable() -> None:
    packet = build_research_fold_canon_alignment_plan(
        supplied_upstream_surfaces={"canon_drop_006_research_folds": {"fold_ids": []}}
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["canon_alignment_status"] == "NOT_ALIGNED"
    assert (
        "missing_required_upstream_surface:canon_drop_007_research_folds"
        in packet["not_computable_reasons"]
    )


def test_authority_locks_always_false() -> None:
    packet = build_research_fold_canon_alignment_plan(supplied_upstream_surfaces=_PASS_SURFACES)
    expected_keys = {
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
    assert set(packet["authority_locks"].keys()) == expected_keys
    assert all(value is False for value in packet["authority_locks"].values())


def test_candidate_ordering_stable() -> None:
    packet = build_research_fold_canon_alignment_plan(supplied_upstream_surfaces=_PASS_SURFACES)
    observed = [target["candidate_id"] for target in packet["research_fold_targets"]]
    assert observed == [
        "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER",
        "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
        "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER",
        "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER",
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER",
    ]


def test_recommended_next_lane_p95_only_on_pass_aligned() -> None:
    pass_packet = build_research_fold_canon_alignment_plan(
        supplied_upstream_surfaces=_PASS_SURFACES
    )
    assert pass_packet["status"] == "PASS"
    assert pass_packet["canon_alignment_status"] == "ALIGNED"
    assert pass_packet["recommended_next_lane"] == "P95_RESEARCH_FOLD_DROP_SPEC_BUILDER"

    blocked_packet = build_research_fold_canon_alignment_plan(
        supplied_upstream_surfaces={"canon_drop_007_research_folds": {"fold_ids": []}}
    )
    assert blocked_packet["status"] == "NOT_COMPUTABLE"
    assert blocked_packet["recommended_next_lane"] != "P95_RESEARCH_FOLD_DROP_SPEC_BUILDER"


def test_schema_locks_authority_fields_false() -> None:
    schema = json.loads(
        Path("contracts/canon/research_fold_canon_alignment_plan.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    for field in (
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
    ):
        assert schema["properties"]["authority_locks"]["properties"][field]["const"] is False


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_fold_canon_alignment_plan" / "latest.json"
    first = run_research_fold_canon_alignment_plan.run(
        supplied_upstream_surfaces=_PASS_SURFACES,
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")

    second = run_research_fold_canon_alignment_plan.run(
        supplied_upstream_surfaces=_PASS_SURFACES,
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")

    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_writer_final_newline(tmp_path: Path) -> None:
    packet = build_research_fold_canon_alignment_plan(supplied_upstream_surfaces=_PASS_SURFACES)
    out_path = tmp_path / "research_fold_canon_alignment_plan_test.json"
    write_research_fold_canon_alignment_plan(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
