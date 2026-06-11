from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt import (
    build_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt,
    render_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_markdown,
    write_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt,
)
from core.abx_artifact_lineage_registry_traceability_audit import (
    write_abx_artifact_lineage_registry_traceability_audit,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt.py",
    "local_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_runner",
)


def test_scoped_execution_receipt_is_deterministic_and_bounded() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt()
    second = build_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt()

    assert first["receipt_hash"] == second["receipt_hash"]
    assert first["status"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
    assert first["repair_execution_performed"] is True
    assert first["execution_authority"] is True
    assert first["execution_allowed"] is False
    assert first["valid_for_execution"] is False
    assert first["valid_for_repair"] is False
    assert first["runtime_mutation_allowed"] is False
    assert first["canon_mutation_allowed"] is False
    assert first["queue_mutation_allowed"] is False
    assert first["runner_casing_policy_override_allowed"] is False
    assert first["notion_completeness_claim_allowed"] is False
    assert first["registry_coverage_repair"]["repaired_count"] > 0
    assert first["output_pairing_repair"]["exception_count"] > 0
    assert first["docs_reference_repair"]["exception_count"] > 0


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt(REPO_ROOT, out_root=tmp_path)

    json_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["receipt_hash"] == packet["receipt_hash"]

    schema = json.loads(
        Path(
            "contracts/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_markdown(packet)
    assert markdown[0] == "# ABX Artifact Lineage Registry Direct Repair Scoped Execution Receipt"
    assert any("RUNNER_CASING_POLICY_OVERRIDE" in line for line in markdown)


def test_traceability_audit_consumes_scoped_receipt(tmp_path: Path) -> None:
    packet = write_abx_artifact_lineage_registry_traceability_audit(
        tmp_path / "out/sync/abx_artifact_lineage_registry_traceability_audit/latest.json",
        tmp_path / "out/sync/abx_artifact_lineage_registry_traceability_audit/latest.md",
    )

    assert packet["scoped_direct_repair_execution"]["receipt_observed"] is True
    registry_statuses = {finding["finding_id"]: finding["status"] for finding in packet["registry_findings"]}
    output_statuses = {finding["finding_id"]: finding["status"] for finding in packet["output_findings"]}
    docs_statuses = {finding["finding_id"]: finding["status"] for finding in packet["docs_findings"]}
    runner_statuses = {finding["finding_id"]: finding["status"] for finding in packet["runner_findings"]}
    notion_statuses = {finding["finding_id"]: finding["status"] for finding in packet["notion_mapping_findings"]}

    assert registry_statuses["detect_artifacts_with_outputs_but_no_registry_entry"] == "PASS"
    assert output_statuses["detect_markdown_outputs_without_json_pair"] == "PASS"
    assert docs_statuses["detect_docs_references_to_missing_artifacts"] == "PASS"
    assert runner_statuses["detect_uppercase_Scripts_runner_discovery_gaps"] == "NOT_COMPUTABLE"
    assert notion_statuses["detect_generated_outputs_with_no_notion_surface"] == "NOT_COMPUTABLE"


def test_registry_includes_scoped_receipt_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
