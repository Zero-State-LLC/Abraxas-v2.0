from __future__ import annotations

import json
import shutil
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.operator_review_terminal_hold_consolidation_receipt import (
    AUTHORITY_BOOLEAN_FIELDS,
    build_operator_review_terminal_hold_consolidation_receipt,
    render_operator_review_terminal_hold_consolidation_receipt_markdown,
)
from scripts import run_operator_review_terminal_hold_consolidation_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/operator_review_terminal_hold_consolidation_receipt.v1.schema.json"
)
P102G_PATH = "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json"
BULK_PATH = "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json"


def _family(packet: dict, family_id: str) -> dict:
    return next(item for item in packet["terminal_hold_matrix"] if item["family_id"] == family_id)


def _copy_sources(tmp_path: Path) -> None:
    for rel_path in (P102G_PATH, BULK_PATH):
        target = tmp_path / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel_path, target)


def test_operator_review_terminal_hold_consolidation_receipt_ready_path_is_stable() -> None:
    first = build_operator_review_terminal_hold_consolidation_receipt(REPO_ROOT)
    second = build_operator_review_terminal_hold_consolidation_receipt(REPO_ROOT)

    assert first["receipt_hash"] == second["receipt_hash"]
    assert first == second
    assert first["receipt_status"] == "OPERATOR_REVIEW_TERMINAL_HOLD_CONSOLIDATION_RECEIPT_READY"
    assert first["source_readiness"] == "SOURCE_AGGREGATES_READY"
    assert first["source_surface_count"] >= 109
    assert first["source_operator_review_required_count"] >= 73
    assert first["source_authority_grant_count"] == 0
    assert first["terminal_hold_matrix_ready"] is True
    assert first["terminal_hold_family_count"] >= 8
    assert first["terminal_hold_surface_count"] >= 73
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False
    assert first["valid_for_execution"] is False


def test_operator_review_terminal_hold_consolidation_receipt_includes_v2_stabilization_hold() -> None:
    packet = build_operator_review_terminal_hold_consolidation_receipt(REPO_ROOT)
    stabilization = _family(packet, "v2_phase1_stabilization")

    assert "v2_hygiene_phase1_stabilization_review_chain_compression_audit_001" in (
        stabilization["held_surface_ids"]
    )
    assert (
        "v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_001"
        in stabilization["held_surface_ids"]
    )
    assert "v2_hygiene_phase1_stabilization_review_chain_compression_audit_001" in (
        stabilization["missing_attestation_surface_ids"]
    )
    assert stabilization["missing_attestation_surface_count"] >= 1
    assert stabilization["authority_grant_count"] == 0


def test_operator_review_terminal_hold_consolidation_receipt_denies_authority() -> None:
    packet = build_operator_review_terminal_hold_consolidation_receipt(REPO_ROOT)

    assert all(packet[field] is False for field in AUTHORITY_BOOLEAN_FIELDS)
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(
        finding["authority_granted"] is False
        for finding in packet["consolidation_findings"]
    )
    for family in packet["terminal_hold_matrix"]:
        assert family["authority_grant_count"] == 0
        assert family["valid_for_execution"] is False
        assert family["safe_to_auto_continue"] is False
        assert all(value is False for value in family["authority_locks"].values())


def test_operator_review_terminal_hold_consolidation_receipt_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_operator_review_terminal_hold_consolidation_receipt(tmp_path)

    assert packet["receipt_status"] == "NOT_COMPUTABLE"
    assert packet["source_readiness"] == "SOURCE_AGGREGATES_MISSING"
    assert packet["source_p102g_observed"] is False
    assert packet["source_bulk_disposition_observed"] is False
    assert packet["terminal_hold_matrix_ready"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False


def test_operator_review_terminal_hold_consolidation_receipt_blocks_authorizing_source(
    tmp_path: Path,
) -> None:
    _copy_sources(tmp_path)
    bulk_path = tmp_path / BULK_PATH
    bulk = json.loads(bulk_path.read_text(encoding="utf-8"))
    bulk["authority_grant_count"] = 1
    bulk["safe_to_auto_continue"] = True
    write_canonical_json(bulk_path, bulk)

    packet = build_operator_review_terminal_hold_consolidation_receipt(tmp_path)

    assert packet["receipt_status"] == "OPERATOR_REVIEW_TERMINAL_HOLD_CONSOLIDATION_RECEIPT_BLOCKED"
    assert packet["source_readiness"] == "SOURCE_AGGREGATES_NOT_READY"
    assert "bulk_disposition_authority_grants_present" in packet["source_blockers"]
    assert "bulk_disposition_safe_to_auto_continue_not_false" in packet["source_blockers"]
    assert packet["terminal_hold_matrix_ready"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["valid_for_execution"] is False


def test_operator_review_terminal_hold_consolidation_receipt_schema_and_hash_are_stable() -> None:
    packet = build_operator_review_terminal_hold_consolidation_receipt(REPO_ROOT)
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("receipt_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_operator_review_terminal_hold_consolidation_receipt_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = tmp_path / "out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.json"
    out_md = tmp_path / "out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.md"

    first = run_operator_review_terminal_hold_consolidation_receipt.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_operator_review_terminal_hold_consolidation_receipt.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_operator_review_terminal_hold_consolidation_receipt_markdown_names_terminal_hold() -> None:
    packet = build_operator_review_terminal_hold_consolidation_receipt(REPO_ROOT)
    markdown = render_operator_review_terminal_hold_consolidation_receipt_markdown(packet)

    assert markdown[0] == "# Operator Review Terminal Hold Consolidation Receipt"
    assert any("v2_phase1_stabilization" in line for line in markdown)
    assert any("NOT_COMPUTABLE" in line for line in markdown)
