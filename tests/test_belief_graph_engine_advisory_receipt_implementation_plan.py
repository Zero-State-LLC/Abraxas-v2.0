from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.belief_graph_engine_advisory_receipt_implementation_plan import (
    BLOCKED_ACTIONS,
    build_belief_graph_engine_advisory_receipt_implementation_plan,
    render_belief_graph_engine_advisory_receipt_implementation_plan_markdown,
)
from core.canonical.json import canonical_hash
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/belief_graph_engine_advisory_receipt_implementation_plan.v1.schema.json"
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_belief_graph_engine_advisory_receipt_implementation_plan.py",
    "local_belief_graph_engine_advisory_receipt_implementation_plan_runner",
)


def test_receipt_implementation_plan_is_advisory_only() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_plan(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "BeliefGraphEngineAdvisoryReceiptImplementationPlan.v1"
    assert packet["plan_status"] == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_PLAN_READY"
    assert packet["source_plan"]["source_ready"] is True
    assert packet["implementation_plan_scope"] == "ADVISORY_RECEIPT_IMPLEMENTATION_PLAN_ONLY"
    assert packet["receipt_code_creation_authorized"] is False
    assert packet["receipt_implementation_authorized"] is False
    assert packet["receipt_implementation_performed"] is False
    assert packet["belief_graph_engine_implementation_authorized"] is False
    assert packet["belief_graph_engine_implementation_performed"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_receipt_implementation_plan_scopes_steps_gates_and_commands() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_plan(repo_root=REPO_ROOT)

    assert len(packet["planned_implementation_steps"]) == 5
    assert len(packet["planned_validation_gates"]) == 5
    assert len(packet["planned_validation_commands"]) == 3
    assert (
        packet["recommended_next_lane"]
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_GATE"
    )
    for action in BLOCKED_ACTIONS:
        assert action in packet["blocked_actions"]
    assert all(step["requires_future_authorization"] is True for step in packet["planned_implementation_steps"])
    assert all(step["creates_runtime_surface"] is False for step in packet["planned_implementation_steps"])
    assert all(gate["grants_authority"] is False for gate in packet["planned_validation_gates"])


def test_receipt_implementation_plan_schema_and_hash_are_stable() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_plan(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_receipt_implementation_plan_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/audit/belief_graph_engine_advisory_receipt_implementation_plan_001.latest.json"
    out_md = tmp_path / "out/audit/belief_graph_engine_advisory_receipt_implementation_plan_001.latest.md"

    first = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_receipt_implementation_plan_markdown() -> None:
    packet = build_belief_graph_engine_advisory_receipt_implementation_plan(repo_root=REPO_ROOT)
    markdown = render_belief_graph_engine_advisory_receipt_implementation_plan_markdown(packet)

    assert markdown[0] == "# Belief Graph Engine Advisory Receipt Implementation Plan"
    assert any("BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CODE_CREATION" in line for line in markdown)


def test_receipt_implementation_plan_registry_entries() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/audit/belief_graph_engine_advisory_receipt_implementation_plan_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/audit/belief_graph_engine_advisory_receipt_implementation_plan_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
