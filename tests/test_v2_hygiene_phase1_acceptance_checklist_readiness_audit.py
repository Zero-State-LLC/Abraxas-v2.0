from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_phase1_acceptance_checklist_readiness_audit import (
    OUT_JSON,
    build_v2_hygiene_phase1_acceptance_checklist_readiness_audit,
    render_v2_hygiene_phase1_acceptance_checklist_readiness_audit_markdown,
    write_v2_hygiene_phase1_acceptance_checklist_readiness_audit,
)
from scripts import run_v2_hygiene_phase1_acceptance_checklist_readiness_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/v2_hygiene_phase1_acceptance_checklist_readiness_audit.v1.schema.json"
)


def test_v2_hygiene_phase1_acceptance_checklist_readiness_audit_held() -> None:
    packet = build_v2_hygiene_phase1_acceptance_checklist_readiness_audit(REPO_ROOT)

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_ACCEPTANCE_CHECKLIST_READINESS_AUDIT_HELD_FOR_OPERATOR"
    )
    assert packet["source_ready"] is True
    assert packet["notion_checklist_source"]["status"] == "TASKS_TO_DO"
    assert packet["acceptance_summary"]["total_gate_count"] == 14
    assert packet["acceptance_summary"]["p0_gate_count"] == 6
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_v2_hygiene_phase1_acceptance_checklist_records_are_to_do_and_held() -> None:
    packet = build_v2_hygiene_phase1_acceptance_checklist_readiness_audit(REPO_ROOT)
    records = {record["task_id"]: record for record in packet["acceptance_records"]}

    assert len(records) == 14
    assert records["phase1_p0_005"]["task"] == "Implement HygieneMode system"
    assert records["phase1_p0_005"]["repo_observed"] is False
    assert records["phase1_p0_005"]["checklist_status"] == (
        "NOTION_CHECKLIST_TO_DO_REPO_MISSING_HELD"
    )
    assert records["phase1_p2_014"]["repo_path"] == (
        "out/operator_review/v2_hygiene_phase1_final_review_001.latest.json"
    )
    assert all(record["implementation_authorized"] is False for record in records.values())
    assert all(record["authority_granted"] is False for record in records.values())


def test_v2_hygiene_phase1_acceptance_checklist_denies_authority() -> None:
    packet = build_v2_hygiene_phase1_acceptance_checklist_readiness_audit(REPO_ROOT)

    assert packet["checklist_completion_attested"] is False
    assert packet["schema_file_creation_authorized"] is False
    assert packet["test_file_creation_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["hygiene_code_creation_authorized"] is False
    assert packet["advisory_integration_hook_authorized"] is False
    assert packet["strict_mode_enablement_authorized"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_phase1_acceptance_checklist_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_acceptance_checklist_readiness_audit(REPO_ROOT)
    without_hash = dict(packet)
    audit_hash = without_hash.pop("audit_hash")
    assert audit_hash == canonical_hash(without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase1_acceptance_checklist_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_acceptance_checklist_readiness_audit(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / OUT_JSON
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_acceptance_checklist_readiness_audit.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["audit_hash"] == packet["audit_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase1_acceptance_checklist_markdown() -> None:
    packet = build_v2_hygiene_phase1_acceptance_checklist_readiness_audit(REPO_ROOT)
    markdown = render_v2_hygiene_phase1_acceptance_checklist_readiness_audit_markdown(
        packet,
    )

    assert markdown[0] == "# v2.0 Hygiene Phase 1 Acceptance Checklist Readiness Audit"
    assert any("Implement HygieneMode system" in line for line in markdown)
    assert any("p0_missing_gate_count" in line for line in markdown)
