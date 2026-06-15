from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.operator_review_required_items_bulk_disposition import (
    build_operator_review_required_items_bulk_disposition,
    render_operator_review_required_items_bulk_disposition_markdown,
)
from scripts import run_operator_review_required_items_bulk_disposition

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/operator_review_required_items_bulk_disposition.v1.schema.json"
)


def _item(packet: dict, surface_id: str) -> dict:
    return next(
        item
        for item in packet["surface_dispositions"]
        if item["surface_id"] == surface_id
    )


def test_operator_review_required_items_bulk_disposition_records_review_only_approval() -> None:
    first = build_operator_review_required_items_bulk_disposition(REPO_ROOT)
    second = build_operator_review_required_items_bulk_disposition(REPO_ROOT)

    assert first["disposition_hash"] == second["disposition_hash"]
    assert (
        first["disposition_status"]
        == "OPERATOR_REVIEW_REQUIRED_ITEMS_BULK_DISPOSITION_REVIEW_ONLY_APPROVED_WITH_HOLDS"
    )
    assert first["source_user_request"] == "examine all operator review required items and approve"
    assert first["surface_count"] == 23
    assert first["review_only_approved_count"] == first["surface_count"]
    assert first["operator_review_required_count"] >= 9
    assert first["held_after_review_count"] == first["operator_review_required_count"]
    assert first["authority_grant_count"] == 0


def test_operator_review_required_items_bulk_disposition_preserves_blockers() -> None:
    packet = build_operator_review_required_items_bulk_disposition(REPO_ROOT)

    pr_item = _item(packet, "pr_644_stack_review_receipt")
    assert pr_item["disposition_status"] == "REVIEW_ONLY_APPROVED_HELD_FOR_PR_OPERATOR_REVIEW"
    assert pr_item["source_blockers"] == [
        "operator_review_not_observed",
        "pr_is_draft",
    ]
    assert pr_item["merge_approval_granted"] is False

    v2_item = _item(
        packet,
        "v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review",
    )
    assert (
        v2_item["disposition_status"]
        == "REVIEW_ONLY_APPROVED_HELD_FOR_EXTERNAL_ATTESTATIONS"
    )
    assert "operator_identity_not_attested" in v2_item["source_blockers"]
    assert v2_item["evidence_bundle_creation_approved"] is False
    assert v2_item["authorization_record_creation_approved"] is False


def test_operator_review_required_items_bulk_disposition_denies_authority() -> None:
    packet = build_operator_review_required_items_bulk_disposition(REPO_ROOT)

    assert packet["review_only_approval_recorded"] is True
    assert packet["bulk_authority_approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["authorization_record_created"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["implementation_authorized"] is False
    assert packet["merge_authority"] is False
    assert packet["safe_to_merge"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(
        item["authority_granted"] is False
        for item in packet["surface_dispositions"]
    )


def test_operator_review_required_items_bulk_disposition_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_operator_review_required_items_bulk_disposition(tmp_path)

    assert packet["disposition_status"] == "OPERATOR_REVIEW_REQUIRED_ITEMS_BULK_DISPOSITION_DEGRADED"
    assert packet["surface_count"] == 0
    assert packet["review_only_approval_recorded"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False
    assert any(
        finding["finding_status"] == "FAIL_CLOSED"
        for finding in packet["review_findings"]
    )


def test_operator_review_required_items_bulk_disposition_schema_and_hash_are_stable() -> None:
    packet = build_operator_review_required_items_bulk_disposition(REPO_ROOT)
    packet_without_hash = dict(packet)
    disposition_hash = packet_without_hash.pop("disposition_hash")
    assert disposition_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_operator_review_required_items_bulk_disposition_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = tmp_path / "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json"
    out_md = tmp_path / "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.md"

    first = run_operator_review_required_items_bulk_disposition.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_operator_review_required_items_bulk_disposition.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_operator_review_required_items_bulk_disposition_markdown_names_approval_scope() -> None:
    packet = build_operator_review_required_items_bulk_disposition(REPO_ROOT)
    markdown = render_operator_review_required_items_bulk_disposition_markdown(packet)

    assert markdown[0] == "# Operator Review Required Items Bulk Disposition"
    assert any("authority_grant_count: 0" in line for line in markdown)
    assert any("pr_644_stack_review_receipt" in line for line in markdown)
    assert any(
        "REVIEW_ONLY_APPROVED_HELD_FOR_EXTERNAL_ATTESTATIONS" in line
        for line in markdown
    )
