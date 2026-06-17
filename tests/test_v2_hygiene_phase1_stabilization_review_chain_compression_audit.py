from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run import (
    write_v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run,
)
from core.sync.v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review import (
    REVIEW_JSON_PATH as SOURCE_REVIEW_JSON_PATH,
    write_v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review,
)
from core.sync.v2_hygiene_phase1_stabilization_review_chain_compression_audit import (
    AUDIT_JSON_PATH,
    build_v2_hygiene_phase1_stabilization_review_chain_compression_audit,
    render_v2_hygiene_phase1_stabilization_review_chain_compression_audit_markdown,
    write_v2_hygiene_phase1_stabilization_review_chain_compression_audit,
)
from scripts import run_v2_hygiene_phase1_stabilization_review_chain_compression_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_stabilization_review_chain_compression_audit.v1.schema.json"
)


def _seed_ready_source(tmp_path: Path) -> None:
    write_v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run(
        REPO_ROOT,
        out_root=tmp_path,
    )
    write_v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review(
        tmp_path,
        out_root=tmp_path,
    )


def test_v2_hygiene_phase1_stabilization_review_chain_compression_audit_held() -> None:
    first = build_v2_hygiene_phase1_stabilization_review_chain_compression_audit(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase1_stabilization_review_chain_compression_audit(
        REPO_ROOT
    )

    assert first["audit_hash"] == second["audit_hash"]
    assert (
        first["status"]
        == "V2_HYGIENE_PHASE1_STABILIZATION_REVIEW_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR"
    )
    assert first["source_review_ready"] is True
    assert first["recursive_review_chain_compressed"] is True
    assert (
        first["compression_recommendation"]
        == "COMPRESS_TO_TERMINAL_OPERATOR_STABILIZATION_HOLD"
    )
    assert (
        first["selected_operator_decision"]
        == "HOLD_FOR_OPERATOR_STABILIZATION_DECISION"
    )
    assert (
        first["selected_follow_on_action"]
        == "MAINTAIN_V2_HYGIENE_PHASE1_STABILIZATION_HOLD"
    )
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["downstream"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False


def test_v2_hygiene_phase1_stabilization_review_chain_compression_audit_findings() -> None:
    packet = build_v2_hygiene_phase1_stabilization_review_chain_compression_audit(
        REPO_ROOT
    )
    findings = {finding["finding_id"]: finding for finding in packet["review_findings"]}

    assert packet["source_readiness"] == "SOURCE_STABILIZATION_REVIEW_READY"
    assert findings["source_stabilization_review_ready_and_held"][
        "finding_status"
    ] == "OBSERVED"
    assert findings["recursive_review_chain_detected"]["finding_status"] == "OBSERVED"
    assert (
        findings["terminal_operator_stabilization_required"]["finding_status"]
        == "HELD_FOR_OPERATOR"
    )
    assert (
        "terminal operator-stabilization hold" in packet["terminal_hold_reason"]
    )
    assert packet["source_validation_blockers"] == [
        "operator_identity_not_attested",
        "strategy_scope_acknowledgement_not_attested",
        "stabilization_disposition_not_attested",
        "authority_boundary_acknowledgement_not_attested",
        "terminal_output_controls_not_attested",
    ]


def test_v2_hygiene_phase1_stabilization_review_chain_compression_audit_denies_authority() -> None:
    packet = build_v2_hygiene_phase1_stabilization_review_chain_compression_audit(
        REPO_ROOT
    )

    assert packet["compression_audit_only"] is True
    assert packet["operator_review_required"] is True
    assert packet["operator_input_required"] is True
    assert packet["operator_attestations_present"] is False
    assert packet["operator_decision_attested"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["operator_evidence_bundle_created"] is False
    assert packet["decision_record_created"] is False
    assert packet["decision_record_creation_authorized"] is False
    assert packet["authorization_record_created"] is False
    assert packet["authorization_record_creation_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["hygiene_code_creation_authorized"] is False
    assert packet["schema_file_creation_authorized"] is False
    assert packet["v2_module_registration_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["strict_mode_enablement_authorized"] is False
    assert packet["projection_surface_mutation_authorized"] is False
    assert packet["schema_mutation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_decision_record"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(
        finding["authority_granted"] is False for finding in packet["review_findings"]
    )


def test_v2_hygiene_phase1_stabilization_review_chain_compression_audit_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_stabilization_review_chain_compression_audit(
        tmp_path
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_review_observed"] is False
    assert packet["source_review_ready"] is False
    assert packet["recursive_review_chain_compressed"] is False
    assert packet["compression_recommendation"] == "REPAIR_SOURCE_REVIEW_BEFORE_COMPRESSION"
    assert packet["selected_operator_decision"] == "NOT_COMPUTABLE"
    assert packet["valid_for_implementation"] is False


def test_v2_hygiene_phase1_stabilization_review_chain_compression_audit_blocks_mutated_source(
    tmp_path: Path,
) -> None:
    _seed_ready_source(tmp_path)
    source_path = tmp_path / SOURCE_REVIEW_JSON_PATH
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    payload["safe_to_auto_continue"] = True
    write_canonical_json(source_path, payload)

    packet = build_v2_hygiene_phase1_stabilization_review_chain_compression_audit(
        tmp_path
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_STABILIZATION_REVIEW_CHAIN_COMPRESSION_AUDIT_BLOCKED"
    )
    assert packet["source_review_ready"] is False
    assert packet["recursive_review_chain_compressed"] is False
    assert packet["selected_follow_on_action"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False


def test_v2_hygiene_phase1_stabilization_review_chain_compression_audit_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_stabilization_review_chain_compression_audit(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    audit_hash = packet_without_hash.pop("audit_hash")
    assert audit_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase1_stabilization_review_chain_compression_audit_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    _seed_ready_source(tmp_path)
    packet = write_v2_hygiene_phase1_stabilization_review_chain_compression_audit(
        tmp_path,
        out_root=tmp_path,
    )
    out_json = tmp_path / AUDIT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_stabilization_review_chain_compression_audit.run(
        repo_root=tmp_path,
        out_root=tmp_path,
    )

    assert second["audit_hash"] == packet["audit_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase1_stabilization_review_chain_compression_audit_markdown() -> None:
    packet = build_v2_hygiene_phase1_stabilization_review_chain_compression_audit(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_phase1_stabilization_review_chain_compression_audit_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# v2.0 Hygiene Phase 1 Stabilization Review Chain Compression Audit"
    )
    assert any("recursive_review_chain_detected" in line for line in markdown)
    assert any("operator_identity_not_attested" in line for line in markdown)
