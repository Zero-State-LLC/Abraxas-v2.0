from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.belief_graph_engine_advisory_receipt_implementation_authorization_record_plan import (
    DENIED_AUTHORITY,
    build_belief_graph_engine_advisory_receipt_implementation_authorization_record_plan,
    render_belief_graph_engine_advisory_receipt_implementation_authorization_record_plan_markdown,
)
from core.canonical.json import canonical_hash
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "belief_graph_engine_advisory_receipt_implementation_authorization_record_plan.v1.schema.json"
)
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_belief_graph_engine_advisory_receipt_implementation_authorization_record_plan.py",
    "local_belief_graph_engine_advisory_receipt_implementation_authorization_record_plan_runner",
)


def test_authorization_record_plan_is_plan_only() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_authorization_record_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["artifact_type"]
        == "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecordPlan.v1"
    )
    assert (
        packet["record_plan_status"]
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN_READY"
    )
    assert packet["source_authorization_gate"]["source_ready"] is True
    assert packet["authorization_record_plan_only"] is True
    assert packet["authorization_record_required"] is True
    assert packet["authorization_record_creation_allowed"] is False
    assert packet["authorization_record_created"] is False
    assert packet["operator_approved"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_authorization_record_plan_denies_record_creation_and_receipt_authority() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_authorization_record_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["recommended_next_lane"]
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_PLAN"
    )
    for authority in DENIED_AUTHORITY:
        assert authority in packet["denied_authority"]
    assert all(
        requirement["creation_allowed"] is False
        for requirement in packet["record_plan_requirements"]
    )
    planned_record = packet["planned_authorization_record"]
    assert planned_record["operator_approval_required"] is True
    assert planned_record["operator_approved"] is False
    assert planned_record["authorization_granted"] is False
    assert planned_record["record_creation_allowed"] is False
    assert planned_record["record_created"] is False
    assert planned_record["execution_authority"] is False


def test_authorization_record_plan_schema_and_hash_are_stable() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_authorization_record_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_authorization_record_plan_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "belief_graph_engine_advisory_receipt_implementation_authorization_record_plan_001.latest.json"
    )
    out_md = (
        tmp_path
        / "out/audit/"
        "belief_graph_engine_advisory_receipt_implementation_authorization_record_plan_001.latest.md"
    )

    first = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_authorization_record_plan_markdown() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_authorization_record_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_belief_graph_engine_advisory_receipt_implementation_authorization_record_plan_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# Belief Graph Engine Advisory Receipt Implementation Authorization Record Plan"
    )
    assert any("authorization_record_creation_allowed: False" in line for line in markdown)
    assert any("AUTHORIZATION_RECORD_CREATION" in line for line in markdown)


def test_authorization_record_plan_registry_entries() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_plan_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_plan_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
