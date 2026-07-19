from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_phase1_operator_decision_evidence_collection_dry_run import (
    build_abx_codegen_phase1_operator_decision_evidence_collection_dry_run,
    render_abx_codegen_phase1_operator_decision_evidence_collection_dry_run_markdown,
    write_abx_codegen_phase1_operator_decision_evidence_collection_dry_run,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_phase1_operator_decision_evidence_collection_dry_run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_codegen_phase1_operator_decision_evidence_collection_dry_run_ready() -> None:
    first = build_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(
        REPO_ROOT
    )
    second = build_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(
        REPO_ROOT
    )

    assert first["dry_run_hash"] == second["dry_run_hash"]
    assert (
        first["status"]
        == "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_DRY_RUN_READY"
    )
    assert first["source_evidence_collection_plan_ready"] is True
    assert first["simulated_only"] is True
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_codegen_phase1_operator_decision_evidence_collection_dry_run_denies_authority() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(
        REPO_ROOT
    )

    assert packet["operator_attestations_present"] is False
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


def test_codegen_phase1_operator_decision_evidence_collection_dry_run_simulates_missing_bundle() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(
        REPO_ROOT
    )
    groups = {
        group["group_id"]: group for group in packet["simulated_evidence_bundle"]
    }

    assert packet["readiness_summary"]["groups_ready"] == 0
    assert packet["readiness_summary"]["groups_total"] == 5
    assert packet["readiness_summary"]["evidence_bundle_complete"] is False
    assert set(groups) == {
        "operator_identity",
        "operator_decision",
        "authority_acknowledgements",
        "provenance_evidence",
        "evidence_outputs",
    }
    assert groups["operator_identity"]["attested"] is False
    assert "operator_id" in groups["operator_identity"]["missing_fields"]
    assert "selected_decision" in groups["operator_decision"]["missing_fields"]
    assert "operator_identity_not_attested" in packet["evaluation_blockers"]


def test_codegen_phase1_operator_decision_evidence_collection_dry_run_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(
        tmp_path
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_evidence_collection_plan_observed"] is False
    assert packet["source_evidence_collection_plan_ready"] is False
    assert packet["source_evidence_collection_plan_hash"] == "NOT_COMPUTABLE"
    assert packet["simulated_evidence_bundle"] == []
    assert packet["valid_for_decision_record"] is False
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert "source_evidence_collection_plan_missing_or_not_ready" in packet[
        "evaluation_blockers"
    ]


def test_codegen_phase1_operator_decision_evidence_collection_dry_run_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("dry_run_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads(
        (
            REPO_ROOT
            / "contracts/operator_review/"
            "abx_codegen_phase1_operator_decision_evidence_collection_dry_run.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)


def test_codegen_phase1_operator_decision_evidence_collection_dry_run_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_phase1_operator_decision_evidence_collection_dry_run_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_phase1_operator_decision_evidence_collection_dry_run.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["dry_run_hash"] == packet["dry_run_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_phase1_operator_decision_evidence_collection_dry_run_markdown() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(
        REPO_ROOT
    )
    markdown = (
        render_abx_codegen_phase1_operator_decision_evidence_collection_dry_run_markdown(
            packet
        )
    )

    assert (
        markdown[0]
        == "# ABX Codegen Phase 1 Operator Decision Evidence Collection Dry Run"
    )
    assert any("operator_identity_not_attested" in line for line in markdown)
    assert any("operator_identity" in line for line in markdown)
