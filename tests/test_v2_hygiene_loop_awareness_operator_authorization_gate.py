from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_loop_awareness_alignment_plan import (
    write_v2_hygiene_loop_awareness_alignment_plan,
    write_v2_hygiene_loop_awareness_alignment_plan_markdown,
)
from core.sync.v2_hygiene_loop_awareness_operator_authorization_gate import (
    build_v2_hygiene_loop_awareness_operator_authorization_gate,
    render_v2_hygiene_loop_awareness_operator_authorization_gate_markdown,
)
from scripts.hygiene import run_v2_hygiene_loop_awareness_alignment_plan
from scripts.hygiene import run_v2_hygiene_loop_awareness_operator_authorization_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate.v1.schema.json"


def _seed_alignment_plan(tmp_path: Path) -> None:
    packet = run_v2_hygiene_loop_awareness_alignment_plan.run(repo_root=REPO_ROOT)
    write_v2_hygiene_loop_awareness_alignment_plan(
        tmp_path / "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.json",
        packet,
    )
    write_v2_hygiene_loop_awareness_alignment_plan_markdown(
        tmp_path / "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.md",
        packet,
    )


def test_v2_hygiene_operator_authorization_gate_held_for_operator() -> None:
    first = build_v2_hygiene_loop_awareness_operator_authorization_gate(REPO_ROOT)
    second = build_v2_hygiene_loop_awareness_operator_authorization_gate(REPO_ROOT)

    assert first["gate_hash"] == second["gate_hash"]
    assert (
        first["gate_status"]
        == "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
    )
    assert first["source_alignment_plan"]["source_ready"] is True
    assert first["authorization_eligible"] is True
    assert first["requires_operator_decision"] is True
    assert first["selected_operator_decision"] == "HOLD"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_v2_hygiene_operator_authorization_gate_denies_all_authority() -> None:
    packet = build_v2_hygiene_loop_awareness_operator_authorization_gate(REPO_ROOT)

    assert packet["operator_authorization_observed"] is False
    assert packet["operator_authorization_record_created"] is False
    assert packet["authorization_granted"] is False
    assert packet["authorization_record_creation_authorized"] is False
    assert packet["v2_module_registration_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["projection_surface_mutation_authorized"] is False
    assert packet["schema_mutation_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["safe_to_prepare_patch"] is False
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_operator_authorization_gate_preserves_workstreams_and_required_fields() -> None:
    packet = build_v2_hygiene_loop_awareness_operator_authorization_gate(REPO_ROOT)

    assert packet["source_alignment_required_workstreams"] == []
    assert "reviewed_alignment_plan_hash" in packet["required_operator_authorization_fields"]
    assert "approved_workstreams" in packet["required_operator_authorization_fields"]
    assert "no_auto_continuation_acknowledged" in packet["required_operator_authorization_fields"]
    assert "V2_HYGIENE_DIRECT_MUTATION" in packet["blocked_actions"]
    assert all(check["grants_authority"] is False for check in packet["authorization_checks"])


def test_v2_hygiene_operator_authorization_gate_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_v2_hygiene_loop_awareness_operator_authorization_gate(tmp_path)

    assert packet["gate_status"] == "NOT_COMPUTABLE"
    assert packet["source_alignment_plan"]["source_ready"] is False
    assert packet["source_alignment_plan"]["hash"] == "NOT_COMPUTABLE"
    assert packet["authorization_eligible"] is False
    assert packet["source_alignment_required_workstreams"] == []
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False


def test_v2_hygiene_operator_authorization_gate_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_loop_awareness_operator_authorization_gate(REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("gate_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_operator_authorization_gate_runner_writes_stable_outputs(tmp_path: Path) -> None:
    _seed_alignment_plan(tmp_path)
    out_json = tmp_path / "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json"
    out_md = tmp_path / "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.md"

    first = run_v2_hygiene_loop_awareness_operator_authorization_gate.run(
        repo_root=tmp_path,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_loop_awareness_operator_authorization_gate.run(
        repo_root=tmp_path,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_operator_authorization_gate_markdown_names_hold() -> None:
    packet = build_v2_hygiene_loop_awareness_operator_authorization_gate(REPO_ROOT)
    markdown = render_v2_hygiene_loop_awareness_operator_authorization_gate_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Loop-Awareness Operator Authorization Gate"
    assert any("selected_operator_decision: HOLD" in line for line in markdown)
    assert any("V2_HYGIENE_DIRECT_MUTATION" in line for line in markdown)
