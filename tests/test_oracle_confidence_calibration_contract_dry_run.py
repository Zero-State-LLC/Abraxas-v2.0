from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.oracle_confidence_calibration_contract_dry_run import (
    build_oracle_confidence_calibration_contract_dry_run,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/oracle_confidence_calibration_contract_dry_run.v1.schema.json"


def _load_runner_module():
    runner_path = (
        REPO_ROOT
        / "scripts/ingest/run_oracle_confidence_calibration_contract_dry_run.py"
    )
    spec = importlib.util.spec_from_file_location(
        "local_oracle_confidence_calibration_contract_dry_run_runner",
        runner_path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_dry_run_is_advisory_only_and_fail_closed() -> None:
    packet = build_oracle_confidence_calibration_contract_dry_run(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "OracleConfidenceCalibrationContractDryRun.v1"
    assert packet["dry_run_status"] == "ORACLE_CONFIDENCE_CALIBRATION_CONTRACT_DRY_RUN_READY"
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["safe_to_prepare_planning_pr"] is False
    assert packet["safe_to_prepare_implementation_pr"] is False
    assert packet["authoring_performed"] is False
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["canon_mutation"] is False
    assert packet["runtime_mutation"] is False
    assert packet["queue_mutation"] is False
    assert packet["valid_for_authoring"] is False
    assert packet["valid_for_execution"] is False


def test_contract_dry_run_simulates_missing_contract_bundle() -> None:
    packet = build_oracle_confidence_calibration_contract_dry_run(repo_root=REPO_ROOT)

    assert packet["missing_contract_paths"] == [
        "contracts/oracle/oracle_confidence_calibration_profile.v1.schema.json",
        "contracts/oracle/oracle_confidence_calibration_bucket_set.v1.schema.json",
        "contracts/oracle/oracle_confidence_calibration_receipt.v1.schema.json",
    ]
    assert packet["simulated_contract_count"] == 3
    assert [item["contract_id"] for item in packet["simulated_contract_bundle"]] == [
        "ORACLE_CONFIDENCE_CALIBRATION_PROFILE",
        "ORACLE_CONFIDENCE_CALIBRATION_BUCKET_SET",
        "ORACLE_CONFIDENCE_CALIBRATION_RECEIPT",
    ]
    assert all(item["simulated_only"] is True for item in packet["simulated_contract_bundle"])
    assert packet["contract_plan_ready"] is True
    assert packet["operator_hold_active"] is True


def test_contract_dry_run_schema_and_hash_are_stable() -> None:
    first = build_oracle_confidence_calibration_contract_dry_run(repo_root=REPO_ROOT)
    second = build_oracle_confidence_calibration_contract_dry_run(repo_root=REPO_ROOT)

    assert first == second
    packet_without_hash = dict(first)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(first, schema)


def test_contract_dry_run_runner_writes_stable_outputs(tmp_path: Path) -> None:
    runner = _load_runner_module()
    out_json = tmp_path / "out/sync/oracle_confidence_calibration_contract_dry_run/latest.json"
    out_md = tmp_path / "out/sync/oracle_confidence_calibration_contract_dry_run/latest.md"

    first = runner.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = runner.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert out_json.read_text(encoding="utf-8") == first_json
    assert out_md.read_text(encoding="utf-8") == first_md


def test_registry_includes_contract_dry_run_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/sync/oracle_confidence_calibration_contract_dry_run/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/sync/oracle_confidence_calibration_contract_dry_run/latest.md" in _DERIVED_OPTIONAL_ARTIFACTS
