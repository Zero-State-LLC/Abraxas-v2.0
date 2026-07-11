from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.oracle_confidence_calibration_plan import (
    build_oracle_confidence_calibration_plan,
    write_oracle_confidence_calibration_plan,
    write_oracle_confidence_calibration_plan_markdown,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/oracle_confidence_calibration_plan.v1.schema.json"


def _seed_repo(tmp_path: Path) -> Path:
    write_canonical_json(
        tmp_path / "out/sync/oracle_signal_research_intake_receipt/latest.json",
        {
            "schema_version": "OracleSignalResearchIntakeReceipt.v1",
            "downstream": "NOT_COMPUTABLE",
            "source_research_package": {
                "package_id": "ORACLE_SIGNAL_GLOBAL_INGEST_RESEARCH_SYNC_SEAL_2026_06_05",
                "package_status": "ASSIMILATED_ADVISORY_ONLY",
            },
            "candidate_mappings": [
                {
                    "candidate_id": "ORACLE_CONFIDENCE_CALIBRATION",
                    "allowed_status": "ADVISORY_IMPLEMENTATION_CANDIDATE",
                    "proposed_role": "calibrated confidence and uncertainty dimensions",
                    "provenance": "RESEARCH",
                    "supporting_research_item_ids": ["RESEARCH-UQ-CALIBRATION-001"],
                }
            ],
        },
    )
    write_canonical_json(
        tmp_path / "out/operator_review/global_ingest_operator_decision_request_001.latest.json",
        {
            "schema_version": "GlobalIngestOperatorDecisionRequest.v1",
            "target_pipeline_id": "oracle_signal",
            "recommended_decision": "HOLD",
            "implementation_authorized": False,
        },
    )
    return tmp_path


def test_plan_is_advisory_only_and_fail_closed(tmp_path: Path) -> None:
    packet = build_oracle_confidence_calibration_plan(repo_root=_seed_repo(tmp_path))

    assert packet["artifact_type"] == "OracleConfidenceCalibrationPlan.v1"
    assert packet["plan_id"] == "ORACLE_CONFIDENCE_CALIBRATION_PLAN_001"
    assert packet["plan_status"] == "PLAN_EMITTED_ADVISORY_ONLY"
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["implementation_patch_id"] == "PATCH-ABX-ORACLE-CONFIDENCE-CALIBRATION-001"
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["forecast_routing"] is False
    assert packet["canon_mutation"] is False
    assert packet["runtime_mutation"] is False
    assert packet["queue_mutation"] is False
    assert packet["valid_for_execution"] is False


def test_plan_requires_research_receipt_and_operator_hold(tmp_path: Path) -> None:
    packet = build_oracle_confidence_calibration_plan(repo_root=_seed_repo(tmp_path))

    assert packet["research_ready"] is True
    assert packet["operator_hold_active"] is True
    assert packet["candidate_mapping"]["candidate_id"] == "ORACLE_CONFIDENCE_CALIBRATION"
    assert packet["candidate_mapping"]["allowed_status"] == "ADVISORY_IMPLEMENTATION_CANDIDATE"


def test_plan_fails_closed_when_prerequisites_are_missing(tmp_path: Path) -> None:
    packet = build_oracle_confidence_calibration_plan(repo_root=tmp_path)

    assert packet["plan_status"] == "NOT_COMPUTABLE"
    assert "RESEARCH_RECEIPT_NOT_READY" in packet["not_computable_reasons"]
    assert "GLOBAL_INGEST_OPERATOR_HOLD_NOT_OBSERVED" in packet["not_computable_reasons"]


def test_schema_and_hash_are_stable(tmp_path: Path) -> None:
    packet = build_oracle_confidence_calibration_plan(repo_root=_seed_repo(tmp_path))
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_writer_and_runner_emit_stable_outputs(tmp_path: Path) -> None:
    repo_root = _seed_repo(tmp_path / "repo")
    out_json = tmp_path / "out/sync/oracle_confidence_calibration_plan/latest.json"
    out_md = tmp_path / "out/sync/oracle_confidence_calibration_plan/latest.md"

    packet = build_oracle_confidence_calibration_plan(repo_root=repo_root)
    write_oracle_confidence_calibration_plan(out_json, packet)
    write_oracle_confidence_calibration_plan_markdown(out_md, packet)
    assert out_json.exists()
    assert out_md.exists()

    runner = load_script_runner(
        REPO_ROOT,
        "scripts/run_oracle_confidence_calibration_plan.py",
        "local_oracle_confidence_calibration_plan_runner",
    )
    runner_packet = runner.run(repo_root=repo_root, out_json=out_json, out_md=out_md)
    assert runner_packet["packet_hash"] == packet["packet_hash"]


def test_registry_includes_plan_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/sync/oracle_confidence_calibration_plan/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/sync/oracle_confidence_calibration_plan/latest.md" in _DERIVED_OPTIONAL_ARTIFACTS
