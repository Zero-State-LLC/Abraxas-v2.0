from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.global_ingest_adapter_spine_implementation_spec import (
    build_global_ingest_adapter_spine_implementation_spec,
    render_global_ingest_adapter_spine_implementation_spec_markdown,
    write_global_ingest_adapter_spine_implementation_spec,
)
from core.global_ingest_operator_decision_record import write_global_ingest_operator_decision_record
from core.global_ingest_separate_implementation_spec_plan import (
    write_global_ingest_separate_implementation_spec_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_global_ingest_adapter_spine_implementation_spec.py",
    "local_global_ingest_adapter_spine_implementation_spec_runner",
)


def test_spec_is_deterministic_and_bound_to_approved_plan() -> None:
    first = build_global_ingest_adapter_spine_implementation_spec()
    second = build_global_ingest_adapter_spine_implementation_spec()

    assert first["spec_hash"] == second["spec_hash"]
    assert first["status"] == "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_CONSUMED_ADVISORY_ONLY"
    assert first["source_spec_plan_hash"]
    assert first["source_selected_decision"] == "APPROVE_SEPARATE_IMPLEMENTATION_SPEC"
    assert first["spec_authoring_allowed"] is True
    assert first["safe_to_prepare_implementation_pr"] is False
    assert first["implementation_pr_consumed"] is True
    assert first["additive_shadow_surfaces_observed"] is True
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_spec_preserves_authority_locks_and_blocks_runtime_mutation() -> None:
    packet = build_global_ingest_adapter_spine_implementation_spec()

    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["scheduler_mutation_allowed"] is False
    assert packet["pipeline_or_route_mutation_allowed"] is False
    assert packet["queue_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "CORE_ORACLE_SIGNAL_IMPLEMENTATION" in packet["blocked_actions"]


def test_spec_defines_additive_future_surfaces_without_creating_runtime_behavior() -> None:
    packet = build_global_ingest_adapter_spine_implementation_spec()

    assert packet["future_additive_contracts"] == [
        "contracts/oracle/oracle_candidate_signal_packet.v1.schema.json",
        "contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json",
        "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json",
    ]
    assert packet["missing_additive_contracts"] == []
    assert packet["observed_additive_contracts"] == packet["future_additive_contracts"]
    assert packet["future_candidate_runner"] == "scripts/ingest/run_oracle_signal_intake_boundary.py"
    assert packet["candidate_runner_observed"] is True
    assert packet["shadow_receipt_observed"] is True
    assert any("run_ingest_once.py behavior remains unchanged" in item for item in packet["preserved_surfaces"])
    assert any(section["status"] == "AUTHORITY_DENIED" for section in packet["spec_sections"])


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    write_global_ingest_operator_decision_record(".", out_root=tmp_path)
    write_global_ingest_separate_implementation_spec_plan(tmp_path, out_root=tmp_path)
    packet = write_global_ingest_adapter_spine_implementation_spec(tmp_path, out_root=tmp_path)

    json_path = tmp_path / "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json"
    md_path = tmp_path / "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.md"
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=tmp_path, out_root=tmp_path)
    assert runner_packet["spec_hash"] == packet["spec_hash"]

    schema = json.loads(
        Path("contracts/operator_review/global_ingest_adapter_spine_implementation_spec.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validate(packet, schema)
    markdown = render_global_ingest_adapter_spine_implementation_spec_markdown(packet)
    assert markdown[0] == "# Global Ingest Adapter Spine Implementation Spec"
    assert any("CORE_ORACLE_SIGNAL_IMPLEMENTATION" in line for line in markdown)


def test_spec_fails_closed_when_plan_is_not_ready(tmp_path: Path) -> None:
    plan_path = tmp_path / "out/operator_review/global_ingest_separate_implementation_spec_plan_001.latest.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(
        json.dumps(
            {
                "status": "GLOBAL_INGEST_SEPARATE_IMPLEMENTATION_SPEC_PLAN_BLOCKED",
                "spec_authoring_allowed": False,
                "implementation_authorized": False,
                "execution_authority": False,
            }
        ),
        encoding="utf-8",
    )

    packet = build_global_ingest_adapter_spine_implementation_spec(tmp_path)

    assert packet["status"] == "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_BLOCKED"
    assert packet["spec_authoring_allowed"] is False
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_registry_includes_implementation_spec_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json" in (
        _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.md" in (
        _DERIVED_OPTIONAL_ARTIFACTS
    )
