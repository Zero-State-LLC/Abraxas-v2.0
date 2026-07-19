from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.continuity_namespace_migration_plan import (
    PLAN_ID,
    SELECTED_POLICY,
    build_continuity_namespace_migration_plan,
)
from scripts.temporal import run_continuity_namespace_migration_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/continuity_namespace_migration_plan.v1.schema.json"
OUT_PATH = "out/continuity_namespace_migration_plan/latest.json"


def test_builds_expected_source_state_and_selected_policy() -> None:
    packet = build_continuity_namespace_migration_plan(repo_root=REPO_ROOT)

    assert packet["plan_id"] == PLAN_ID
    assert packet["artifact_type"] == "ContinuityNamespaceMigrationPlan.v1"
    assert packet["source_audit_id"] == "CONTINUITY_NAMESPACE_AUDIT_001"
    assert packet["selected_policy"] == SELECTED_POLICY
    assert packet["source_state"]["highest_observed_lane"] == "P102G"
    assert packet["source_state"]["lane_count"] == 58
    assert packet["source_state"]["governance"] == "FROZEN"
    assert packet["source_state"]["canon"] == "ADVISORY_ONLY"
    assert packet["source_state"]["downstream"] == "NOT_COMPUTABLE"
    assert packet["source_state"]["audit_observed_namespace_count"] == 10
    assert packet["source_state"]["audit_collision_count"] == 62
    assert packet["source_state"]["audit_orphaned_reference_count"] == 25


def test_composite_policy_and_remediation_order_are_defined() -> None:
    packet = build_continuity_namespace_migration_plan(repo_root=REPO_ROOT)

    assert "TEMPORAL_CONTINUITY.P102G" in packet["composite_id_recommendation_examples"]
    assert "RESEARCH_CANARY.P103" in packet["composite_id_recommendation_examples"]
    assert packet["canonical_global_id_policy"]["current_highest_global_id"] == "P102G"
    critical = packet["remediation_order"]["collision_remediation_order"][0]
    assert critical["target"] == ["P103", "P104", "P105", "P106", "P107"]
    assert all(row["ambiguity"] == "P103_TO_P107_RESEARCH_BRANCH_NAME_COLLISION" for row in packet["critical_ambiguities"])


def test_non_execution_boundary_and_blocked_actions() -> None:
    packet = build_continuity_namespace_migration_plan(repo_root=REPO_ROOT)

    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False
    assert packet["explicit_non_execution_boundary"]["valid_for_execution"] is False
    assert packet["explicit_non_execution_boundary"]["route_authority"] is False
    assert packet["explicit_non_execution_boundary"]["mutation_authority"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "CREATE_P102H" in packet["blocked_actions"]
    assert "CREATE_P103_TEMPORAL_OPERATOR_ROUTE" in packet["blocked_actions"]
    assert "MIGRATE_IDS_WITHOUT_SEPARATE_AUTHORIZATION" in packet["blocked_actions"]


def test_schema_validates_packet_and_hash_is_stable() -> None:
    packet = build_continuity_namespace_migration_plan(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_source_inputs_are_observed() -> None:
    packet = build_continuity_namespace_migration_plan(repo_root=REPO_ROOT)
    sources = {row["path"]: row for row in packet["packet_source_inputs"]}
    for rel_path in [
        "out/continuity_namespace_audit/latest.json",
        "docs/status/continuity-spine.json",
        "docs/status/badges.json",
        "README.md",
        "AGENTS.md",
        "PLANS.md",
        "core/generated_artifact_registry.py",
    ]:
        assert sources[rel_path]["observed"] is True
        assert sources[rel_path]["sha256"] != "NOT_COMPUTABLE"


def test_runner_writes_byte_stable_artifact(tmp_path: Path) -> None:
    target = tmp_path / "latest.json"
    first = run_continuity_namespace_migration_plan.run(
        repo_root=REPO_ROOT,
        output_path=target,
    )
    first_text = target.read_text(encoding="utf-8")
    second = run_continuity_namespace_migration_plan.run(
        repo_root=REPO_ROOT,
        output_path=target,
    )
    second_text = target.read_text(encoding="utf-8")

    assert first == second
    assert first_text == second_text


def test_repo_output_path_constant() -> None:
    assert str(run_continuity_namespace_migration_plan.OUT_PATH) == OUT_PATH
