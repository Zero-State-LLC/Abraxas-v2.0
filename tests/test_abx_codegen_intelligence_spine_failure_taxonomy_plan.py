from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_failure_taxonomy_plan import (
    build_abx_codegen_intelligence_spine_failure_taxonomy_plan,
    render_abx_codegen_intelligence_spine_failure_taxonomy_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_failure_taxonomy_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_failure_taxonomy_plan.v1.schema.json"
)


def test_codegen_failure_taxonomy_plan_ready() -> None:
    packet = build_abx_codegen_intelligence_spine_failure_taxonomy_plan(repo_root=REPO_ROOT)

    assert packet["failure_taxonomy_plan_status"] == "ABX_CODEGEN_FAILURE_TAXONOMY_PLAN_READY"
    assert packet["source_artifact_registry_integration_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_failure_taxonomy_categories_and_prefixes_are_preserved() -> None:
    packet = build_abx_codegen_intelligence_spine_failure_taxonomy_plan(repo_root=REPO_ROOT)

    assert [item["code_prefix"] for item in packet["top_level_categories"]] == [
        "VAL-",
        "RPL-",
        "GOV-",
        "META-",
        "INT-",
        "INTL-",
    ]
    assert all(
        item["taxonomy_status"] == "PLANNING_ONLY"
        for item in packet["top_level_categories"]
    )
    assert all(
        item["automated_response_authorized"] is False
        for item in packet["top_level_categories"]
    )


def test_codegen_failure_taxonomy_error_codes_and_recommendations_are_preserved() -> None:
    packet = build_abx_codegen_intelligence_spine_failure_taxonomy_plan(repo_root=REPO_ROOT)
    codes = {item["error_code"]: item for item in packet["detailed_error_codes"]}

    assert set(codes) >= {"VAL-001", "RPL-001", "GOV-004", "META-003", "INT-001", "INTL-002"}
    assert codes["GOV-004"]["recommended_responses"] == ["BLOCK_POLICY_VIOLATION"]
    assert codes["META-003"]["recommended_responses"] == [
        "HOLD_FOR_META_GATE",
        "BLOCK_POLICY_VIOLATION",
    ]
    assert all(item["response_authorized"] is False for item in codes.values())


def test_codegen_failure_taxonomy_promotion_blockers_are_reference_only() -> None:
    packet = build_abx_codegen_intelligence_spine_failure_taxonomy_plan(repo_root=REPO_ROOT)

    assert [item["promotion_blocker"] for item in packet["promotion_blocker_mapping"]] == [
        "replay_hash_divergence",
        "governance_compliance_failed",
        "self_modification_detected",
    ]
    assert all(
        item["receipt_mutation_authorized"] is False
        for item in packet["promotion_blocker_mapping"]
    )


def test_codegen_failure_taxonomy_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_failure_taxonomy_plan(repo_root=REPO_ROOT)

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_failure_taxonomy_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_failure_taxonomy_plan(repo_root=tmp_path)

    assert packet["failure_taxonomy_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_artifact_registry_integration_plan"]["source_ready"] is False
    assert all(
        item["taxonomy_status"] == "NOT_COMPUTABLE"
        for item in packet["top_level_categories"]
    )


def test_codegen_failure_taxonomy_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_failure_taxonomy_plan(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_failure_taxonomy_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_failure_taxonomy_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_failure_taxonomy_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_failure_taxonomy_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_failure_taxonomy_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_failure_taxonomy_plan(repo_root=REPO_ROOT)
    markdown = render_abx_codegen_intelligence_spine_failure_taxonomy_plan_markdown(packet)

    assert markdown[0] == "# ABX Codegen Intelligence Spine Failure Taxonomy Plan"
    assert any("Validation (VAL-): PLANNING_ONLY" in line for line in markdown)
    assert any("RPL-001 -> replay_hash_divergence" in line for line in markdown)
