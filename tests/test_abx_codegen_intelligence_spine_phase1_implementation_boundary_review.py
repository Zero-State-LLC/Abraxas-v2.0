from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_phase1_implementation_boundary_review import (
    build_abx_codegen_intelligence_spine_phase1_implementation_boundary_review,
    render_abx_codegen_intelligence_spine_phase1_implementation_boundary_review_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import (
    run_abx_codegen_intelligence_spine_phase1_implementation_boundary_review,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_phase1_implementation_boundary_review.v1.schema.json"
)


def test_codegen_phase1_boundary_review_is_held_for_operator() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_implementation_boundary_review(
        repo_root=REPO_ROOT
    )

    assert (
        packet["phase1_implementation_boundary_review_status"]
        == "ABX_CODEGEN_PHASE1_IMPLEMENTATION_BOUNDARY_REVIEW_HELD_FOR_OPERATOR"
    )
    assert packet["source_phase1_code_detail_plan"]["source_ready"] is True
    assert packet["source_module_surface_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_phase1_boundary_review_preserves_notion_intent_without_authority() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_implementation_boundary_review(
        repo_root=REPO_ROOT
    )

    intents = {item["notion_intent"]: item for item in packet["phase1_notion_intent"]}
    assert "implement_run_codegen_shadow_replay_skeleton" in intents
    assert "build_shadow_improvement_receipt" in intents
    assert all(
        item["implementation_authorized_by_repo"] is False
        for item in packet["phase1_notion_intent"]
    )


def test_codegen_phase1_boundary_review_blocks_phase1_actions() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_implementation_boundary_review(
        repo_root=REPO_ROOT
    )

    actions = {item["action"]: item for item in packet["blocked_phase1_actions"]}
    assert actions["create_core_codegen_shadow_replay_harness"]["authorized"] is False
    assert actions["execute_shadow_replay_or_simulation"]["authorized"] is False
    assert actions["route_promote_to_canary"]["authorized"] is False
    assert actions["write_back_to_notion_or_github"]["authorized"] is False


def test_codegen_phase1_boundary_review_only_allows_advisory_repo_actions() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_implementation_boundary_review(
        repo_root=REPO_ROOT
    )

    allowed = {item["action"]: item for item in packet["allowed_repo_actions"]}
    assert allowed["emit_boundary_review_artifact"]["authority"] == "advisory_only"
    assert (
        allowed["validate_existing_planning_artifacts"]["authority"]
        == "validation_only"
    )
    assert (
        allowed["update_repo_status_docs_from_observed_artifacts"]["authority"]
        == "documentation_sync_only"
    )


def test_codegen_phase1_boundary_review_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_implementation_boundary_review(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_phase1_boundary_review_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_implementation_boundary_review(
        repo_root=tmp_path
    )

    assert packet["phase1_implementation_boundary_review_status"] == "NOT_COMPUTABLE"
    assert packet["source_phase1_code_detail_plan"]["source_ready"] is False
    assert packet["source_module_surface_plan"]["source_ready"] is False
    assert all(
        item["action_status"] == "NOT_COMPUTABLE"
        for item in packet["blocked_phase1_actions"]
    )


def test_codegen_phase1_boundary_review_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_implementation_boundary_review(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_phase1_boundary_review_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_phase1_implementation_boundary_review_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_phase1_implementation_boundary_review.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_phase1_implementation_boundary_review.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_phase1_boundary_review_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_implementation_boundary_review(
        repo_root=REPO_ROOT
    )
    markdown = (
        render_abx_codegen_intelligence_spine_phase1_implementation_boundary_review_markdown(
            packet
        )
    )

    assert (
        markdown[0]
        == "# ABX Codegen Intelligence Spine Phase 1 Implementation Boundary Review"
    )
    assert any("create_core_codegen_shadow_replay_harness" in line for line in markdown)
    assert any("operator_authorization_missing" in line for line in markdown)
