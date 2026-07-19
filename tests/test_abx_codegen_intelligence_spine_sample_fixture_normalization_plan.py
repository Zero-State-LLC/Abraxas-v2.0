from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_sample_fixture_normalization_plan import (
    build_abx_codegen_intelligence_spine_sample_fixture_normalization_plan,
    render_abx_codegen_intelligence_spine_sample_fixture_normalization_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_intelligence_spine_sample_fixture_normalization_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_sample_fixture_normalization_plan.v1.schema.json"
)


def test_codegen_sample_fixture_normalization_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_fixture_normalization_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["sample_fixture_normalization_plan_status"]
        == "ABX_CODEGEN_SAMPLE_FIXTURE_NORMALIZATION_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_fixture_validation_harness_plan"]["source_ready"] is True
    assert packet["source_sample_meta_gate_chain_validation_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_sample_fixture_normalization_classifies_notion_samples() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_fixture_normalization_plan(
        repo_root=REPO_ROOT
    )

    classes = {item["sample_class"]: item for item in packet["notion_sample_classes"]}
    assert classes["GapDiagnosisPacket.v1 self-diagnosis"]["fixture_use"] == (
        "reference_only_requires_normalization"
    )
    assert classes["Adversarial negative cases A-D"]["fixture_use"] == (
        "negative_fixture_requirements_only"
    )
    assert classes["v1.1 HOLD/BLOCK receipt examples E-F"]["fixture_use"] == (
        "governance_recommendation_requirements_only"
    )


def test_codegen_sample_fixture_normalization_requires_cleanup_before_fixture_use() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_fixture_normalization_plan(
        repo_root=REPO_ROOT
    )

    requirements = {item["requirement"]: item for item in packet["normalization_requirements"]}
    assert (
        requirements["replace_illustrative_or_notional_hashes_with_real_fixture_hashes"][
            "normalization_execution_authorized"
        ]
        is False
    )
    assert (
        requirements["remove_json_comments_and_ellipsis_before_schema_validation"][
            "requirement_status"
        ]
        == "SAMPLE_FIXTURE_NORMALIZATION_DEFINED_HELD_FOR_OPERATOR"
    )
    assert (
        requirements["never_treat_samples_as_observed_runtime_receipts"][
            "normalization_execution_authorized"
        ]
        is False
    )


def test_codegen_sample_fixture_normalization_negative_case_expectations() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_fixture_normalization_plan(
        repo_root=REPO_ROOT
    )

    cases = {item["case_id"]: item for item in packet["negative_case_expectations"]}
    assert "missing_evidence_hash" in cases["A"]["expected_rejection_reasons"]
    assert "invalid_canon_promotion_path" in cases["B"]["expected_rejection_reasons"]
    assert (
        "governance_violation_with_promote_recommendation"
        in cases["C"]["expected_rejection_reasons"]
    )
    assert "core_policy_mutation_attempt" in cases["D"]["expected_rejection_reasons"]
    assert cases["E"]["required_semantics"] == [
        "HOLD_FOR_META_GATE",
        "promotion_blockers_present",
    ]
    assert cases["F"]["required_semantics"] == [
        "BLOCK_REPLAY_FAILURE",
        "promotion_blockers_present",
    ]


def test_codegen_sample_fixture_normalization_repo_fixture_alignment() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_fixture_normalization_plan(
        repo_root=REPO_ROOT
    )

    alignment = packet["repo_fixture_alignment"]
    assert alignment["fixture_count"] == 12
    assert alignment["valid_fixture_count"] == 7
    assert alignment["negative_fixture_count"] == 5
    assert alignment["repo_fixtures_are_canonical_test_material"] is True
    assert alignment["notion_samples_are_canonical_test_material"] is False
    assert alignment["fixture_write_authorized"] is False


def test_codegen_sample_fixture_normalization_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_fixture_normalization_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "fixture_file_mutation" in packet["blocked_actions"]
    assert "schema_validation_execution" in packet["blocked_actions"]


def test_codegen_sample_fixture_normalization_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_sample_fixture_normalization_plan(
        repo_root=tmp_path
    )

    assert packet["sample_fixture_normalization_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_fixture_validation_harness_plan"]["source_ready"] is False
    assert packet["source_sample_meta_gate_chain_validation_plan"]["source_ready"] is False
    assert all(
        item["sample_status"] == "NOT_COMPUTABLE"
        for item in packet["notion_sample_classes"]
    )


def test_codegen_sample_fixture_normalization_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_fixture_normalization_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_sample_fixture_normalization_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_sample_fixture_normalization_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_sample_fixture_normalization_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_sample_fixture_normalization_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_sample_fixture_normalization_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_fixture_normalization_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_sample_fixture_normalization_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Sample Fixture Normalization Plan"
    assert any("Adversarial negative cases A-D" in line for line in markdown)
    assert any("fixture_file_mutation" in line for line in markdown)
