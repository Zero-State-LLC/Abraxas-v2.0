from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import write_canonical_json
from core.ingest.controlled_ingest_scheduler_governance_audit import (
    render_controlled_ingest_scheduler_governance_audit_markdown,
)
from core.ingest.controlled_ingest_scheduler_operator_review_record import (
    build_controlled_ingest_scheduler_operator_review_record,
    render_controlled_ingest_scheduler_operator_review_record_markdown,
    write_controlled_ingest_scheduler_operator_review_record,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_controlled_ingest_scheduler_operator_review_record.py",
    "local_controlled_ingest_scheduler_operator_review_record_runner",
)


def test_record_is_deterministic_and_accepts_review_only_audit() -> None:
    first = build_controlled_ingest_scheduler_operator_review_record()
    second = build_controlled_ingest_scheduler_operator_review_record()

    assert first["record_hash"] == second["record_hash"]
    assert first["status"] == "CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW_ACCEPTED"
    assert first["selected_decision"] == "APPROVE_OPERATOR_REVIEW"
    assert first["audit_accepted_as_reviewed_evidence"] is True
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_record_preserves_authority_locks() -> None:
    packet = build_controlled_ingest_scheduler_operator_review_record()

    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["scheduler_mutation_allowed"] is False
    assert packet["ingest_runner_mutation_allowed"] is False
    assert packet["pipeline_or_route_mutation_allowed"] is False
    assert packet["queue_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["forecast_weight_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    source_audit = json.loads(Path("out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json").read_text(encoding="utf-8"))
    audit_path = tmp_path / "out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(audit_path, source_audit)
    audit_path.with_suffix(".md").write_text(
        render_controlled_ingest_scheduler_governance_audit_markdown(source_audit),
        encoding="utf-8",
    )
    packet = write_controlled_ingest_scheduler_operator_review_record(tmp_path, out_root=tmp_path)
    json_path = tmp_path / "out/operator_review/controlled_ingest_scheduler_operator_review_record_001.latest.json"
    md_path = tmp_path / "out/operator_review/controlled_ingest_scheduler_operator_review_record_001.latest.md"

    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=tmp_path, out_root=tmp_path)
    assert runner_packet["record_hash"] == packet["record_hash"]

    schema = json.loads(
        Path("contracts/operator_review/controlled_ingest_scheduler_operator_review_record.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validate(packet, schema)
    markdown = render_controlled_ingest_scheduler_operator_review_record_markdown(packet)
    assert markdown[0] == "# Controlled Ingest Scheduler Operator Review Record"
    assert any("APPROVE_OPERATOR_REVIEW" in line for line in markdown)


def test_record_fails_closed_when_audit_is_not_clean(tmp_path: Path) -> None:
    audit_path = tmp_path / "out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(
        json.dumps(
            {
                "schema_version": "ControlledIngestSchedulerGovernanceAudit.v1",
                "final_status": "FAIL",
                "audit_posture": "FAILED",
                "recommended_next_step": "CONTROLLED_INGEST_SCHEDULER_BOUNDARY_REPAIR_REQUIRED",
                "finding_counts": {"FAIL": 1},
            }
        ),
        encoding="utf-8",
    )

    packet = build_controlled_ingest_scheduler_operator_review_record(tmp_path)

    assert packet["status"] == "CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW_BLOCKED"
    assert packet["selected_decision"] == "NOT_COMPUTABLE"
    assert packet["audit_accepted_as_reviewed_evidence"] is False


def test_registry_includes_review_record_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/operator_review/controlled_ingest_scheduler_operator_review_record_001.latest.json" in (
        _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert "out/operator_review/controlled_ingest_scheduler_operator_review_record_001.latest.md" in (
        _DERIVED_OPTIONAL_ARTIFACTS
    )
