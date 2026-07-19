from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_testing_validation_strategy_plan import (
    build_abx_codegen_intelligence_spine_testing_validation_strategy_plan,
    render_abx_codegen_intelligence_spine_testing_validation_strategy_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_intelligence_spine_testing_validation_strategy_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_testing_validation_strategy_plan.v1.schema.json"
)


def test_codegen_testing_validation_strategy_plan_ready() -> None:
    packet = build_abx_codegen_intelligence_spine_testing_validation_strategy_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["testing_validation_strategy_plan_status"]
        == "ABX_CODEGEN_TESTING_VALIDATION_STRATEGY_PLAN_READY"
    )
    assert packet["source_failure_taxonomy_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_testing_validation_layers_are_preserved_and_not_authorized() -> None:
    packet = build_abx_codegen_intelligence_spine_testing_validation_strategy_plan(
        repo_root=REPO_ROOT
    )

    assert [item["layer"] for item in packet["testing_layers"]] == [
        "Unit Tests",
        "Integration Tests",
        "Property-Based / Determinism Tests",
        "Adversarial / Negative Tests",
        "Governance Compliance Tests",
    ]
    assert all(item["layer_status"] == "PLANNING_ONLY" for item in packet["testing_layers"])
    assert all(
        item["test_implementation_authorized"] is False for item in packet["testing_layers"]
    )
    assert all(item["harness_execution_authorized"] is False for item in packet["testing_layers"])


def test_codegen_testing_validation_structure_and_fixtures_are_reference_only() -> None:
    packet = build_abx_codegen_intelligence_spine_testing_validation_strategy_plan(
        repo_root=REPO_ROOT
    )

    assert packet["recommended_test_structure"]["root"] == "tests/codegen/"
    assert packet["recommended_test_structure"]["directory_creation_authorized"] is False
    assert packet["recommended_test_structure"]["test_file_creation_authorized"] is False
    assert packet["golden_fixture_strategy"]["normal_proposal_pairs_required"] is True
    assert packet["golden_fixture_strategy"]["self_improvement_proposal_pairs_required"] is True
    assert packet["golden_fixture_strategy"]["fixture_generation_authorized"] is False


def test_codegen_testing_validation_continuous_validation_is_non_executable() -> None:
    packet = build_abx_codegen_intelligence_spine_testing_validation_strategy_plan(
        repo_root=REPO_ROOT
    )
    continuous = packet["continuous_validation"]

    assert continuous["all_tests_deterministic"] is True
    assert continuous["all_tests_replay_safe"] is True
    assert continuous["property_based_testing_recommended"] is True
    assert continuous["hypothesis_dependency_authorized"] is False
    assert continuous["harness_test_execution_authorized"] is False
    assert continuous["meta_gate_test_execution_authorized"] is False


def test_codegen_testing_validation_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_testing_validation_strategy_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_testing_validation_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_testing_validation_strategy_plan(
        repo_root=tmp_path
    )

    assert packet["testing_validation_strategy_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_failure_taxonomy_plan"]["source_ready"] is False
    assert all(item["layer_status"] == "NOT_COMPUTABLE" for item in packet["testing_layers"])


def test_codegen_testing_validation_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_testing_validation_strategy_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_testing_validation_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_testing_validation_strategy_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_testing_validation_strategy_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_testing_validation_strategy_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_testing_validation_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_testing_validation_strategy_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_testing_validation_strategy_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Testing Validation Strategy Plan"
    assert any("Unit Tests: PLANNING_ONLY" in line for line in markdown)
    assert any("harness_test_execution_authorized: False" in line for line in markdown)
