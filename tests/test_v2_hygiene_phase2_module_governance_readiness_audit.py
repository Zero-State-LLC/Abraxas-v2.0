from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_phase2_module_governance_readiness_audit import (
    OUT_JSON,
    build_v2_hygiene_phase2_module_governance_readiness_audit,
    render_v2_hygiene_phase2_module_governance_readiness_audit_markdown,
    write_v2_hygiene_phase2_module_governance_readiness_audit,
)
from scripts.hygiene import run_v2_hygiene_phase2_module_governance_readiness_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/v2_hygiene_phase2_module_governance_readiness_audit.v1.schema.json"
)


def test_v2_hygiene_phase2_module_governance_readiness_audit_held() -> None:
    packet = build_v2_hygiene_phase2_module_governance_readiness_audit(REPO_ROOT)

    assert packet["status"] == (
        "V2_HYGIENE_PHASE2_MODULE_GOVERNANCE_READINESS_AUDIT_HELD_FOR_OPERATOR"
    )
    assert packet["source_ready"] is True
    assert packet["notion_phase2_source"]["title"] == (
        "Phase 2: Module Skeletons & Governance Hooks"
    )
    assert packet["governance_summary"]["expected_governance_control_count"] == 6
    assert packet["governance_summary"]["missing_control_count"] == 6
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_v2_hygiene_phase2_module_governance_controls_are_missing_and_held() -> None:
    packet = build_v2_hygiene_phase2_module_governance_readiness_audit(REPO_ROOT)
    records = {record["requirement_id"]: record for record in packet["governance_records"]}

    assert set(records) == {
        "default_advisory_mode",
        "no_output_mutation_without_configuration",
        "metadata_version_owner_posture",
        "hygiene_pipeline_interaction",
        "promotion_governance_review",
        "module_boundary_tests",
    }
    assert records["default_advisory_mode"]["repo_evidence_path"] == "abraxas/v2/modules"
    assert records["metadata_version_owner_posture"]["repo_evidence_path"] == (
        "abraxas/v2/modules/*/config.py"
    )
    assert records["promotion_governance_review"]["repo_evidence_path"] == (
        "docs/v2_hygiene/module_promotion_criteria.md"
    )
    assert all(record["repo_observed"] is False for record in records.values())
    assert all(
        record["readiness_status"] == "GOVERNANCE_CONTROL_REPO_MISSING_HELD"
        for record in records.values()
    )
    assert all(record["authority_granted"] is False for record in records.values())


def test_v2_hygiene_phase2_module_governance_readiness_audit_denies_authority() -> None:
    packet = build_v2_hygiene_phase2_module_governance_readiness_audit(REPO_ROOT)

    assert packet["operator_attestation_created"] is False
    assert packet["authorization_record_created"] is False
    assert packet["module_code_creation_authorized"] is False
    assert packet["module_test_creation_authorized"] is False
    assert packet["module_registration_authorized"] is False
    assert packet["hygiene_pipeline_integration_authorized"] is False
    assert packet["promotion_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["strict_mode_enablement_authorized"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["safe_to_prepare_patch"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_phase2_module_governance_readiness_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase2_module_governance_readiness_audit(REPO_ROOT)
    without_hash = dict(packet)
    audit_hash = without_hash.pop("audit_hash")
    assert audit_hash == canonical_hash(without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase2_module_governance_readiness_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase2_module_governance_readiness_audit(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / OUT_JSON
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase2_module_governance_readiness_audit.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["audit_hash"] == packet["audit_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase2_module_governance_readiness_markdown() -> None:
    packet = build_v2_hygiene_phase2_module_governance_readiness_audit(REPO_ROOT)
    markdown = render_v2_hygiene_phase2_module_governance_readiness_audit_markdown(
        packet,
    )

    assert markdown[0] == "# v2.0 Hygiene Phase 2 Module Governance Readiness Audit"
    assert any("default_advisory_mode" in line for line in markdown)
    assert any("missing_control_count" in line for line in markdown)
