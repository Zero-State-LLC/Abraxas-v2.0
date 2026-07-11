from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan import (
    DENIED_AUTHORITY,
    build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan,
    render_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_markdown,
)
from core.canonical.json import canonical_hash
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan.v1.schema.json"
)
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan.py",
    "local_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_runner",
)


def test_authorization_record_creation_plan_is_plan_only() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["artifact_type"]
        == "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecordCreationPlan.v1"
    )
    assert (
        packet["creation_plan_status"]
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY"
    )
    assert packet["source_authorization_record_plan"]["source_ready"] is True
    assert packet["authorization_record_creation_plan_only"] is True
    assert packet["authorization_record_creation_required"] is True
    assert packet["authorization_record_creation_allowed"] is False
    assert packet["authorization_record_created"] is False
    assert packet["authorization_token_created"] is False
    assert packet["operator_approved"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_authorization_record_creation_plan_blocks_creation_and_execution() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["recommended_next_lane"]
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE"
    )
    for authority in DENIED_AUTHORITY:
        assert authority in packet["denied_authority"]
    assert packet["planned_record_output"]["creation_allowed"] is False
    assert packet["planned_record_output"]["creation_authority"] is False
    assert all(item["authorization_record_creation_allowed"] is False for item in packet["creation_plan_items"])
    assert all(item["authorization_record_created"] is False for item in packet["creation_plan_items"])
    assert all(item["authorization_granted"] is False for item in packet["creation_plan_items"])
    assert all(item["execution_allowed"] is False for item in packet["creation_plan_items"])
    assert any(check["check_status"] == "HELD_FOR_OPERATOR" for check in packet["pre_creation_checks"])


def test_authorization_record_creation_plan_schema_and_hash_are_stable() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_authorization_record_creation_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_001.latest.json"
    )
    out_md = (
        tmp_path
        / "out/audit/"
        "belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_001.latest.md"
    )

    first = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_authorization_record_creation_plan_markdown() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# Belief Graph Engine Advisory Receipt Implementation Authorization Record Creation Plan"
    )
    assert any("authorization_record_creation_allowed: False" in line for line in markdown)
    assert any("AUTHORIZATION_TOKEN_CREATION" in line for line in markdown)


def test_authorization_record_creation_plan_registry_entries() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
