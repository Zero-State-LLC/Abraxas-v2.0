from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.p102g_plus_operator_decision_surface_audit import (
    build_p102g_plus_operator_decision_surface_audit,
    render_p102g_plus_operator_decision_surface_audit_markdown,
)
from scripts import run_p102g_plus_operator_decision_surface_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/operator_review/p102g_plus_operator_decision_surface_audit.v1.schema.json"


def test_p102g_plus_operator_decision_surface_audit_ready() -> None:
    first = build_p102g_plus_operator_decision_surface_audit(REPO_ROOT)
    second = build_p102g_plus_operator_decision_surface_audit(REPO_ROOT)

    assert first["audit_hash"] == second["audit_hash"]
    assert first["audit_status"] == "P102G_PLUS_OPERATOR_DECISION_SURFACE_AUDIT_READY"
    assert first["surface_count"] == 11
    assert first["observed_surface_count"] == first["surface_count"]
    assert first["status_match_count"] == first["surface_count"]
    assert first["authority_lock_pass_count"] == first["surface_count"]
    assert "codegen_phase1_validation_review_evidence_dry_run_review" in first["held_surfaces"]
    runtime_surface = next(
        item
        for item in first["surface_records"]
        if item["surface_id"] == "runtime_integration_gate_operator_review_advisory_spec_plan"
    )
    assert runtime_surface["source_observed"] is True
    assert runtime_surface["status_matches_expected"] is True
    assert runtime_surface["authority_lock_passed"] is True
    assert "artifact_lineage_direct_repair_scoped_execution_receipt" in first["review_accepted_surfaces"]


def test_p102g_plus_operator_decision_surface_audit_denies_authority() -> None:
    packet = build_p102g_plus_operator_decision_surface_audit(REPO_ROOT)

    assert packet["operator_decision_record_created"] is False
    assert packet["operator_authorization_record_created"] is False
    assert packet["operator_attestation_observed"] is False
    assert packet["shadow_replay_authorized"] is False
    assert packet["codegen_implementation_authorized"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(
        finding["authority_granted"] is False for finding in packet["audit_findings"]
    )


def test_p102g_plus_operator_decision_surface_audit_tracks_notion_codegen_conventions() -> None:
    packet = build_p102g_plus_operator_decision_surface_audit(REPO_ROOT)

    assert "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_SPEC_PLAN_001" in packet[
        "notion_context"
    ]["source_pages_observed"]
    assert "Abraxas v2.0 Live Status Dashboard & Alignment Hub" in packet[
        "notion_context"
    ]["source_pages_observed"]
    assert "P102G+CODEGEN-ODR-###" in packet["notion_context"]["lane_prefixes"]
    assert "META-P102G+CODEGEN-META-###" in packet["notion_context"]["lane_prefixes"]
    assert packet["notion_context"]["source_observed_date"] == "2026-06-12"


def test_p102g_plus_operator_decision_surface_audit_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_p102g_plus_operator_decision_surface_audit(tmp_path)

    assert packet["audit_status"] == "P102G_PLUS_OPERATOR_DECISION_SURFACE_AUDIT_DEGRADED"
    assert packet["observed_surface_count"] == 0
    assert packet["status_match_count"] == 0
    assert packet["authority_lock_pass_count"] == 0
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False
    assert any(
        finding["finding_status"] == "FAIL_CLOSED"
        for finding in packet["audit_findings"]
    )


def test_p102g_plus_operator_decision_surface_audit_schema_and_hash_are_stable() -> None:
    packet = build_p102g_plus_operator_decision_surface_audit(REPO_ROOT)
    packet_without_hash = dict(packet)
    audit_hash = packet_without_hash.pop("audit_hash")
    assert audit_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_p102g_plus_operator_decision_surface_audit_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = tmp_path / "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json"
    out_md = tmp_path / "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.md"

    first = run_p102g_plus_operator_decision_surface_audit.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_p102g_plus_operator_decision_surface_audit.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_p102g_plus_operator_decision_surface_audit_markdown_names_hold() -> None:
    packet = build_p102g_plus_operator_decision_surface_audit(REPO_ROOT)
    markdown = render_p102g_plus_operator_decision_surface_audit_markdown(packet)

    assert markdown[0] == "# P102G+ Operator Decision Surface Audit"
    assert any("recommended_next_patch: NOT_COMPUTABLE" in line for line in markdown)
    assert any("codegen_phase1_decision_record_review" in line for line in markdown)
    assert any(
        "runtime_integration_gate_operator_review_advisory_spec_plan" in line
        for line in markdown
    )
