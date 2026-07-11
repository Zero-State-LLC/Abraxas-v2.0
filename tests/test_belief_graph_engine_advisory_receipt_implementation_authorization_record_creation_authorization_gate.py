from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate import (
    DENIED_AUTHORITY,
    build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate,
    render_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_markdown,
)
from core.canonical.json import canonical_hash
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate.v1.schema.json"
)
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate.py",
    "local_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_runner",
)


def test_record_creation_authorization_gate_is_held_for_operator() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate(
        repo_root=REPO_ROOT
    )

    assert (
        packet["artifact_type"]
        == "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecordCreationAuthorizationGate.v1"
    )
    assert (
        packet["gate_status"]
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
    )
    assert packet["source_authorization_record_creation_plan"]["source_ready"] is True
    assert packet["authorization_scope"] == "RECORD_CREATION_ELIGIBILITY_REVIEW_ONLY"
    assert packet["record_creation_authorization_eligible"] is True
    assert packet["requires_operator_decision"] is True
    assert packet["selected_operator_decision"] == "HOLD"
    assert packet["authorization_record_creation_allowed"] is False
    assert packet["authorization_record_created"] is False
    assert packet["authorization_token_created"] is False
    assert packet["operator_approved"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_record_creation_authorization_gate_denies_creation_and_receipt_authority() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate(
        repo_root=REPO_ROOT
    )

    assert (
        packet["recommended_next_lane"]
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_RECORD_PLAN"
    )
    for authority in DENIED_AUTHORITY:
        assert authority in packet["denied_authority"]
    assert all(
        check["grants_authority"] is False
        for check in packet["authorization_prerequisites"]
    )
    assert any(
        check["check_status"] == "HELD_FOR_OPERATOR"
        for check in packet["authorization_prerequisites"]
    )
    assert (
        packet["planned_record_artifact_type"]
        == "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecord.v1"
    )


def test_record_creation_authorization_gate_schema_and_hash_are_stable() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_record_creation_authorization_gate_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_001.latest.json"
    )
    out_md = (
        tmp_path
        / "out/audit/"
        "belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_001.latest.md"
    )

    first = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_record_creation_authorization_gate_markdown() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate(
        repo_root=REPO_ROOT
    )
    markdown = render_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# Belief Graph Engine Advisory Receipt Implementation Authorization Record Creation Authorization Gate"
    )
    assert any("selected_operator_decision: HOLD" in line for line in markdown)
    assert any("AUTHORIZATION_RECORD_CREATION" in line for line in markdown)


def test_record_creation_authorization_gate_registry_entries() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
