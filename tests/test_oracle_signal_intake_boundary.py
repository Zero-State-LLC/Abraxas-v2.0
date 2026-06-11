from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import validate

from core.oracle_signal_intake_boundary import (
    build_oracle_signal_intake_receipt,
    render_oracle_signal_intake_receipt_markdown,
    write_oracle_signal_intake_receipt,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_oracle_signal_intake_boundary.py",
    "local_oracle_signal_intake_boundary_runner",
)


def _schema(path: str) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_receipt_is_deterministic_and_shadow_only() -> None:
    first = build_oracle_signal_intake_receipt()
    second = build_oracle_signal_intake_receipt()

    assert first["receipt_hash"] == second["receipt_hash"]
    assert first["receipt_status"] == "ORACLE_SIGNAL_INTAKE_RECEIPT_EMITTED_ADVISORY_ONLY"
    assert first["authority"] == "SHADOW_INTAKE_BOUNDARY_ONLY"
    assert first["candidate_signal_count"] == len(first["candidate_signals"])
    assert first["input_envelope_ref_count"] == len(first["input_envelope_refs"])
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_receipt_denies_authority_and_runtime_mutation() -> None:
    packet = build_oracle_signal_intake_receipt()

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["forecast_authority"] is False
    assert packet["canon_mutation"] is False
    assert packet["runtime_mutation"] is False
    assert packet["scheduler_mutation"] is False
    assert packet["queue_mutation"] is False
    assert packet["pipeline_or_route_mutation"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "INGEST_RUNNER_BEHAVIOR_MUTATION" in packet["blocked_actions"]


def test_candidate_and_envelope_contracts_validate() -> None:
    packet = build_oracle_signal_intake_receipt()
    candidate_schema = _schema("contracts/oracle/oracle_candidate_signal_packet.v1.schema.json")
    envelope_schema = _schema("contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json")
    receipt_schema = _schema("contracts/oracle/oracle_signal_intake_receipt.v1.schema.json")

    validate(packet, receipt_schema)
    for candidate in packet["candidate_signals"]:
        validate(candidate, candidate_schema)
        assert candidate["payload_ref"] == "SOURCE_URI_ONLY_NO_FETCH"
        assert candidate["forecast_authority"] is False
    for envelope in packet["input_envelope_refs"]:
        validate(envelope, envelope_schema)
        assert envelope["envelope_status"] == "REFERENCE_ONLY_NOT_BOUND"


def test_writer_runner_and_markdown_are_stable(tmp_path: Path) -> None:
    packet = write_oracle_signal_intake_receipt(source_root=".", out_root=tmp_path)
    json_path = tmp_path / "out/oracle/oracle_signal_intake_receipt.latest.json"
    md_path = tmp_path / "out/oracle/oracle_signal_intake_receipt.latest.md"
    assert json_path.exists()
    assert md_path.exists()

    first_json = json_path.read_text(encoding="utf-8")
    first_md = md_path.read_text(encoding="utf-8")
    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["receipt_hash"] == packet["receipt_hash"]
    assert json_path.read_text(encoding="utf-8") == first_json
    assert md_path.read_text(encoding="utf-8") == first_md

    markdown = render_oracle_signal_intake_receipt_markdown(packet)
    assert markdown[0] == "# Oracle Signal Intake Receipt"
    assert any("CORE_ORACLE_SIGNAL_IMPLEMENTATION" in line for line in markdown)


def test_receipt_fails_closed_when_queue_authority_drifts(tmp_path: Path) -> None:
    queue = json.loads(Path("out/ingest/oracle_intake_queue_001.latest.json").read_text(encoding="utf-8"))
    queue["execution_authority"] = True
    queue_path = tmp_path / "queue.json"
    queue_path.write_text(json.dumps(queue), encoding="utf-8")

    with pytest.raises(ValueError, match="execution_authority=false"):
        build_oracle_signal_intake_receipt(queue_path=queue_path)


def test_registry_includes_oracle_signal_receipt_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/oracle/oracle_signal_intake_receipt.latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/oracle/oracle_signal_intake_receipt.latest.md" in _DERIVED_OPTIONAL_ARTIFACTS
