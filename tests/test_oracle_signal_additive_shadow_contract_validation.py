from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.oracle_signal_additive_shadow_contract_validation import (
    build_oracle_signal_additive_shadow_contract_validation,
    render_oracle_signal_additive_shadow_contract_validation_markdown,
    write_oracle_signal_additive_shadow_contract_validation,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_oracle_signal_additive_shadow_contract_validation.py",
    "local_oracle_signal_additive_shadow_contract_validation_runner",
)


def test_validation_is_deterministic_and_shadow_only() -> None:
    first = build_oracle_signal_additive_shadow_contract_validation()
    second = build_oracle_signal_additive_shadow_contract_validation()

    assert first["validation_id"] == second["validation_id"]
    assert first["status"] == "ORACLE_SIGNAL_ADDITIVE_SHADOW_CONTRACT_VALIDATION_READY"
    assert first["target_pipeline_id"] == "oracle_signal"
    assert first["validation_scope"] == "SCHEMA_AND_SHADOW_RECEIPT_ONLY"
    assert first["validation_ready"] is True
    assert first["implementation_authorized"] is False
    assert first["execution_authority"] is False
    assert first["valid_for_execution"] is False
    assert all(value is False for value in first["authority_locks"].values())


def test_validation_records_contract_and_runner_coverage() -> None:
    packet = build_oracle_signal_additive_shadow_contract_validation()

    assert packet["observed_contract_paths"] == [
        "contracts/oracle/oracle_candidate_signal_packet.v1.schema.json",
        "contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json",
        "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json",
    ]
    assert packet["missing_contract_paths"] == []
    assert packet["candidate_runner_path"] == "scripts/ingest/run_oracle_signal_intake_boundary.py"
    assert packet["candidate_runner_observed"] is True
    assert "CORE_ORACLE_SIGNAL_IMPLEMENTATION" in packet["blocked_actions"]


def test_schema_writer_runner_and_markdown_are_stable(tmp_path: Path) -> None:
    packet = write_oracle_signal_additive_shadow_contract_validation(out_root=tmp_path)
    json_path = tmp_path / "out/oracle/oracle_signal_additive_shadow_contract_validation.latest.json"
    md_path = tmp_path / "out/oracle/oracle_signal_additive_shadow_contract_validation.latest.md"
    schema = json.loads(
        Path("contracts/oracle/oracle_signal_additive_shadow_contract_validation.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )

    validate(packet, schema)
    assert json_path.exists()
    assert md_path.exists()
    first_json = json_path.read_text(encoding="utf-8")
    first_md = md_path.read_text(encoding="utf-8")
    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["validation_id"] == packet["validation_id"]
    assert json_path.read_text(encoding="utf-8") == first_json
    assert md_path.read_text(encoding="utf-8") == first_md

    markdown = render_oracle_signal_additive_shadow_contract_validation_markdown(packet)
    assert markdown[0] == "# Oracle Signal Additive Shadow Contract Validation"
    assert any("EXECUTION_AUTHORITY_GRANT" in line for line in markdown)


def test_generated_artifact_registry_includes_validation_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/oracle/oracle_signal_additive_shadow_contract_validation.latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/oracle/oracle_signal_additive_shadow_contract_validation.latest.md" in _DERIVED_OPTIONAL_ARTIFACTS
