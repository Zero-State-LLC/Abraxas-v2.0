from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.runtime_integration_gate_operator_review_advisory_spec_plan import (
    build_runtime_integration_gate_operator_review_advisory_spec_plan,
)
from scripts.runtime import run_runtime_integration_gate_operator_review_advisory_spec_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/runtime_integration_gate_operator_review_advisory_spec_plan.v1.schema.json"


def test_runtime_integration_gate_operator_review_plan_is_terminal_advisory_only() -> None:
    packet = build_runtime_integration_gate_operator_review_advisory_spec_plan(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "RuntimeIntegrationGateOperatorReviewAdvisorySpecPlan.v1"
    assert packet["plan_status"] == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_READY"
    assert packet["operator_review_required"] is True
    assert packet["operator_attestation_present"] is False
    assert packet["recommended_next_lane"] == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN"
    assert packet["safe_to_auto_continue"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_runtime_wiring"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["replay_mutation_allowed"] is False
    assert packet["queue_mutation_allowed"] is False
    assert packet["scheduler_mutation_allowed"] is False
    assert packet["forecast_routing_allowed"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["codegen_implementation_allowed"] is False
    assert packet["activation_allowed"] is False
    assert packet["auto_approval_allowed"] is False


def test_runtime_integration_gate_operator_review_plan_schema_and_hash_are_stable() -> None:
    packet = build_runtime_integration_gate_operator_review_advisory_spec_plan(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runtime_integration_gate_operator_review_plan_declares_review_work() -> None:
    packet = build_runtime_integration_gate_operator_review_advisory_spec_plan(repo_root=REPO_ROOT)

    assert packet["source_receipt_status"] == "RUNTIME_INTEGRATION_GATE_RECEIPT_READY_ADVISORY_ONLY"
    assert packet["source_recommended_next_lane"] == (
        "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_OR_ADVISORY_SPEC_PLAN"
    )
    assert "CODEGEN_IMPLEMENTATION" in packet["blocked_patch_classes"]
    assert "MANDATORY_PRE_DISPATCH_WIRING" in packet["blocked_patch_classes"]
    assert {gate["gate_id"] for gate in packet["acceptance_gates"]} == {
        "NO_AUTHORITY_ESCALATION",
        "OPERATOR_ATTESTATION_REQUIRED",
        "SOURCE_RECEIPT_OBSERVED",
    }
    assert {workstream["workstream_id"] for workstream in packet["planned_workstreams"]} == {
        "AUTHORITY_OWNER_MAPPING",
        "CODEGEN_BOUNDARY_REVIEW",
        "NO_AUTHORITY_SEAL_REVIEW",
        "RECEIPT_FRESHNESS_REVIEW",
    }


def test_runtime_integration_gate_operator_review_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/runtime_integration_gate_operator_review_advisory_spec_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_runtime_integration_gate_operator_review_advisory_spec_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_runtime_integration_gate_operator_review_advisory_spec_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
    assert first_md.startswith("# Runtime Integration Gate Operator Review Advisory Spec Plan 001\n")
