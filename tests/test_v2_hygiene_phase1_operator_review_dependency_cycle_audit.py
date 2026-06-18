from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_phase1_operator_review_dependency_cycle_audit import (
    AUDIT_JSON_PATH,
    build_v2_hygiene_phase1_operator_review_dependency_cycle_audit,
    render_v2_hygiene_phase1_operator_review_dependency_cycle_audit_markdown,
    write_v2_hygiene_phase1_operator_review_dependency_cycle_audit,
)
from scripts import run_v2_hygiene_phase1_operator_review_dependency_cycle_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_operator_review_dependency_cycle_audit.v1.schema.json"
)


def test_v2_hygiene_phase1_operator_review_dependency_cycle_audit_observes_cycle() -> None:
    first = build_v2_hygiene_phase1_operator_review_dependency_cycle_audit(REPO_ROOT)
    second = build_v2_hygiene_phase1_operator_review_dependency_cycle_audit(REPO_ROOT)

    assert first["audit_hash"] == second["audit_hash"]
    assert (
        first["audit_status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_DEPENDENCY_CYCLE_AUDIT_BLOCKED"
    )
    assert first["cycle_observed"] is False
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_v2_hygiene_phase1_operator_review_dependency_cycle_audit_edges() -> None:
    packet = build_v2_hygiene_phase1_operator_review_dependency_cycle_audit(REPO_ROOT)
    edges = {edge["edge_id"]: edge for edge in packet["cycle_edges"]}

    assert (
        edges["bulk_disposition_scans_phase1_reconciliation"]["hash_current"]
        is True
    )
    assert (
        edges["phase1_reconciliation_consumes_bulk_disposition"]["hash_current"]
        is False
    )
    assert any(
        record["path"]
        == "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json"
        for record in packet["source_records"]
    )


def test_v2_hygiene_phase1_operator_review_dependency_cycle_audit_denies_authority() -> None:
    packet = build_v2_hygiene_phase1_operator_review_dependency_cycle_audit(REPO_ROOT)

    assert packet["authorization_granted"] is False
    assert packet["authorization_record_created"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["operator_evidence_bundle_created"] is False
    assert packet["implementation_authorized"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_prepare_patch"] is False
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(
        finding["authority_granted"] is False for finding in packet["audit_findings"]
    )


def test_v2_hygiene_phase1_operator_review_dependency_cycle_audit_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_operator_review_dependency_cycle_audit(tmp_path)

    assert (
        packet["audit_status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_DEPENDENCY_CYCLE_AUDIT_BLOCKED"
    )
    assert packet["cycle_observed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_v2_hygiene_phase1_operator_review_dependency_cycle_audit_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_operator_review_dependency_cycle_audit(REPO_ROOT)
    packet_without_hash = dict(packet)
    audit_hash = packet_without_hash.pop("audit_hash")
    assert audit_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase1_operator_review_dependency_cycle_audit_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_operator_review_dependency_cycle_audit(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / AUDIT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_operator_review_dependency_cycle_audit.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["audit_hash"] == packet["audit_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase1_operator_review_dependency_cycle_audit_markdown() -> None:
    packet = build_v2_hygiene_phase1_operator_review_dependency_cycle_audit(REPO_ROOT)
    markdown = render_v2_hygiene_phase1_operator_review_dependency_cycle_audit_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# v2.0 Hygiene Phase 1 Operator Review Dependency Cycle Audit"
    )
    assert any("bulk_disposition_scans_phase1_reconciliation" in line for line in markdown)
    assert any("HOLD_FOR_OPERATOR_STABILIZATION_STRATEGY" in line for line in markdown)
