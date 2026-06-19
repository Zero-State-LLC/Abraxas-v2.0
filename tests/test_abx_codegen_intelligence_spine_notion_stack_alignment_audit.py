from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_notion_stack_alignment_audit import (
    EXPECTED_HELD_REVIEW_STATUS,
    EXPECTED_PACKET_RECEIPT_STATUS,
    build_abx_codegen_intelligence_spine_notion_stack_alignment_audit,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_notion_stack_alignment_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_notion_stack_alignment_audit.v1.schema.json"
)


def test_codegen_notion_stack_alignment_audit_is_ready_and_held() -> None:
    packet = build_abx_codegen_intelligence_spine_notion_stack_alignment_audit(
        repo_root=REPO_ROOT
    )

    assert (
        packet["audit_status"]
        == "ABX_CODEGEN_INTELLIGENCE_SPINE_NOTION_STACK_ALIGNMENT_AUDIT_READY"
    )
    assert packet["target_surface"] == "ABX_CODEGEN_INTELLIGENCE_SPINE_001"
    assert packet["alignment_blockers"] == []
    assert all(check["passed"] is True for check in packet["alignment_checks"])
    assert (
        packet["current_edge"]["packet_validation_receipt_status"]
        == EXPECTED_PACKET_RECEIPT_STATUS
    )
    assert (
        packet["current_edge"]["phase1_operator_review_status"]
        == EXPECTED_HELD_REVIEW_STATUS
    )
    assert packet["current_edge"]["downstream"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_codegen_notion_stack_alignment_audit_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_notion_stack_alignment_audit(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["code_generation_authorized"] is False
    assert packet["file_writeback_authorized"] is False
    assert packet["shadow_replay_execution_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["scheduler_mutation_authorized"] is False
    assert packet["queue_mutation_authorized"] is False
    assert packet["runtime_mutation_authorized"] is False
    assert packet["canon_mutation_authorized"] is False
    assert packet["forecast_routing_authorized"] is False
    assert packet["activation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_notion_stack_alignment_audit_observes_requested_contracts() -> None:
    packet = build_abx_codegen_intelligence_spine_notion_stack_alignment_audit(
        repo_root=REPO_ROOT
    )
    schema_paths = {record["path"] for record in packet["schema_contracts"]}
    fixtures = packet["fixture_vectors"]

    assert {
        "contracts/canon/gap_diagnosis_packet.v1.schema.json",
        "contracts/canon/improvement_proposal.v1.schema.json",
        "contracts/canon/shadow_improvement_receipt.v1.schema.json",
    } <= schema_paths
    assert fixtures["notion_samples_copied_verbatim"] is False
    assert fixtures["valid_fixture_count"] == 5
    assert fixtures["negative_fixture_count"] == 5
    assert "gap_diagnosis_golden.v1.json" in fixtures["expected_valid_fixtures"]
    assert (
        "invalid_improvement_proposal_missing_operator_decision.v1.json"
        in fixtures["expected_negative_fixtures"]
    )


def test_codegen_notion_stack_alignment_audit_fails_closed_without_held_review(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_notion_stack_alignment_audit(
        repo_root=REPO_ROOT,
        phase1_held_review_path=tmp_path / "missing-held-review.json",
    )

    assert (
        packet["audit_status"]
        == "ABX_CODEGEN_INTELLIGENCE_SPINE_NOTION_STACK_ALIGNMENT_AUDIT_BLOCKED"
    )
    assert "phase1_operator_review_held_without_authority" in packet[
        "alignment_blockers"
    ]
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False


def test_codegen_notion_stack_alignment_audit_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_notion_stack_alignment_audit(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    audit_hash = packet_without_hash.pop("audit_hash")
    assert audit_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_notion_stack_alignment_audit_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_notion_stack_alignment_audit_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_notion_stack_alignment_audit.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_notion_stack_alignment_audit.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
    assert first_md.startswith(
        "# ABX Codegen Intelligence Spine Notion Stack Alignment Audit\n"
    )
    assert "phase1_operator_review_status" in first_md
