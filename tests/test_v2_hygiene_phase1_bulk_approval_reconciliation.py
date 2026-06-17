from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_phase1_bulk_approval_reconciliation import (
    build_v2_hygiene_phase1_bulk_approval_reconciliation,
    render_v2_hygiene_phase1_bulk_approval_reconciliation_markdown,
    write_v2_hygiene_phase1_bulk_approval_reconciliation,
)
from scripts import run_v2_hygiene_phase1_bulk_approval_reconciliation

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/v2_hygiene_phase1_bulk_approval_reconciliation.v1.schema.json"
)


def test_v2_hygiene_phase1_bulk_approval_reconciliation_holds_after_bulk_review() -> None:
    first = build_v2_hygiene_phase1_bulk_approval_reconciliation(REPO_ROOT)
    second = build_v2_hygiene_phase1_bulk_approval_reconciliation(REPO_ROOT)

    assert first["reconciliation_hash"] == second["reconciliation_hash"]
    assert (
        first["reconciliation_status"]
        == "V2_HYGIENE_PHASE1_BULK_APPROVAL_RECONCILIATION_HELD_FOR_OPERATOR_AUTHORIZATION"
    )
    assert first["source_ready"] is True
    assert first["bulk_review_only_approval_recorded"] is True
    assert first["operator_decision_after_bulk_review"] == "HOLD"
    assert first["effect_summary"]["phase1_task_count"] == 14
    assert first["effect_summary"]["held_task_count"] == 14
    assert first["effect_summary"]["implementation_authorized_task_count"] == 0
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_v2_hygiene_phase1_bulk_approval_reconciliation_denies_authority() -> None:
    packet = build_v2_hygiene_phase1_bulk_approval_reconciliation(REPO_ROOT)

    assert packet["implementation_authorized"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_prepare_patch"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["authorization_granted"] is False
    assert packet["authorization_record_created"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["operator_evidence_bundle_created"] is False
    assert packet["hygiene_code_creation_authorized"] is False
    assert packet["schema_file_creation_authorized"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(
        task["implementation_authorized"] is False
        for task in packet["phase1_task_effects"]
    )


def test_v2_hygiene_phase1_bulk_approval_reconciliation_maps_phase1_tasks() -> None:
    packet = build_v2_hygiene_phase1_bulk_approval_reconciliation(REPO_ROOT)
    tasks = {task["task_id"]: task for task in packet["phase1_task_effects"]}

    assert tasks["phase1_p0_001"]["task"] == "Set up folder structure"
    assert tasks["phase1_p0_002"]["repo_path"] == "abraxas/v2/hygiene/loop_dynamics.py"
    assert tasks["phase1_p0_006"]["task"] == "Implement LoopAwarenessRune"
    assert tasks["phase1_p1_010"]["bulk_review_disposition"] == "REVIEW_ONLY_APPROVED"
    assert (
        tasks["phase1_p2_012"]["post_reconciliation_status"]
        == "HELD_FOR_EXPLICIT_OPERATOR_AUTHORIZATION"
    )


def test_v2_hygiene_phase1_bulk_approval_reconciliation_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_bulk_approval_reconciliation(tmp_path)

    assert (
        packet["reconciliation_status"]
        == "V2_HYGIENE_PHASE1_BULK_APPROVAL_RECONCILIATION_BLOCKED"
    )
    assert packet["source_ready"] is False
    assert packet["valid_for_execution"] is False
    assert packet["blockers"] == ["phase1_bulk_approval_sources_not_reconciled"]


def test_v2_hygiene_phase1_bulk_approval_reconciliation_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_bulk_approval_reconciliation(REPO_ROOT)
    packet_without_hash = dict(packet)
    reconciliation_hash = packet_without_hash.pop("reconciliation_hash")
    assert reconciliation_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase1_bulk_approval_reconciliation_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_bulk_approval_reconciliation(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = (
        tmp_path
        / "out/operator_review/v2_hygiene_phase1_bulk_approval_reconciliation_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_bulk_approval_reconciliation.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["reconciliation_hash"] == packet["reconciliation_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase1_bulk_approval_reconciliation_markdown() -> None:
    packet = build_v2_hygiene_phase1_bulk_approval_reconciliation(REPO_ROOT)
    markdown = render_v2_hygiene_phase1_bulk_approval_reconciliation_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Phase 1 Bulk Approval Reconciliation"
    assert any("bulk_review_status" in line for line in markdown)
    assert any("phase1_p0_001" in line for line in markdown)
