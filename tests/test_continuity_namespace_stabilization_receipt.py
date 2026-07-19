from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.continuity_namespace_stabilization_receipt import (
    AUDIT_PATH,
    COMPOSITE_ID_FORMAT,
    MIGRATION_PLAN_PATH,
    RECEIPT_ID,
    SELECTED_POLICY,
    build_continuity_namespace_stabilization_receipt,
)
from scripts.temporal import run_continuity_namespace_stabilization_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/continuity_namespace_stabilization_receipt.v1.schema.json"
OUT_PATH = "out/continuity_namespace_stabilization_receipt/latest.json"


def test_receipt_preserves_source_state_and_policy() -> None:
    packet = build_continuity_namespace_stabilization_receipt(repo_root=REPO_ROOT)

    assert packet["receipt_id"] == RECEIPT_ID
    assert packet["artifact_type"] == "ContinuityNamespaceStabilizationReceipt.v1"
    assert packet["consumed_audit_artifact_path"] == AUDIT_PATH
    assert packet["consumed_migration_plan_artifact_path"] == MIGRATION_PLAN_PATH
    assert packet["selected_policy"] == SELECTED_POLICY
    assert packet["composite_id_format"] == COMPOSITE_ID_FORMAT
    assert packet["source_state"] == {
        "canon": "ADVISORY_ONLY",
        "downstream": "NOT_COMPUTABLE",
        "governance": "FROZEN",
        "highest_observed_lane": "P102G",
        "lane_count": 58,
    }


def test_consistency_registry_and_stability_statuses_are_sealed() -> None:
    packet = build_continuity_namespace_stabilization_receipt(repo_root=REPO_ROOT)

    assert packet["audit_plan_consistency_status"] == "CONSISTENT"
    assert packet["registry_binding_status"] == "BOUND"
    assert packet["byte_stability_status"] == "BYTE_STABLE"
    assert packet["non_execution_boundary_status"] == "NON_EXECUTION_BOUNDARY_CONFIRMED"
    assert packet["blocked_action_status"] == "BLOCKED_ACTIONS_REMAIN_DENIED"
    assert packet["stabilization_window_status"] == "STABILIZATION_HOLD_READY"
    assert packet["composite_id_mutation_status"] == "NO_COMPOSITE_ID_MUTATION_DETECTED"


def test_not_computable_handoff_and_authority_locks_remain_false() -> None:
    packet = build_continuity_namespace_stabilization_receipt(repo_root=REPO_ROOT)

    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False
    assert packet["authorization_granted"] is False
    assert packet["authorization_record_created"] is False
    assert packet["token_minting_allowed"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    for blocked in [
        "CREATE_P102H",
        "CREATE_P103",
        "CREATE_DOWNSTREAM_CONTINUITY_LANES",
        "ADD_COMPOSITE_IDS_TO_EXISTING_SURFACES",
    ]:
        assert blocked in packet["blocked_actions"]["blocked_actions"]


def test_schema_validates_packet_and_hash_is_stable() -> None:
    packet = build_continuity_namespace_stabilization_receipt(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_source_inputs_are_observed() -> None:
    packet = build_continuity_namespace_stabilization_receipt(repo_root=REPO_ROOT)
    sources = {row["path"]: row for row in packet["packet_source_inputs"]}
    for rel_path in [
        AUDIT_PATH,
        MIGRATION_PLAN_PATH,
        "docs/status/continuity-spine.json",
        "docs/status/badges.json",
        "core/generated_artifact_registry.py",
    ]:
        assert sources[rel_path]["observed"] is True
        assert sources[rel_path]["sha256"] != "NOT_COMPUTABLE"


def test_runner_writes_byte_stable_artifact(tmp_path: Path) -> None:
    target = tmp_path / "latest.json"
    first = run_continuity_namespace_stabilization_receipt.run(
        repo_root=REPO_ROOT,
        output_path=target,
    )
    first_text = target.read_text(encoding="utf-8")
    second = run_continuity_namespace_stabilization_receipt.run(
        repo_root=REPO_ROOT,
        output_path=target,
    )
    second_text = target.read_text(encoding="utf-8")

    assert first == second
    assert first_text == second_text


def test_repo_output_path_constant() -> None:
    assert str(run_continuity_namespace_stabilization_receipt.OUT_PATH) == OUT_PATH
