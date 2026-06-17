from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run import (
    write_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run,
)
from core.abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review import (
    build_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review,
    render_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_markdown,
    write_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review

REPO_ROOT = Path(__file__).resolve().parents[1]


def _seed_ready_evidence_dry_run(tmp_path: Path) -> None:
    write_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run(
        REPO_ROOT,
        out_root=tmp_path,
    )


def test_codegen_phase1_validation_review_evidence_dry_run_review_held() -> None:
    first = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review(
        REPO_ROOT
    )
    second = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review(
        REPO_ROOT
    )

    assert first["review_hash"] == second["review_hash"]
    assert (
        first["status"]
        == "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR"
    )
    assert first["source_validation_review_evidence_dry_run_ready"] is True
    assert first["selected_operator_decision"] == "HOLD_FOR_OPERATOR_REVIEW"
    assert first["selected_follow_on_action"] == "MAINTAIN_VALIDATION_REVIEW_EVIDENCE_HOLD"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False


def test_codegen_phase1_validation_review_evidence_dry_run_review_denies_authority() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review(
        REPO_ROOT
    )

    assert packet["operator_review_required"] is True
    assert packet["operator_attestations_present"] is False
    assert packet["operator_decision_attested"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["decision_record_created"] is False
    assert packet["authorization_record_created"] is False
    assert packet["authorization_record_lane_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["implementation_unblocked"] is False
    assert packet["shadow_replay_execution_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_decision_record"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(finding["authority_granted"] is False for finding in packet["review_findings"])


def test_codegen_phase1_validation_review_evidence_dry_run_review_records_missing_operator_evidence() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review(
        REPO_ROOT
    )
    findings = {finding["finding_id"]: finding for finding in packet["review_findings"]}

    assert "validation_review_evidence_dry_run_ready" in findings
    assert "external_operator_attestations_missing" in findings
    assert findings["external_operator_attestations_missing"]["finding_status"] == "HELD_FOR_OPERATOR"
    assert set(packet["source_evaluation_blockers"]) == {
        "operator_identity_not_attested",
        "operator_decision_not_attested",
        "operator_acknowledgements_not_attested",
        "operator_provenance_evidence_not_attested",
        "operator_evidence_output_not_attested",
    }
    assert set(packet["source_simulated_evidence_group_ids"]) == {
        "operator_identity",
        "operator_decision",
        "authority_acknowledgements",
        "provenance_evidence",
        "evidence_outputs",
    }
    assert "external operator attestations remain missing" in packet["terminal_hold_reason"]


def test_codegen_phase1_validation_review_evidence_dry_run_review_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review(
        tmp_path
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_validation_review_evidence_dry_run_observed"] is False
    assert packet["source_validation_review_evidence_dry_run_ready"] is False
    assert packet["source_validation_review_evidence_dry_run_packet_hash"] == "NOT_COMPUTABLE"
    assert packet["selected_operator_decision"] == "NOT_COMPUTABLE"
    assert packet["valid_for_decision_record"] is False


def test_codegen_phase1_validation_review_evidence_dry_run_review_blocks_mutated_source(
    tmp_path: Path,
) -> None:
    _seed_ready_evidence_dry_run(tmp_path)
    source_path = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_001.latest.json"
    )
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    payload["operator_attestations_present"] = True
    source_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review(
        tmp_path
    )

    assert (
        packet["status"]
        == "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_REVIEW_BLOCKED"
    )
    assert packet["source_validation_review_evidence_dry_run_ready"] is False
    assert packet["selected_follow_on_action"] == "NOT_COMPUTABLE"


def test_codegen_phase1_validation_review_evidence_dry_run_review_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("review_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads(
        (
            REPO_ROOT
            / "contracts/operator_review/"
            "abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)


def test_codegen_phase1_validation_review_evidence_dry_run_review_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    _seed_ready_evidence_dry_run(tmp_path)
    packet = write_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review(
        tmp_path,
        out_root=tmp_path,
    )
    out_json = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review.run(
        repo_root=tmp_path,
        out_root=tmp_path,
    )

    assert second["review_hash"] == packet["review_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_phase1_validation_review_evidence_dry_run_review_markdown() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review(
        REPO_ROOT
    )
    markdown = (
        render_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_markdown(
            packet
        )
    )

    assert (
        markdown[0]
        == "# ABX Codegen Phase 1 Operator Decision Evidence Collection Validation Review Evidence Dry Run Review"
    )
    assert any("safe_to_auto_continue" in line for line in markdown)
    assert any("Source Simulated Evidence Groups" in line for line in markdown)
