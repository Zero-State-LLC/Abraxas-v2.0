from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.continuity_namespace_audit import (
    AUDIT_ID,
    OUT_PATH,
    build_continuity_namespace_audit,
)
from scripts import run_continuity_namespace_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/continuity_namespace_audit.v1.schema.json"


def _collision_numbers(packet: dict) -> set[str]:
    return {collision["p_number"] for collision in packet["collisions"]}


def test_builds_expected_p102g_source_state_and_authority_locks() -> None:
    packet = build_continuity_namespace_audit(repo_root=REPO_ROOT)

    assert packet["audit_id"] == AUDIT_ID
    assert packet["artifact_type"] == "ContinuityNamespaceAudit.v1"
    assert packet["source_state"]["highest_observed_lane"] == "P102G"
    assert packet["source_state"]["lane_count"] == 58
    assert packet["source_state"]["governance"] == "FROZEN"
    assert packet["source_state"]["canon"] == "ADVISORY_ONLY"
    assert packet["source_state"]["downstream"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["authorization_granted"] is False
    assert packet["authorization_record_created"] is False
    assert packet["token_minting_allowed"] is False


def test_discovers_namespaces_and_p103_research_temporal_collision() -> None:
    packet = build_continuity_namespace_audit(repo_root=REPO_ROOT)
    namespace_ids = {namespace["namespace_id"] for namespace in packet["observed_namespaces"]}

    assert "TEMPORAL_CONTINUITY" in namespace_ids
    assert "RESEARCH_CANARY" in namespace_ids
    assert "P103" in _collision_numbers(packet)
    p103 = next(collision for collision in packet["collisions"] if collision["p_number"] == "P103")
    assert "TEMPORAL_CONTINUITY" in p103["namespaces"]
    assert "RESEARCH_CANARY" in p103["namespaces"]
    assert packet["global_p_numbering_safe"] is False
    assert (
        packet["namespace_policy_recommendation"]["recommended_policy"]
        == "D_HYBRID_CANONICAL_GLOBAL_IDS_WITH_BRANCH_LOCAL_ALIASES"
    )


def test_inventory_records_p102g_and_fail_closed_orphan_handling() -> None:
    packet = build_continuity_namespace_audit(repo_root=REPO_ROOT)
    lane_ids = {entry["lane_id"] for entry in packet["lane_reference_inventory"]}
    assert "P102G" in lane_ids
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert all(
        reference["resolution_status"] != "MISSING_REPO_EVIDENCE"
        or reference in packet["orphaned_references"]
        for reference in packet["recommended_next_lane_references"]
    )


def test_schema_validates_packet_and_hash_is_stable() -> None:
    packet = build_continuity_namespace_audit(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runner_writes_byte_stable_artifact(tmp_path: Path) -> None:
    first = run_continuity_namespace_audit.run(
        repo_root=REPO_ROOT,
        output_path=tmp_path / "latest.json",
    )
    first_text = (tmp_path / "latest.json").read_text(encoding="utf-8")
    second = run_continuity_namespace_audit.run(
        repo_root=REPO_ROOT,
        output_path=tmp_path / "latest.json",
    )
    second_text = (tmp_path / "latest.json").read_text(encoding="utf-8")

    assert first == second
    assert first_text == second_text


def test_repo_artifact_path_constant_is_expected() -> None:
    assert OUT_PATH == "out/continuity_namespace_audit/latest.json"
