from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_shadow_replay_harness_implementation_authorization_gate import (
    build_abx_codegen_shadow_replay_harness_implementation_authorization_gate,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_shadow_replay_harness_implementation_authorization_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_shadow_replay_harness_implementation_"
    "authorization_gate.v1.schema.json"
)


def test_codegen_shadow_replay_harness_authorization_gate_holds_for_operator() -> None:
    packet = build_abx_codegen_shadow_replay_harness_implementation_authorization_gate(
        repo_root=REPO_ROOT,
        authorization_record_path="out/operator_review/missing_record.json",
    )

    assert (
        packet["artifact_type"]
        == "AbxCodegenIntelligenceSpineShadowReplayHarnessImplementationAuthorizationGate.v1"
    )
    assert (
        packet["authorization_gate_status"]
        == "SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_HELD_FOR_OPERATOR"
    )
    assert packet["target_surface"] == "ABX_CODEGEN_INTELLIGENCE_SPINE_001"
    assert packet["target_module"] == "core/codegen_shadow_replay_harness.py"
    assert packet["operator_review_required"] is True
    assert packet["implementation_authorization_granted"] is False
    assert packet["record_creation_authorized"] is False
    assert packet["harness_implementation_performed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert "harness_implementation" in packet["blocked_actions"]
    assert "operator_decision_attestation" in packet["blocked_actions"]


def test_codegen_shadow_replay_harness_authorization_gate_granted_with_record() -> None:
    packet = build_abx_codegen_shadow_replay_harness_implementation_authorization_gate(
        repo_root=REPO_ROOT
    )

    assert (
        packet["authorization_gate_status"]
        == "SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_GRANTED"
    )
    assert packet["implementation_authorization_granted"] is True
    assert packet["valid_for_implementation"] is True
    assert packet["operator_review_required"] is False
    assert packet["authority_locks"]["harness_implementation"] is True
    assert packet["authority_locks"]["execution_authority"] is False
    assert "harness_implementation" not in packet["blocked_actions"]
    assert packet["recommended_next_lane"] == "CORE_CODEGEN_SHADOW_REPLAY_HARNESS_IMPLEMENTATION"


def test_codegen_shadow_replay_harness_authorization_gate_scope_is_phase_one() -> None:
    packet = build_abx_codegen_shadow_replay_harness_implementation_authorization_gate(
        repo_root=REPO_ROOT
    )

    scope = packet["implementation_scope"]
    assert scope["phase"] == "PHASE_1_CORE_FOUNDATION"
    assert "run_codegen_shadow_replay" in scope["planned_interfaces"]
    assert "_build_receipt" in scope["planned_interfaces"]
    assert scope["requires_12_run_invariance"] is True
    assert scope["requires_24_run_meta_gate_invariance"] is True

    findings = {item["finding_id"]: item["finding_status"] for item in packet["authorization_findings"]}
    assert findings["implementation_spec_observed"] == "READY_FOR_IMPLEMENTATION"


def test_codegen_shadow_replay_harness_authorization_gate_granted_findings() -> None:
    packet = build_abx_codegen_shadow_replay_harness_implementation_authorization_gate(
        repo_root=REPO_ROOT
    )
    findings = {item["finding_id"]: item["finding_status"] for item in packet["authorization_findings"]}
    assert findings["implementation_spec_observed"] == "READY_FOR_IMPLEMENTATION"
    assert findings["operator_authorization_consumed"] == "AUTHORIZATION_GRANTED"
    assert findings["execution_authority_denied"] == "EXECUTION_NOT_AUTHORIZED"


def test_codegen_shadow_replay_harness_authorization_gate_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_shadow_replay_harness_implementation_authorization_gate(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_shadow_replay_harness_authorization_gate_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_shadow_replay_harness_implementation_"
        "authorization_gate_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_shadow_replay_harness_implementation_authorization_gate.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_shadow_replay_harness_implementation_authorization_gate.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
    assert first_md.startswith(
        "# ABX Codegen Shadow Replay Harness Implementation Authorization Gate\n"
    )
