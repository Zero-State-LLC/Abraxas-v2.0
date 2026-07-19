from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.continuity_namespace_readiness_review import (
    AUDIT_PATH,
    COMPOSITE_ID_FORMAT,
    MIGRATION_PLAN_PATH,
    REVIEW_ID,
    SELECTED_POLICY,
    STABILIZATION_RECEIPT_PATH,
    build_continuity_namespace_readiness_review,
)
from scripts.temporal import run_continuity_namespace_readiness_review

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/continuity_namespace_readiness_review.v1.schema.json"
OUT_PATH = "out/continuity_namespace_readiness_review/latest.json"


def test_review_preserves_source_state_policy_and_inputs() -> None:
    packet = build_continuity_namespace_readiness_review(repo_root=REPO_ROOT)

    assert packet["review_id"] == REVIEW_ID
    assert packet["artifact_type"] == "ContinuityNamespaceReadinessReview.v1"
    assert packet["consumed_audit_artifact_path"] == AUDIT_PATH
    assert packet["consumed_migration_plan_artifact_path"] == MIGRATION_PLAN_PATH
    assert packet["consumed_stabilization_receipt_artifact_path"] == STABILIZATION_RECEIPT_PATH
    assert packet["selected_policy"] == SELECTED_POLICY
    assert packet["composite_id_format"] == COMPOSITE_ID_FORMAT
    assert packet["source_state"] == {
        "canon": "ADVISORY_ONLY",
        "downstream": "NOT_COMPUTABLE",
        "governance": "FROZEN",
        "highest_observed_lane": "P102G",
        "lane_count": 58,
    }


def test_readiness_status_is_ready_only_for_future_plan() -> None:
    packet = build_continuity_namespace_readiness_review(repo_root=REPO_ROOT)

    assert packet["readiness_status"] == "READY_FOR_ADDITIVE_ALIAS_PLAN"
    assert packet["readiness_blockers"] == []
    assert (
        packet["safe_next_surface_recommendation"]
        == "CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY"
    )
    assert packet["recommended_next_action"] == "DRAFT_ADVISORY_ONLY_ADDITIVE_ALIAS_PLAN"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_unresolved_summaries_are_review_inputs_not_execution_grants() -> None:
    packet = build_continuity_namespace_readiness_review(repo_root=REPO_ROOT)

    assert packet["unresolved_collision_summary"]["total_collision_count"] == 62
    assert packet["unresolved_collision_summary"]["critical_p_numbers"] == [
        "P103",
        "P104",
        "P105",
        "P106",
        "P107",
    ]
    assert packet["unresolved_orphan_summary"]["total_orphaned_recommended_next_lane_references"] == 25
    assert "CREATE_ALIAS_MANIFESTS_NOW" in packet["unsafe_actions"]
    assert "ADD_COMPOSITE_IDS_INTO_EXISTING_SURFACES" in packet["unsafe_actions"]


def test_authority_locks_and_activation_evidence_are_fail_closed() -> None:
    packet = build_continuity_namespace_readiness_review(repo_root=REPO_ROOT)

    assert packet["valid_for_execution"] is False
    assert packet["authorization_granted"] is False
    assert packet["authorization_record_created"] is False
    assert packet["token_minting_allowed"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "explicit_future_operator_authorization_record" in packet["required_evidence_for_activation"]
    assert "separate_governance_design_for_alias_implementation" in packet["required_evidence_for_activation"]


def test_schema_validates_packet_and_hash_is_stable() -> None:
    packet = build_continuity_namespace_readiness_review(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_source_inputs_are_observed() -> None:
    packet = build_continuity_namespace_readiness_review(repo_root=REPO_ROOT)
    sources = {row["path"]: row for row in packet["packet_source_inputs"]}
    for rel_path in [
        AUDIT_PATH,
        MIGRATION_PLAN_PATH,
        STABILIZATION_RECEIPT_PATH,
        "docs/status/continuity-spine.json",
        "docs/status/badges.json",
        "core/generated_artifact_registry.py",
    ]:
        assert sources[rel_path]["observed"] is True
        assert sources[rel_path]["malformed"] is False
        assert sources[rel_path]["sha256"] != "NOT_COMPUTABLE"


def test_runner_writes_byte_stable_artifact(tmp_path: Path) -> None:
    target = tmp_path / "latest.json"
    first = run_continuity_namespace_readiness_review.run(
        repo_root=REPO_ROOT,
        output_path=target,
    )
    first_text = target.read_text(encoding="utf-8")
    second = run_continuity_namespace_readiness_review.run(
        repo_root=REPO_ROOT,
        output_path=target,
    )
    second_text = target.read_text(encoding="utf-8")

    assert first == second
    assert first_text == second_text


def test_repo_output_path_constant() -> None:
    assert str(run_continuity_namespace_readiness_review.OUT_PATH) == OUT_PATH
