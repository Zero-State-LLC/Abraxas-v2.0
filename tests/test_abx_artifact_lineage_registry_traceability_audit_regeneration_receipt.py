from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_traceability_audit_regeneration_receipt import (
    RECEIPT_ID,
    build_abx_artifact_lineage_registry_traceability_audit_regeneration_receipt,
    write_abx_artifact_lineage_registry_traceability_audit_regeneration_receipt,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_abx_artifact_lineage_registry_traceability_audit_regeneration_receipt.py",
    "local_abx_artifact_lineage_traceability_audit_regeneration_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_artifact_lineage_registry_traceability_audit_regeneration_receipt.v1.schema.json"
)


def test_regeneration_receipt_is_deterministic() -> None:
    first = build_abx_artifact_lineage_registry_traceability_audit_regeneration_receipt(
        source_root=REPO_ROOT
    )
    second = build_abx_artifact_lineage_registry_traceability_audit_regeneration_receipt(
        source_root=REPO_ROOT
    )
    assert first["receipt_hash"] == second["receipt_hash"]
    assert first["artifact_id"] == RECEIPT_ID


def test_regeneration_receipt_emitted_when_scoped_receipt_ready() -> None:
    packet = build_abx_artifact_lineage_registry_traceability_audit_regeneration_receipt(
        source_root=REPO_ROOT
    )
    assert packet["status"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REGENERATION_RECEIPT_EMITTED"
    assert packet["audit_regeneration_performed"] is True
    assert packet["downstream_status"] == "TRACEABILITY_AUDIT_REGENERATION_COMPLETE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["observed_post_repair_findings"]["detect_artifacts_with_outputs_but_no_registry_entry"] == "PASS"


def test_writer_runner_and_schema(tmp_path: Path) -> None:
    packet = write_abx_artifact_lineage_registry_traceability_audit_regeneration_receipt(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["receipt_hash"] == packet["receipt_hash"]
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
