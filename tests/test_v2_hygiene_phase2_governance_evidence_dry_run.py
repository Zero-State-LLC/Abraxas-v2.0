from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase2_governance_evidence_dry_run import (
    DRY_RUN_JSON_PATH,
    build_v2_hygiene_phase2_governance_evidence_dry_run,
    render_v2_hygiene_phase2_governance_evidence_dry_run_markdown,
    write_v2_hygiene_phase2_governance_evidence_dry_run,
)
from core.sync.v2_hygiene_phase2_governance_evidence_request_plan import (
    PLAN_JSON_PATH as SOURCE_PLAN_JSON_PATH,
    write_v2_hygiene_phase2_governance_evidence_request_plan,
)
from scripts import run_v2_hygiene_phase2_governance_evidence_dry_run

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/v2_hygiene_phase2_governance_evidence_dry_run.v1.schema.json"
)


def test_v2_hygiene_phase2_governance_evidence_dry_run_ready() -> None:
    first = build_v2_hygiene_phase2_governance_evidence_dry_run(REPO_ROOT)
    second = build_v2_hygiene_phase2_governance_evidence_dry_run(REPO_ROOT)

    assert first["dry_run_hash"] == second["dry_run_hash"]
    assert first["status"] == "V2_HYGIENE_PHASE2_GOVERNANCE_EVIDENCE_DRY_RUN_READY"
    assert first["source_evidence_plan_ready"] is True
    assert first["simulated_only"] is True
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False


def test_v2_hygiene_phase2_governance_evidence_dry_run_simulates_bundle() -> None:
    packet = build_v2_hygiene_phase2_governance_evidence_dry_run(REPO_ROOT)
    bundle = packet["simulated_evidence_bundle"]
    groups = {group["group_id"]: group for group in bundle["groups"]}

    assert bundle["artifact_type"] == (
        "V2HygienePhase2GovernanceEvidenceBundle.v1.simulated"
    )
    assert bundle["evidence_bundle_hash"] == "SIMULATED_PENDING_OPERATOR_INPUT"
    assert packet["readiness_summary"]["required_group_count"] == 5
    assert packet["readiness_summary"]["required_field_count"] == 36
    assert packet["readiness_summary"]["attested_group_count"] == 0
    assert packet["readiness_summary"]["attested_field_count"] == 0
    assert packet["readiness_summary"]["source_missing_control_count"] == 6
    assert set(groups) == {
        "operator_identity",
        "review_scope_acknowledgement",
        "authority_acknowledgements",
        "phase2_governance_control_disposition",
        "terminal_output_controls",
    }
    assert groups["operator_identity"]["attested"] is False
    assert "operator_signature_reference" in groups["operator_identity"][
        "missing_fields"
    ]
    assert groups["phase2_governance_control_disposition"]["source_control_ids"] == [
        "default_advisory_mode",
        "no_output_mutation_without_configuration",
        "metadata_version_owner_posture",
        "hygiene_pipeline_interaction",
        "promotion_governance_review",
        "module_boundary_tests",
    ]
    assert groups["operator_identity"]["fields"][0]["simulated_value"] == (
        "SIMULATED_PENDING_OPERATOR_INPUT"
    )
    assert (
        "phase2_governance_control_disposition_not_attested"
        in packet["evaluation_blockers"]
    )


def test_v2_hygiene_phase2_governance_evidence_dry_run_denies_authority() -> None:
    packet = build_v2_hygiene_phase2_governance_evidence_dry_run(REPO_ROOT)

    assert packet["operator_attestations_present"] is False
    assert packet["operator_decision_attested"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["operator_evidence_bundle_created"] is False
    assert packet["authorization_record_created"] is False
    assert packet["authorization_record_creation_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["module_code_creation_authorized"] is False
    assert packet["module_test_creation_authorized"] is False
    assert packet["module_registration_authorized"] is False
    assert packet["hygiene_pipeline_integration_authorized"] is False
    assert packet["promotion_authorized"] is False
    assert packet["strict_mode_enablement_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_authorization_record"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_phase2_governance_evidence_dry_run_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase2_governance_evidence_dry_run(tmp_path)

    assert packet["status"] == "V2_HYGIENE_PHASE2_GOVERNANCE_EVIDENCE_DRY_RUN_BLOCKED"
    assert packet["source_evidence_plan_observed"] is False
    assert packet["source_evidence_plan_ready"] is False
    assert packet["source_evidence_plan_hash"] == "NOT_COMPUTABLE"
    assert packet["simulated_evidence_bundle"]["groups"] == []
    assert "source_phase2_governance_evidence_request_plan_missing_or_not_ready" in (
        packet["evaluation_blockers"]
    )


def test_v2_hygiene_phase2_governance_evidence_dry_run_blocks_mutated_source(
    tmp_path: Path,
) -> None:
    write_v2_hygiene_phase2_governance_evidence_request_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    source_path = tmp_path / SOURCE_PLAN_JSON_PATH
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["operator_attestations_present"] = True
    write_canonical_json(source_path, source)

    packet = build_v2_hygiene_phase2_governance_evidence_dry_run(tmp_path)

    assert packet["status"] == "V2_HYGIENE_PHASE2_GOVERNANCE_EVIDENCE_DRY_RUN_BLOCKED"
    assert packet["source_evidence_plan_ready"] is False
    assert packet["simulated_evidence_bundle"]["groups"] == []
    assert packet["valid_for_execution"] is False


def test_v2_hygiene_phase2_governance_evidence_dry_run_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase2_governance_evidence_dry_run(REPO_ROOT)
    packet_without_hash = dict(packet)
    dry_run_hash = packet_without_hash.pop("dry_run_hash")
    assert dry_run_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase2_governance_evidence_dry_run_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    write_v2_hygiene_phase2_governance_evidence_request_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    packet = write_v2_hygiene_phase2_governance_evidence_dry_run(
        tmp_path,
        out_root=tmp_path,
    )
    out_json = tmp_path / DRY_RUN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase2_governance_evidence_dry_run.run(
        repo_root=tmp_path,
        out_root=tmp_path,
    )

    assert second["dry_run_hash"] == packet["dry_run_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase2_governance_evidence_dry_run_markdown() -> None:
    packet = build_v2_hygiene_phase2_governance_evidence_dry_run(REPO_ROOT)
    markdown = render_v2_hygiene_phase2_governance_evidence_dry_run_markdown(
        packet
    )

    assert markdown[0] == "# v2.0 Hygiene Phase 2 Governance Evidence Dry Run"
    assert any("operator_identity_not_attested" in line for line in markdown)
    assert any("phase2_governance_control_disposition" in line for line in markdown)
