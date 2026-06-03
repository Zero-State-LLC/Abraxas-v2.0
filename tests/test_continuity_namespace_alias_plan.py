from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.continuity_namespace_alias_plan import (
    AUDIT_PATH,
    COMPOSITE_ID_FORMAT,
    MIGRATION_PLAN_PATH,
    PLAN_ID,
    READINESS_REVIEW_PATH,
    SELECTED_POLICY,
    STABILIZATION_RECEIPT_PATH,
    build_continuity_namespace_alias_plan,
)
from scripts import run_continuity_namespace_alias_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/continuity_namespace_alias_plan.v1.schema.json"
OUT_PATH = "out/continuity_namespace_alias_plan/latest.json"


def test_alias_plan_preserves_readiness_gate_and_source_state() -> None:
    packet = build_continuity_namespace_alias_plan(repo_root=REPO_ROOT)

    assert packet["plan_id"] == PLAN_ID
    assert packet["artifact_type"] == "ContinuityNamespaceAliasPlan.v1"
    assert packet["plan_status"] == "ADDITIVE_ALIAS_PLAN_EMITTED"
    assert packet["consumed_readiness_review_artifact_path"] == READINESS_REVIEW_PATH
    assert packet["consumed_stabilization_receipt_artifact_path"] == STABILIZATION_RECEIPT_PATH
    assert packet["consumed_migration_plan_artifact_path"] == MIGRATION_PLAN_PATH
    assert packet["consumed_audit_artifact_path"] == AUDIT_PATH
    assert packet["selected_policy"] == SELECTED_POLICY
    assert packet["composite_id_format"] == COMPOSITE_ID_FORMAT
    assert packet["source_state"] == {
        "canon": "ADVISORY_ONLY",
        "downstream": "NOT_COMPUTABLE",
        "governance": "FROZEN",
        "highest_observed_lane": "P102G",
        "lane_count": 58,
    }


def test_alias_manifest_is_planned_only_and_additive() -> None:
    packet = build_continuity_namespace_alias_plan(repo_root=REPO_ROOT)

    assert packet["alias_manifest_shape"]["planned_only"] is True
    assert packet["alias_manifest_shape"]["artifact_path"] == "out/continuity_namespace_alias_manifest/latest.json"
    assert packet["no_path_rename_rule"] == "FORBIDDEN"
    assert packet["legacy_id_rewrite_rule"] == "FORBIDDEN"
    assert packet["additive_metadata_strategy"]["metadata_posture"] == (
        "ADDITIVE_ONLY_NO_EXISTING_SURFACE_MUTATION_IN_THIS_PLAN"
    )
    assert packet["compatibility_with_existing_generated_artifacts"]["legacy_artifact_paths_preserved"] is True
    assert "alias_manifest_status" in packet["status_surface_additive_fields"]


def test_lookup_precedence_and_collision_handling_fail_closed() -> None:
    packet = build_continuity_namespace_alias_plan(repo_root=REPO_ROOT)

    assert packet["alias_lookup_precedence"][-1] == "fail_closed_on_missing_or_ambiguous_alias"
    assert packet["alias_collision_handling"]["collision_policy"] == "FAIL_CLOSED_NOT_COMPUTABLE"
    assert packet["alias_collision_handling"]["tie_breaking"] == (
        "NO_AUTOMATED_TIE_BREAKING_OPERATOR_REVIEW_REQUIRED"
    )
    assert "alias_collision_validation" in packet["validation_gates"]
    assert packet["stabilization_receipt_requirement_before_implementation"]["required"] is True
    assert packet["stabilization_receipt_requirement_before_implementation"][
        "valid_for_implementation_until_receipt"
    ] is False


def test_authority_locks_and_next_lane_remain_denied() -> None:
    packet = build_continuity_namespace_alias_plan(repo_root=REPO_ROOT)

    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False
    assert packet["authorization_granted"] is False
    assert packet["authorization_record_created"] is False
    assert packet["token_minting_allowed"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "CREATE_P102H" in packet["unsafe_actions"]
    assert "CREATE_P103" in packet["unsafe_actions"]
    assert "IMPLEMENT_ALIAS_MANIFEST_NOW" in packet["unsafe_actions"]


def test_schema_validates_packet_and_hash_is_stable() -> None:
    packet = build_continuity_namespace_alias_plan(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_source_inputs_are_observed_and_registry_bound() -> None:
    packet = build_continuity_namespace_alias_plan(repo_root=REPO_ROOT)
    sources = {row["path"]: row for row in packet["packet_source_inputs"]}
    for rel_path in [
        READINESS_REVIEW_PATH,
        STABILIZATION_RECEIPT_PATH,
        MIGRATION_PLAN_PATH,
        AUDIT_PATH,
        "docs/status/continuity-spine.json",
        "docs/status/badges.json",
        "README.md",
        "AGENTS.md",
        "PLANS.md",
        "core/generated_artifact_registry.py",
    ]:
        assert sources[rel_path]["observed"] is True
        assert sources[rel_path]["malformed"] is False
        assert sources[rel_path]["sha256"] != "NOT_COMPUTABLE"
    assert packet["registry_binding"]["status"] == "BOUND"


def test_runner_writes_byte_stable_artifact(tmp_path: Path) -> None:
    target = tmp_path / "latest.json"
    first = run_continuity_namespace_alias_plan.run(repo_root=REPO_ROOT, output_path=target)
    first_text = target.read_text(encoding="utf-8")
    second = run_continuity_namespace_alias_plan.run(repo_root=REPO_ROOT, output_path=target)
    second_text = target.read_text(encoding="utf-8")

    assert first == second
    assert first_text == second_text


def test_repo_output_path_constant() -> None:
    assert str(run_continuity_namespace_alias_plan.OUT_PATH) == OUT_PATH
