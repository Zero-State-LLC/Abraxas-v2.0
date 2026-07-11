from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.oracle_signal_research_intake_receipt import (
    build_oracle_signal_research_intake_receipt,
    render_oracle_signal_research_intake_receipt_markdown,
    write_oracle_signal_research_intake_receipt,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_oracle_signal_research_intake_receipt.py",
    "local_oracle_signal_research_intake_receipt_runner",
)


def test_receipt_is_deterministic_and_fail_closed() -> None:
    first = build_oracle_signal_research_intake_receipt()
    second = build_oracle_signal_research_intake_receipt()

    assert first["receipt_id"] == second["receipt_id"]
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["non_authoritative"] is True
    assert first["valid_for_execution"] is False
    assert first["downstream"] == "NOT_COMPUTABLE"
    assert first["recommended_next_plan_emitted"] is True


def test_receipt_contains_required_candidate_classifications() -> None:
    packet = build_oracle_signal_research_intake_receipt()
    statuses = {item["candidate_id"]: item["allowed_status"] for item in packet["candidate_mappings"]}

    assert statuses["ORACLE_VECTOR_HDC_ENCODING"] == "ADVISORY_CANDIDATE"
    assert statuses["ORACLE_VECTOR_DIMENSION_POLICY"] == "ADVISORY_CANDIDATE"
    assert statuses["ORACLE_SIGNAL_RECOVERY_LAYER"] == "SHADOW_CANDIDATE"
    assert statuses["ORACLE_SIGNAL_MARGIN_CLASSIFIER"] == "FORECAST_CANDIDATE"
    assert statuses["ORACLE_CONFIDENCE_CALIBRATION"] == "ADVISORY_IMPLEMENTATION_CANDIDATE"
    assert statuses["ORACLE_TRAJECTORY_CONFIDENCE"] == "RESEARCH_CANDIDATE"


def test_receipt_governance_locks_stay_false() -> None:
    packet = build_oracle_signal_research_intake_receipt()
    locks = packet["governance_locks"]

    assert locks["governance_status"] == "FROZEN"
    assert locks["canon_status"] == "ADVISORY_ONLY"
    assert locks["execution_authority"] is False
    assert locks["canon_mutation_allowed"] is False
    assert locks["runtime_mutation_allowed"] is False
    assert locks["research_candidates_canonized"] is False


def test_schema_and_markdown_render() -> None:
    packet = build_oracle_signal_research_intake_receipt()
    schema = json.loads(
        Path(
            "contracts/canon/oracle_signal_research_intake_receipt.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_oracle_signal_research_intake_receipt_markdown(packet)
    assert markdown[0] == "# Oracle Signal Research Intake Receipt"
    assert any("ORACLE_CONFIDENCE_CALIBRATION_PLAN_001" in line for line in markdown)


def test_writer_and_runner_emit_json_and_markdown(tmp_path: Path) -> None:
    packet = write_oracle_signal_research_intake_receipt(".", out_root=tmp_path)

    json_path = tmp_path / "out/sync/oracle_signal_research_intake_receipt/latest.json"
    md_path = tmp_path / "out/sync/oracle_signal_research_intake_receipt/latest.md"
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["receipt_id"] == packet["receipt_id"]


def test_not_computable_and_forbidden_actions_are_present() -> None:
    packet = build_oracle_signal_research_intake_receipt()

    assert any(item["item_id"] == "ORACLE_CONFIDENCE_CALIBRATION_PLAN_001" for item in packet["not_computable_items"])
    assert "promote_research_to_canon" in packet["forbidden_actions"]
    assert "authorize_runtime_execution" in packet["forbidden_actions"]
    assert "treat_calibrated_confidence_as_authorization" in packet["forbidden_actions"]
