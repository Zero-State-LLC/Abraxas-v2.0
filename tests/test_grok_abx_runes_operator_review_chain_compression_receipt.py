from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.grok_abx_runes_operator_review_chain_compression_receipt import (
    RECEIPT_JSON_PATH,
    build_grok_abx_runes_operator_review_chain_compression_receipt,
    render_grok_abx_runes_operator_review_chain_compression_receipt_markdown,
    write_grok_abx_runes_operator_review_chain_compression_receipt,
)
from scripts import run_grok_abx_runes_operator_review_chain_compression_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "grok_abx_runes_operator_review_chain_compression_receipt.v1.schema.json"
)


def test_grok_abx_runes_operator_review_chain_compression_receipt_ready() -> None:
    first = build_grok_abx_runes_operator_review_chain_compression_receipt(REPO_ROOT)
    second = build_grok_abx_runes_operator_review_chain_compression_receipt(REPO_ROOT)

    assert first["receipt_hash"] == second["receipt_hash"]
    assert (
        first["status"]
        == "GROK_ABX_RUNES_OPERATOR_REVIEW_CHAIN_COMPRESSED_TO_TERMINAL_HOLD"
    )
    assert first["source_dry_run_ready"] is True
    assert first["recursive_review_chain_compressed"] is True
    assert (
        first["compression_recommendation"]
        == "COMPRESS_TO_TERMINAL_EXTERNAL_OPERATOR_HOLD"
    )
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_grok_abx_runes_operator_review_chain_compression_receipt_terminal_hold() -> None:
    packet = build_grok_abx_runes_operator_review_chain_compression_receipt(REPO_ROOT)
    findings = {finding["finding_id"] for finding in packet["review_findings"]}

    assert packet["source_required_field_count"] == 29
    assert packet["selected_operator_decision"] == (
        "HOLD_FOR_EXTERNAL_OPERATOR_ATTESTATIONS"
    )
    assert (
        packet["selected_follow_on_action"]
        == "STOP_GROK_ABX_RUNES_RECURSIVE_REPO_LANES"
    )
    assert "explicit external operator attestations" in packet["resume_condition"]
    assert "recursive_operator_review_chain_compressed" in findings
    assert "auto_continuation_denied" in findings
    assert "operator_identity_not_attested" in packet["source_evaluation_blockers"]


def test_grok_abx_runes_operator_review_chain_compression_receipt_denies_authority() -> None:
    packet = build_grok_abx_runes_operator_review_chain_compression_receipt(REPO_ROOT)

    assert packet["operator_attestations_present"] is False
    assert packet["operator_evidence_collected"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["decision_record_created"] is False
    assert packet["authorization_record_created"] is False
    assert packet["external_backlog_accepted"] is False
    assert packet["separate_registration_planning_authorized"] is False
    assert packet["catalog_mutation_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["yggdrasil_binding_mutation_authorized"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["valid_for_decision_record"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_grok_abx_runes_operator_review_chain_compression_receipt_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_grok_abx_runes_operator_review_chain_compression_receipt(tmp_path)

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_dry_run_observed"] is False
    assert packet["source_dry_run_ready"] is False
    assert packet["recursive_review_chain_compressed"] is False
    assert packet["source_dry_run_packet_hash"] == "NOT_COMPUTABLE"
    assert packet["selected_operator_decision"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_grok_abx_runes_operator_review_chain_compression_receipt_schema_and_hash_are_stable() -> None:
    packet = build_grok_abx_runes_operator_review_chain_compression_receipt(REPO_ROOT)
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("receipt_hash")

    assert receipt_hash == canonical_hash(packet_without_hash)
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_grok_abx_runes_operator_review_chain_compression_receipt_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_grok_abx_runes_operator_review_chain_compression_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_grok_abx_runes_operator_review_chain_compression_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["receipt_hash"] == packet["receipt_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_grok_abx_runes_operator_review_chain_compression_receipt_markdown() -> None:
    packet = build_grok_abx_runes_operator_review_chain_compression_receipt(REPO_ROOT)
    markdown = render_grok_abx_runes_operator_review_chain_compression_receipt_markdown(
        packet
    )

    assert markdown[0] == "# Grok ABX-Runes Operator Review Chain Compression Receipt"
    assert any("STOP_GROK_ABX_RUNES_RECURSIVE_REPO_LANES" in line for line in markdown)
    assert any("operator_identity_not_attested" in line for line in markdown)
