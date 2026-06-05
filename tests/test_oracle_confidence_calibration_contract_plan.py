from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.oracle_confidence_calibration_contract_plan import (
    build_oracle_confidence_calibration_contract_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/oracle_confidence_calibration_contract_plan.v1.schema.json"


def _load_runner_module():
    runner_path = REPO_ROOT / "Scripts/run_oracle_confidence_calibration_contract_plan.py"
    spec = importlib.util.spec_from_file_location(
        "local_oracle_confidence_calibration_contract_plan_runner",
        runner_path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_plan_is_advisory_only_and_fail_closed() -> None:
    packet = build_oracle_confidence_calibration_contract_plan(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "OracleConfidenceCalibrationContractPlan.v1"
    assert packet["plan_status"] == "CONTRACT_PLAN_EMITTED_ADVISORY_ONLY"
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["safe_to_prepare_planning_pr"] is False
    assert packet["safe_to_prepare_implementation_pr"] is False
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["canon_mutation"] is False
    assert packet["runtime_mutation"] is False
    assert packet["queue_mutation"] is False
    assert packet["valid_for_execution"] is False


def test_contract_plan_captures_missing_contract_paths_and_specs() -> None:
    packet = build_oracle_confidence_calibration_contract_plan(repo_root=REPO_ROOT)

    assert packet["planned_contract_paths"] == [
        "contracts/oracle/oracle_confidence_calibration_profile.v1.schema.json",
        "contracts/oracle/oracle_confidence_calibration_bucket_set.v1.schema.json",
        "contracts/oracle/oracle_confidence_calibration_receipt.v1.schema.json",
    ]
    assert packet["missing_contract_paths"] == packet["planned_contract_paths"]
    assert [spec["contract_id"] for spec in packet["contract_specs"]] == [
        "ORACLE_CONFIDENCE_CALIBRATION_PROFILE",
        "ORACLE_CONFIDENCE_CALIBRATION_BUCKET_SET",
        "ORACLE_CONFIDENCE_CALIBRATION_RECEIPT",
    ]
    assert packet["operator_hold_active"] is True
    assert packet["calibration_plan_ready"] is True


def test_contract_plan_schema_and_hash_are_stable() -> None:
    first = build_oracle_confidence_calibration_contract_plan(repo_root=REPO_ROOT)
    second = build_oracle_confidence_calibration_contract_plan(repo_root=REPO_ROOT)

    assert first == second
    packet_without_hash = dict(first)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(first, schema)


def test_contract_plan_runner_writes_stable_outputs(tmp_path: Path) -> None:
    runner = _load_runner_module()
    out_json = tmp_path / "out/sync/oracle_confidence_calibration_contract_plan/latest.json"
    out_md = tmp_path / "out/sync/oracle_confidence_calibration_contract_plan/latest.md"

    first = runner.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = runner.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert out_json.read_text(encoding="utf-8") == first_json
    assert out_md.read_text(encoding="utf-8") == first_md


def test_registry_includes_contract_plan_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/sync/oracle_confidence_calibration_contract_plan/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/sync/oracle_confidence_calibration_contract_plan/latest.md" in _DERIVED_OPTIONAL_ARTIFACTS
